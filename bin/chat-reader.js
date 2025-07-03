#!/usr/bin/env node
import { Command } from 'commander';
import { generate } from '../src/generator';

const program = new Command();
program
  .requiredOption('-i, --input <file>', 'Path to conversations.json')
  .option('--import-hkg', 'Import conversation data into hKG')
  .option('--llm-model <model>', 'LLM model to use');

program.parse(process.argv);

const opts = program.opts();

generate({
  inputPath: opts.input,
  importHkg: opts.importHkg,
  llmModel: opts.llmModel
}).catch(err => {
  console.error(err);
  process.exit(1);
});
