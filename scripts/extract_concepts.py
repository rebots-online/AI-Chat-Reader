#!/usr/bin/env python3
# Copyright (C) 2025 Robin L. M. Cheung, MBA. All rights reserved.
import json
import sys
import argparse

try:
    import ollama
except ImportError:
    ollama = None

try:
    import lmstudio
except ImportError:
    lmstudio = None

PROMPT_TEMPLATE = (
    "You are an information extraction agent. "
    "Given the following text, identify the main concepts as a list of strings "
    "and any directed relationships between them as triples [source, relation, target]. "
    "Respond in JSON with keys 'concepts' and 'relations'.\nText:\n{text}"
)


def run_model(text: str, model: str):
    if ollama:
        response = ollama.chat(model=model, messages=[{"role": "user", "content": PROMPT_TEMPLATE.format(text=text)}])
        return response["message"]["content"]
    elif lmstudio:
        client = lmstudio.Client()
        result = client.prompt(model, PROMPT_TEMPLATE.format(text=text))
        return result["choices"][0]["text"]
    else:
        raise RuntimeError("No LLM backend available. Install ollama or lmstudio.")


def main():
    parser = argparse.ArgumentParser(description="Extract concepts using a local LLM")
    parser.add_argument("--model", default="deepseek-r1_0528")
    parser.add_argument("text")
    args = parser.parse_args()

    raw = run_model(args.text, args.model)
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = {"concepts": [], "relations": []}
    print(json.dumps(data))


if __name__ == "__main__":
    main()
