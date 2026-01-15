#!/usr/bin/env python3
# Copyright (C) 2025 Robin L. M. Cheung, MBA. All rights reserved.
"""Incrementally process new OpenAI conversations without rebuilding existing output."""
import os
import json
import argparse
from pathlib import Path

from parsers.openai_parser import OpenAIParser
from generators.html_generator import HTMLGenerator
from generators.index_generator import IndexGenerator
from generators.asset_manager import AssetManager

STATE_DIR = Path('data/html/incremental')
PROCESSED_IDS_FILE = STATE_DIR / 'processed_ids.json'
METADATA_FILE = STATE_DIR / 'metadata.json'
TEMPLATES_DIR = Path('scripts/templates')
ASSETS_DIR = Path('scripts/assets')


def load_processed_ids() -> set:
    if PROCESSED_IDS_FILE.exists():
        with open(PROCESSED_IDS_FILE, 'r', encoding='utf-8') as f:
            return set(json.load(f))
    return set()


def save_processed_ids(ids: set) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    with open(PROCESSED_IDS_FILE, 'w', encoding='utf-8') as f:
        json.dump(sorted(ids), f, indent=2)


def load_metadata() -> list:
    if METADATA_FILE.exists():
        with open(METADATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def save_metadata(metadata: list) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    with open(METADATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, default=str)


def main() -> None:
    parser = argparse.ArgumentParser(description="Process only new OpenAI conversations and update HTML output.")
    parser.add_argument('--input', default='data/raw/openai_conversations.json', help='Path to OpenAI export file')
    args = parser.parse_args()

    openai_parser = OpenAIParser()
    html_gen = HTMLGenerator(str(TEMPLATES_DIR), str(ASSETS_DIR))
    index_gen = IndexGenerator(str(TEMPLATES_DIR))
    asset_mgr = AssetManager(str(ASSETS_DIR))

    conversations = openai_parser.parse_file(args.input)
    if not conversations:
        print('No conversations found in input file.')
        return

    processed_ids = load_processed_ids()
    metadata = load_metadata()

    new_conversations = [c for c in conversations if c.id not in processed_ids]
    if not new_conversations:
        print('No new conversations to process.')
        return

    conversations_dir = STATE_DIR / 'openai'
    conversations_dir.mkdir(parents=True, exist_ok=True)

    new_metadata = html_gen.generate_conversations_batch(
        conversations=new_conversations,
        output_dir=str(STATE_DIR),
        source_subdir='openai',
        assets_relative_path='../../assets',
        index_relative_path='../../index.html',
        source_index_relative_path='../index.html'
    )

    metadata.extend(new_metadata)

    index_gen.generate_source_index(
        conversations=metadata,
        source_name='openai',
        output_path=str(STATE_DIR / 'openai' / 'index.html'),
        assets_relative_path='../assets',
        main_index_path='../index.html'
    )
    index_gen.generate_main_index(
        all_conversations=metadata,
        output_path=str(STATE_DIR / 'index.html'),
        assets_relative_path='assets'
    )

    assets_output_dir = STATE_DIR / 'assets'
    if not assets_output_dir.exists():
        asset_mgr.setup_complete_assets(str(assets_output_dir), site_name='Chat Archive')

    processed_ids.update(c.id for c in new_conversations)
    save_processed_ids(processed_ids)
    save_metadata(metadata)

    print(f'Processed {len(new_conversations)} new conversations.')


if __name__ == '__main__':
    main()
