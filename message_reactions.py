"""Message reactions and quality ratings."""

from typing import Dict, List
from datetime import datetime


class MessageReactions:
    """Manage reactions and ratings on messages."""
    
    REACTIONS = {
        "helpful": "👍",
        "loved": "❤️",
        "thinking": "🤔",
        "learning": "📚",
        "important": "⭐",
        "saved": "💾",
    }
    
    @staticmethod
    def add_reaction(chat: dict, message_index: int, reaction_type: str) -> bool:
        """Add a reaction to a message."""
        if "reactions" not in chat:
            chat["reactions"] = {}
        
        reactions_key = f"msg_{message_index}"
        if reactions_key not in chat["reactions"]:
            chat["reactions"][reactions_key] = {}
        
        if reaction_type in MessageReactions.REACTIONS:
            chat["reactions"][reactions_key][reaction_type] = \
                chat["reactions"][reactions_key].get(reaction_type, 0) + 1
            return True
        
        return False
    
    @staticmethod
    def remove_reaction(chat: dict, message_index: int, reaction_type: str) -> bool:
        """Remove a reaction from a message."""
        reactions_key = f"msg_{message_index}"
        
        if (reactions_key in chat.get("reactions", {}) and 
            reaction_type in chat["reactions"][reactions_key]):
            
            chat["reactions"][reactions_key][reaction_type] -= 1
            
            if chat["reactions"][reactions_key][reaction_type] <= 0:
                del chat["reactions"][reactions_key][reaction_type]
            
            return True
        
        return False
    
    @staticmethod
    def get_reactions(chat: dict, message_index: int) -> Dict:
        """Get all reactions for a message."""
        reactions_key = f"msg_{message_index}"
        return chat.get("reactions", {}).get(reactions_key, {})
    
    @staticmethod
    def rate_message(chat: dict, message_index: int, rating: int, 
                    comment: str = "") -> bool:
        """Rate a message quality (1-5 stars)."""
        if rating < 1 or rating > 5:
            return False
        
        if "ratings" not in chat:
            chat["ratings"] = {}
        
        ratings_key = f"msg_{message_index}"
        
        chat["ratings"][ratings_key] = {
            "rating": rating,
            "comment": comment,
            "timestamp": datetime.now().isoformat(),
        }
        
        return True
    
    @staticmethod
    def get_rating(chat: dict, message_index: int) -> Dict:
        """Get rating for a message."""
        ratings_key = f"msg_{message_index}"
        return chat.get("ratings", {}).get(ratings_key, {})
    
    @staticmethod
    def get_average_rating(chat: dict) -> float:
        """Get average rating for all messages in chat."""
        ratings = chat.get("ratings", {})
        if not ratings:
            return 0.0
        
        total = sum(r.get("rating", 0) for r in ratings.values())
        return total / len(ratings)
    
    @staticmethod
    def get_helpful_messages(chat: dict, min_reactions: int = 2) -> List[int]:
        """Get messages with most helpful reactions."""
        reactions = chat.get("reactions", {})
        helpful_messages = []
        
        for reactions_key, reaction_dict in reactions.items():
            if reaction_dict.get("helpful", 0) >= min_reactions:
                msg_index = int(reactions_key.split("_")[1])
                helpful_messages.append(msg_index)
        
        return sorted(helpful_messages)
    
    @staticmethod
    def get_highly_rated_messages(chat: dict, min_rating: float = 4.0) -> List[int]:
        """Get messages with high quality ratings."""
        ratings = chat.get("ratings", {})
        rated_messages = []
        
        for ratings_key, rating_dict in ratings.items():
            if rating_dict.get("rating", 0) >= min_rating:
                msg_index = int(ratings_key.split("_")[1])
                rated_messages.append(msg_index)
        
        return sorted(rated_messages)
