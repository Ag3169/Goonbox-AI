"""Conversation tagging and categorization system."""

from typing import List, Dict, Set


class ConversationTagger:
    """Tag and categorize conversations."""
    
    DEFAULT_TAGS = {
        "urgent": {"color": "red", "emoji": "🔴"},
        "important": {"color": "orange", "emoji": "⭐"},
        "solved": {"color": "green", "emoji": "✓"},
        "blocked": {"color": "red", "emoji": "🚫"},
        "review": {"color": "yellow", "emoji": "👀"},
        "documentation": {"color": "blue", "emoji": "📚"},
        "bug": {"color": "red", "emoji": "🐛"},
        "feature": {"color": "green", "emoji": "✨"},
        "question": {"color": "blue", "emoji": "❓"},
        "discussion": {"color": "purple", "emoji": "💬"},
    }
    
    @staticmethod
    def add_tag(chat: dict, tag: str) -> bool:
        """Add a tag to a chat."""
        if "tags" not in chat:
            chat["tags"] = []
        
        if tag not in chat["tags"]:
            chat["tags"].append(tag)
            return True
        
        return False
    
    @staticmethod
    def remove_tag(chat: dict, tag: str) -> bool:
        """Remove a tag from a chat."""
        if "tags" in chat and tag in chat["tags"]:
            chat["tags"].remove(tag)
            return True
        
        return False
    
    @staticmethod
    def get_tags(chat: dict) -> List[str]:
        """Get all tags for a chat."""
        return chat.get("tags", [])
    
    @staticmethod
    def has_tag(chat: dict, tag: str) -> bool:
        """Check if chat has a tag."""
        return tag in chat.get("tags", [])
    
    @staticmethod
    def set_category(chat: dict, category: str) -> bool:
        """Set primary category for a chat."""
        valid_categories = ["Development", "Learning", "Bug Fix", "Discussion", "Documentation"]
        
        if category in valid_categories:
            chat["category"] = category
            return True
        
        return False
    
    @staticmethod
    def get_category(chat: dict) -> str:
        """Get category for a chat."""
        return chat.get("category", "Uncategorized")
    
    @staticmethod
    def filter_by_tag(chats: List[Dict], tag: str) -> List[Dict]:
        """Filter chats by tag."""
        return [c for c in chats if ConversationTagger.has_tag(c, tag)]
    
    @staticmethod
    def filter_by_category(chats: List[Dict], category: str) -> List[Dict]:
        """Filter chats by category."""
        return [c for c in chats if ConversationTagger.get_category(c) == category]
    
    @staticmethod
    def get_all_tags_in_library(chats: List[Dict]) -> Set[str]:
        """Get all tags used across all chats."""
        all_tags = set()
        for chat in chats:
            all_tags.update(chat.get("tags", []))
        return all_tags
    
    @staticmethod
    def get_tag_statistics(chats: List[Dict]) -> Dict[str, int]:
        """Get usage count for each tag."""
        tag_counts = {}
        for chat in chats:
            for tag in chat.get("tags", []):
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        return dict(sorted(tag_counts.items(), key=lambda x: x[1], reverse=True))
    
    @staticmethod
    def get_tag_info(tag: str) -> Dict:
        """Get information about a tag."""
        return ConversationTagger.DEFAULT_TAGS.get(tag, {"color": "gray", "emoji": "🏷️"})
    
    @staticmethod
    def auto_tag_by_content(chat: dict) -> List[str]:
        """Auto-detect tags based on chat content."""
        suggested_tags = []
        messages = chat.get("messages", [])
        
        content = " ".join([str(m.get("content", "")) for m in messages if isinstance(m, dict)])
        content_lower = content.lower()
        
        # Auto-tagging logic
        if any(word in content_lower for word in ["error", "bug", "broken", "fail"]):
            suggested_tags.append("bug")
        
        if any(word in content_lower for word in ["help", "how", "explain", "question"]):
            suggested_tags.append("question")
        
        if any(word in content_lower for word in ["solved", "fixed", "working", "success"]):
            suggested_tags.append("solved")
        
        if any(word in content_lower for word in ["document", "readme", "wiki", "comment"]):
            suggested_tags.append("documentation")
        
        if any(word in content_lower for word in ["new feature", "implement", "add", "create"]):
            suggested_tags.append("feature")
        
        return suggested_tags
