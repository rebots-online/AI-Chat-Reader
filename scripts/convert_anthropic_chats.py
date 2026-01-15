# Copyright (C) 2025 Robin L. M. Cheung, MBA. All rights reserved.
import json
import os
from datetime import datetime

# Define paths with proper expansion of '~'
input_file = os.path.expanduser("./data/raw/claude_conversations.json")
output_folder = os.path.expanduser("./data/processed/")
output_file = os.path.join(output_folder, "formatted_claude_conversations.md")

# Ensure the output directory exists
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Load the JSON file
with open(input_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Prepare a list to hold all formatted conversations
formatted_output = []

for conversation in data:
    # Extract title and format as heading
    title = conversation.get('name', 'Untitled Conversation')
    formatted_output.append(f"# {title}\n")
    
    # Extract creation date
    created_at = conversation.get('created_at', '')
    if created_at:
        try:
            # Convert ISO format date string to datetime object and format it
            date_obj = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            date_str = date_obj.strftime('%Y-%m-%d %H:%M:%S')
            formatted_output.append(f"**Date:** {date_str}\n")
        except (ValueError, TypeError):
            pass  # Skip if date conversion fails
    
    # Process messages in the conversation
    messages = conversation.get('chat_messages', [])
    
    if messages:
        for message in messages:
            # Get sender role (human/assistant)
            sender = message.get('sender', 'unknown')
            if sender == 'human':
                role_display = 'User'
            elif sender == 'assistant':
                role_display = 'Claude'
            else:
                role_display = sender.capitalize()
            
            # Get message text
            text = message.get('text', '').strip()
            
            # Skip empty messages
            if not text:
                continue
                
            # Format and add message to output
            formatted_output.append(f"**{role_display}:** {text}\n\n")
    
    # Add a separator between conversations
    formatted_output.append("\n---\n\n")

# Write the formatted conversations to the output file
with open(output_file, 'w', encoding='utf-8') as f:
    f.write("".join(formatted_output))

print(f"✅ Successfully converted Claude conversations to Markdown: {output_file}")