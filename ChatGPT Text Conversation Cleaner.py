import json
import os
import sys
from tkinter import filedialog
import tkinter as tk

def select_file():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    file_path = filedialog.askopenfilename(
        title="Select Chat Log File",
        filetypes=[
            ("JSON files", "*.json"),
            ("All files", "*.*")
        ]
    )
    return file_path

def clean_message(message):
    cleaned = {}
    
    # Get the actual message content from the nested structure
    message_data = message.get('message', {})
    if not message_data:
        return cleaned
        
    content = message_data.get('content', {})
    if not content:
        return cleaned
        
    parts = content.get('parts', [])
    if not parts:
        return cleaned
    
    # Handle different content types
    cleaned_parts = []
    for part in parts:
        if isinstance(part, str):
            cleaned_part = part.strip()
            if cleaned_part:
                cleaned_parts.append(cleaned_part)
        elif isinstance(part, dict):
            if 'text' in part:
                cleaned_part = part['text'].strip()
                if cleaned_part:
                    cleaned_parts.append(cleaned_part)
    
    cleaned_content = " ".join(cleaned_parts)
    
    if cleaned_content:
        cleaned["content"] = cleaned_content
        cleaned["author_role"] = message_data.get('author', {}).get('role')
        cleaned["create_time"] = message_data.get('create_time')
    
    return cleaned

def process_large_json(file_path):
    if not file_path:
        print("No file selected. Exiting...")
        return
        
    print(f"Starting to process {file_path}...")
    
    # Open the large JSON file and iterate over the data
    print("Reading JSON file...")
    with open(file_path, 'r', encoding='utf-8') as f:
        conversations = json.load(f)
        
        # Clean the messages from all conversations
        print("Cleaning messages...")
        cleaned_data = []
        total_messages = 0
        skipped_messages = 0
        
        for conversation in conversations:
            # Get messages from the mapping structure
            mapping = conversation.get('mapping', {})
            messages = list(mapping.values())
            total_messages += len(messages)
            
            for message in messages:
                cleaned_message = clean_message(message)
                if cleaned_message:  # Only add messages with content
                    cleaned_data.append(cleaned_message)
                else:
                    skipped_messages += 1
                
                if (len(cleaned_data) + 1) % 1000 == 0:  # Progress update every 1000 messages
                    print(f"Processed {len(cleaned_data)} messages...")
        
        print(f"\nSummary:")
        print(f"Found {total_messages} total messages across {len(conversations)} conversations")
        print(f"Successfully cleaned {len(cleaned_data)} messages")
        print(f"Skipped {skipped_messages} messages")
        print(f"Success rate: {(len(cleaned_data)/total_messages)*100:.2f}%")

        # Save cleaned data to a new JSON file
        output_file = 'cleaned_' + os.path.basename(file_path)
        print(f"\nSaving cleaned data to {output_file}...")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(cleaned_data, f, indent=2, ensure_ascii=False)
        print("Finished! Cleaned data has been saved.")

def clean_conversation(input_file, output_file):
    # Read the input JSON file
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Clean each message by removing unnecessary fields
    cleaned_data = []
    for message in data:
        cleaned_message = {
            'content': message['content'],
            'author_role': message['author_role'],
            'create_time': message['create_time']
        }
        cleaned_data.append(cleaned_message)

    # Write the cleaned data to a new JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(cleaned_data, f, indent=2, ensure_ascii=False)

    print(f"Cleaned data saved to {output_file}")

if __name__ == "__main__":
    # Get file path from command line argument, or use file dialog
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        print("Please select your chat log file...")
        file_path = select_file()
    
    process_large_json(file_path)
