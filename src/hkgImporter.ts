import fs from 'fs';
import neo4j from 'neo4j-driver';
import { extractConcepts } from './llm/deepseekClient';

export interface ThreadedMessage {
  uuid: string;
  text: string;
  timestamp: number;
  concepts?: string[];
  relations?: [string, string, string][];
}

/**
 * Import threaded chat messages into the hKG Neo4j graph.
 * Only messages newer than the stored `lastImportedTs` will be processed.
 * A `hkg-delta.json` file is written with the processed messages for later
 * ingestion into Qdrant for embeddings.
 */
export async function importToHkg(messages: ThreadedMessage[]) {
  const driver = neo4j.driver(
    process.env.NEO4J_URI || 'bolt://localhost:7687',
    neo4j.auth.basic(
      process.env.NEO4J_USER || 'neo4j',
      process.env.NEO4J_PASSWORD || 'neo4j'
    )
  );
  const session = driver.session();

  // Load last imported timestamp from a Meta node
  const metaRes = await session.run(
    'MERGE (m:Meta {id: 1}) ON CREATE SET m.lastImportedTs = 0 RETURN m.lastImportedTs AS ts'
  );
  let lastImported = metaRes.records[0].get('ts') as number;

  const delta: any[] = [];

  for (const msg of messages) {
    if (msg.timestamp <= lastImported) continue;

    // Ensure concepts/relations are populated
    if (!msg.concepts || !msg.relations) {
      const { concepts, relations } = await extractConcepts(msg.text);
      msg.concepts = concepts;
      msg.relations = relations;
    }

    delta.push({
      uuid: msg.uuid,
      text: msg.text,
      timestamp: msg.timestamp,
      concepts: msg.concepts,
      relations: msg.relations
    });

    // Scaffolding cypher statements
    await session.run(
      'MERGE (c:ChatMessage {uuid: $uuid}) SET c.text = $text, c.timestamp = $timestamp',
      { uuid: msg.uuid, text: msg.text, timestamp: msg.timestamp }
    );

    for (const concept of msg.concepts || []) {
      await session.run(
        'MERGE (k:Concept {name: $name})',
        { name: concept }
      );
      await session.run(
        'MATCH (c:ChatMessage {uuid: $uuid}), (k:Concept {name: $name}) MERGE (c)-[:MENTIONS]->(k)',
        { uuid: msg.uuid, name: concept }
      );
    }

    for (const [a, rel, b] of msg.relations || []) {
      await session.run(
        'MERGE (ka:Concept {name: $a}) MERGE (kb:Concept {name: $b}) MERGE (ka)-[:RELATES {type: $rel}]->(kb)',
        { a, b, rel }
      );
    }
  }

  if (delta.length) {
    const newest = Math.max(...delta.map(d => d.timestamp));
    await session.run(
      'MERGE (m:Meta {id: 1}) SET m.lastImportedTs = $ts',
      { ts: newest }
    );
  }

  await session.close();
  await driver.close();

  fs.writeFileSync('hkg-delta.json', JSON.stringify(delta, null, 2));
}
