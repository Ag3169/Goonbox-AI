"""Chat statistics and metadata."""

from datetime import datetime
from typing import Dict, List


class ChatStatistics:
    """Calculate statistics for chats."""
    
    @staticmethod
    def get_chat_stats(chat: dict) -> Dict:
        """
        Get statistics for a single chat.
        
        Args:
            chat: Chat dictionary
            
        Returns:
            Dictionary with statistics
        """
        messages = chat.get("messages", [])
        
        total_messages = len(messages)
        user_messages = sum(1 for m in messages if isinstance(m, dict) and m.get("role") == "user")
        assistant_messages = sum(1 for m in messages if isinstance(m, dict) and m.get("role") == "assistant")
        
        # Calculate total characters
        total_chars = sum(
            len(str(m.get("content", "")))
            for m in messages
            if isinstance(m, dict)
        )
        
        # Average message length
        avg_length = total_chars / total_messages if total_messages > 0 else 0
        
        # Get longest message
        longest_msg = max(
            (len(str(m.get("content", ""))) for m in messages if isinstance(m, dict)),
            default=0
        )
        
        return {
            "total_messages": total_messages,
            "user_messages": user_messages,
            "assistant_messages": assistant_messages,
            "total_characters": total_chars,
            "average_message_length": int(avg_length),
            "longest_message": longest_msg,
            "title": chat.get("title", "Unknown"),
        }
    
    @staticmethod
    def get_all_chats_stats(chats: list) -> Dict:
        """
        Get aggregated statistics for all chats.
        
        Args:
            chats: List of chat dictionaries
            
        Returns:
            Dictionary with overall statistics
        """
        total_chats = len(chats)
        total_messages = 0
        total_chars = 0
        
        for chat in chats:
            messages = chat.get("messages", [])
            total_messages += len(messages)
            total_chars += sum(
                len(str(m.get("content", "")))
                for m in messages
                if isinstance(m, dict)
            )
        
        return {
            "total_chats": total_chats,
            "total_messages": total_messages,
            "total_characters": total_chars,
            "average_messages_per_chat": int(total_messages / total_chats) if total_chats > 0 else 0,
            "average_chars_per_message": int(total_chars / total_messages) if total_messages > 0 else 0,
        }
    
    @staticmethod
    def get_chat_size_mb(chat: dict) -> float:
        """
        Get approximate size of chat in MB.
        
        Args:
            chat: Chat dictionary
            
        Returns:
            Size in MB
        """
        # Rough estimate: convert to JSON and estimate size
        import json
        try:
            json_str = json.dumps(chat)
            size_bytes = len(json_str.encode('utf-8'))
            return round(size_bytes / (1024 * 1024), 3)
        except:
            return 0.0
    
    @staticmethod
    def format_stats_display(stats: Dict) -> str:
        """
        Format statistics for display.
        
        Args:
            stats: Statistics dictionary
            
        Returns:
            Formatted string for display
        """
        lines = []
        
        for key, value in stats.items():
            # Convert key to readable format
            readable_key = key.replace("_", " ").title()
            
            # Format value
            if isinstance(value, int):
                formatted_value = f"{value:,}"
            elif isinstance(value, float):
                formatted_value = f"{value:.2f}"
            else:
                formatted_value = str(value)
            
            lines.append(f"{readable_key}: {formatted_value}")
        
        return "\n".join(lines)
