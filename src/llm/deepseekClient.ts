import { spawn } from 'child_process';
import path from 'path';

export interface ExtractResult {
  concepts: string[];
  relations: [string, string, string][];
}

/**
 * Extract high-level concepts and relations from a text chunk using a local LLM.
 * Defaults to the `deepseek-r1_0528` model but can be overridden via the
 * `model` parameter or `LLM_MODEL` environment variable.
 */
export async function extractConcepts(text: string, model?: string): Promise<ExtractResult> {
  const selectedModel = model || process.env.LLM_MODEL || 'deepseek-r1_0528';

  const script = path.join(__dirname, '../../scripts/extract_concepts.py');

  return new Promise((resolve, reject) => {
    const proc = spawn('python3', [script, '--model', selectedModel, text]);
    let stdout = '';
    let stderr = '';

    proc.stdout.on('data', (d) => (stdout += d.toString()));
    proc.stderr.on('data', (d) => (stderr += d.toString()));

    proc.on('close', () => {
      if (stderr.trim()) {
        reject(new Error(stderr.trim()));
        return;
      }
      try {
        const parsed = JSON.parse(stdout);
        resolve({
          concepts: parsed.concepts || [],
          relations: parsed.relations || []
        });
      } catch {
        resolve({ concepts: [], relations: [] });
      }
    });
  });
}
