import fs from 'fs';
import path from 'path';
import { extractConcepts } from './llm/deepseekClient';
import { importToHkg, ThreadedMessage } from './hkgImporter';

export interface GeneratorOptions {
  inputPath: string;
  importHkg?: boolean;
  llmModel?: string;
}

interface RawMessage {
  id: string;
  text: string;
  timestamp: number;
  role: string;
}

function threadMessages(data: RawMessage[]): ThreadedMessage[] {
  // In this simple scaffold we assume messages are already threaded
  return data.map((m) => ({
    uuid: m.id,
    text: m.text,
    timestamp: m.timestamp
  }));
}

export async function generate(opts: GeneratorOptions) {
  const raw = JSON.parse(fs.readFileSync(opts.inputPath, 'utf8')) as RawMessage[];
  const messages = threadMessages(raw);

  for (const msg of messages) {
    const { concepts, relations } = await extractConcepts(msg.text, opts.llmModel);
    msg.concepts = concepts;
    msg.relations = relations;
  }

  if (opts.importHkg) {
    await importToHkg(messages);
  }

  // HTML generation would happen here using existing templates
  const outDir = path.join(path.dirname(opts.inputPath), 'html');
  fs.mkdirSync(outDir, { recursive: true });
  fs.writeFileSync(path.join(outDir, 'index.html'), '<html><body>Placeholder</body></html>');
}
