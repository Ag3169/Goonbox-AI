"""Message bookmarking and favorites system."""

from typing import List, Dict


class MessageBookmark:
    """Manage bookmarked messages."""
    
    @staticmethod
    def bookmark_message(chat: dict, message_index: int, note: str = "") -> bool:
        """
        Bookmark a message for later reference.
        
        Args:
            chat: Chat dictionary
            message_index: Index of message to bookmark
            note: Optional user note about the bookmark
            
        Returns:
            bool: True if successful
        """
        if "bookmarks" not in chat:
            chat["bookmarks"] = {}
        
        messages = chat.get("messages", [])
        if message_index < 0 or message_index >= len(messages):
            return False
        
        message = messages[message_index]
        bookmark_id = f"bookmark_{message_index}_{len(chat['bookmarks'])}"
        
        chat["bookmarks"][bookmark_id] = {
            "message_index": message_index,
            "content_preview": str(message.get("content", ""))[:100],
            "role": message.get("role", "unknown"),
            "user_note": note,
            "timestamp": None,  # Can be added later
        }
        
        return True
    
    @staticmethod
    def unbookmark_message(chat: dict, bookmark_id: str) -> bool:
        """Remove a bookmark."""
        if "bookmarks" not in chat:
            return False
        
        if bookmark_id in chat["bookmarks"]:
            del chat["bookmarks"][bookmark_id]
            return True
        
        return False
    
    @staticmethod
    def get_bookmarks(chat: dict) -> Dict:
        """Get all bookmarks in a chat."""
        return chat.get("bookmarks", {})
    
    @staticmethod
    def is_bookmarked(chat: dict, message_index: int) -> bool:
        """Check if a message is bookmarked."""
        bookmarks = chat.get("bookmarks", {})
        for bookmark_id, bookmark in bookmarks.items():
            if bookmark.get("message_index") == message_index:
                return True
        return False
    
    @staticmethod
    def export_bookmarks(chat: dict) -> str:
        """Export bookmarks as formatted text."""
        bookmarks = chat.get("bookmarks", {})
        if not bookmarks:
            return "No bookmarks in this chat."
        
        lines = [f"# Bookmarks for {chat.get('title', 'Chat')}\n"]
        
        for bookmark_id, bookmark in bookmarks.items():
            lines.append(f"## Bookmark: {bookmark_id}")
            lines.append(f"**Role**: {bookmark['role']}")
            lines.append(f"**Preview**: {bookmark['content_preview']}")
            if bookmark['user_note']:
                lines.append(f"**Note**: {bookmark['user_note']}")
            lines.append("")
        
        return "\n".join(lines)
