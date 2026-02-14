"""Export chat conversations to various formats."""

import json
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime
from pathlib import Path


def export_chat_to_markdown(chat: dict, filepath: Path) -> bool:
    """Export a chat to markdown format."""
    try:
        title = chat.get("title", "Chat Export")
        messages = chat.get("messages", [])
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# {title}\n\n")
            f.write(f"**Exported**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            
            for i, msg in enumerate(messages, 1):
                if not isinstance(msg, dict):
                    continue
                
                role = str(msg.get("role", "unknown")).upper()
                content = str(msg.get("content", ""))
                
                if role == "USER":
                    f.write(f"## **User** (Message {i})\n\n")
                elif role == "ASSISTANT":
                    f.write(f"## **Assistant** (Message {i})\n\n")
                else:
                    f.write(f"## **{role}** (Message {i})\n\n")
                
                f.write(f"{content}\n\n")
                f.write("---\n\n")
        
        return True
    except Exception as e:
        print(f"Error exporting to markdown: {e}")
        return False


def export_chat_to_json(chat: dict, filepath: Path) -> bool:
    """Export a chat to JSON format."""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(chat, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error exporting to JSON: {e}")
        return False


def export_chat_to_txt(chat: dict, filepath: Path) -> bool:
    """Export a chat to plain text format."""
    try:
        title = chat.get("title", "Chat Export")
        messages = chat.get("messages", [])
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"{title}\n")
            f.write(f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
            
            for msg in messages:
                if not isinstance(msg, dict):
                    continue
                
                role = str(msg.get("role", "unknown")).upper()
                content = str(msg.get("content", ""))
                
                f.write(f"{role}:\n{content}\n\n")
        
        return True
    except Exception as e:
        print(f"Error exporting to text: {e}")
        return False
