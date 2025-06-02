import json
import os
from datetime import datetime

# Define paths with proper expansion of '~'
input_file = os.path.expanduser("./data/raw/openai_conversations.json")
output_folder = os.path.expanduser("./data/processed/")
output_file = os.path.join(output_folder, "formatted_openai_conversations.md")

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
    title = conversation.get('title', 'Untitled Conversation')
    formatted_output.append(f"# {title}\n")
    
    # Extract creation date if available
    create_time = conversation.get('create_time')
    if create_time:
        try:
            # Convert timestamp to readable date
            date_str = datetime.fromtimestamp(create_time).strftime('%Y-%m-%d %H:%M:%S')
            formatted_output.append(f"**Date:** {date_str}\n")
        except (ValueError, TypeError):
            pass  # Skip if timestamp conversion fails
    
    # Process messages in the conversation
    mapping = conversation.get('mapping', {})
    
    if mapping:
        # Extract messages and sort by creation time to ensure correct order
        messages = []
        for node_id, node in mapping.items():
            # Skip null nodes or nodes without messages
            if not node or node.get("message") is None:
                continue
                
            message = node.get("message", {})
            
            # Get creation time (may be null in some messages)
            create_time = message.get("create_time", 0)
            if create_time is None:
                create_time = 0
            
            # Extract author information and role
            author = message.get("author", {}) or {}
            role = author.get("role", "unknown")
            
            # Handle content extraction
            content_obj = message.get("content", {}) or {}
            content_type = content_obj.get("content_type", "text")
            
            # Skip system messages that are marked as hidden
            is_hidden = message.get("metadata", {}).get("is_visually_hidden_from_conversation", False)
            if is_hidden:
                continue
                
            # Handle different content types
            if content_type == "text":
                content_parts = content_obj.get("parts", []) or []
            elif content_type == "user_editable_context":
                # For user instructions or profile information
                user_instructions = content_obj.get("user_instructions", "")
                user_profile = content_obj.get("user_profile", "")
                content_parts = [f"{user_profile}\n{user_instructions}"] if user_profile or user_instructions else []
            else:
                # Handle other content types
                content_parts = content_obj.get("parts", []) or []
            
            # Process content parts
            processed_parts = []
            for part in content_parts:
                if part:  # Skip empty parts
                    if isinstance(part, str):
                        processed_parts.append(part)
                    elif isinstance(part, dict):
                        # Handle dictionary content types
                        if part.get('type') == 'text':
                            if 'text' in part:
                                processed_parts.append(part['text'])
                        else:
                            # For other dict types, use a reasonable representation
                            processed_parts.append(f"[Content: {str(part)}]")
                    else:
                        # For any other type, convert to string
                        processed_parts.append(str(part))
            
            content = "\n".join(processed_parts).strip()
            
            if content:  # Only add messages with actual content
                messages.append({
                    "create_time": create_time,
                    "role": role,
                    "content": content
                })
        
        # Sort messages by creation time
        messages.sort(key=lambda x: x["create_time"])
        
        # Format and add each message to output
        for message in messages:
            # Convert role to display format
            role = message["role"]
            if role == "assistant":
                role_display = "Assistant"
            elif role == "user":
                role_display = "User"
            elif role == "system":
                role_display = "System"
            elif role == "tool":
                role_display = "Tool"
            else:
                role_display = role.capitalize()
                
            content = message["content"]
            
            formatted_output.append(f"**{role_display}:** {content}\n\n")
    
    # Add a separator between conversations
    formatted_output.append("\n---\n\n")

# Write the formatted conversations to the output file
with open(output_file, 'w', encoding='utf-8') as f:
    f.write("".join(formatted_output))

print(f"✅ Successfully converted OpenAI conversations to Markdown: {output_file}")


