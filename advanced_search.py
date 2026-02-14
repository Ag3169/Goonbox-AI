"""Advanced search with multiple filters."""

from typing import List, Dict
from datetime import datetime


class AdvancedSearcher:
    """Advanced search with multiple filters."""
    
    @staticmethod
    def search_with_filters(chats: List[Dict], query: str, filters: Dict = None) -> List[Dict]:
        """
        Search with multiple filters.
        
        Filters:
            role: Filter by message role (user, assistant, system)
            language: Filter by code language (python, javascript, etc)
            has_code: Filter messages with/without code
            has_links: Filter messages with/without links
            min_length: Minimum message length
            max_length: Maximum message length
            from_date: Start date (ISO format)
            to_date: End date (ISO format)
            tags: List of tags to filter
            category: Chat category
        """
        if filters is None:
            filters = {}
        
        results = []
        
        for chat in chats:
            # Check category filter
            if "category" in filters:
                if chat.get("category") != filters["category"]:
                    continue
            
            # Check tags filter
            if "tags" in filters:
                chat_tags = set(chat.get("tags", []))
                filter_tags = set(filters["tags"])
                if not chat_tags.intersection(filter_tags):
                    continue
            
            messages = chat.get("messages", [])
            
            for msg_idx, msg in enumerate(messages):
                if not isinstance(msg, dict):
                    continue
                
                content = str(msg.get("content", ""))
                
                # Check query
                if query.lower() not in content.lower():
                    continue
                
                # Check role filter
                if "role" in filters:
                    if msg.get("role") != filters["role"]:
                        continue
                
                # Check length filters
                if "min_length" in filters:
                    if len(content) < filters["min_length"]:
                        continue
                
                if "max_length" in filters:
                    if len(content) > filters["max_length"]:
                        continue
                
                # Check code filters
                if "has_code" in filters:
                    has_code = "```" in content or "`" in content
                    if filters["has_code"] != has_code:
                        continue
                
                # Check links filter
                if "has_links" in filters:
                    has_links = "http" in content or "www" in content
                    if filters["has_links"] != has_links:
                        continue
                
                # Check language filter
                if "language" in filters:
                    if filters["language"].lower() not in content.lower():
                        continue
                
                results.append({
                    "chat_id": chat.get("id"),
                    "chat_title": chat.get("title"),
                    "message_index": msg_idx,
                    "role": msg.get("role"),
                    "content_preview": content[:150],
                    "full_content": content,
                })
        
        return results
    
    @staticmethod
    def search_by_date_range(chats: List[Dict], from_date: str, to_date: str) -> List[Dict]:
        """Search messages within date range (ISO format)."""
        results = []
        
        for chat in chats:
            messages = chat.get("messages", [])
            
            for msg_idx, msg in enumerate(messages):
                if not isinstance(msg, dict):
                    continue
                
                timestamp = msg.get("timestamp", msg.get("created", ""))
                if timestamp >= from_date and timestamp <= to_date:
                    results.append({
                        "chat_id": chat.get("id"),
                        "chat_title": chat.get("title"),
                        "message_index": msg_idx,
                        "timestamp": timestamp,
                        "content": msg.get("content", "")[:100],
                    })
        
        return results
    
    @staticmethod
    def search_by_rating(chats: List[Dict], min_rating: float = 4.0) -> List[Dict]:
        """Find highly rated messages."""
        results = []
        
        for chat in chats:
            ratings = chat.get("ratings", {})
            
            for ratings_key, rating_data in ratings.items():
                if rating_data.get("rating", 0) >= min_rating:
                    msg_index = int(ratings_key.split("_")[1])
                    message = chat.get("messages", [])[msg_index] if msg_index < len(chat.get("messages", [])) else {}
                    
                    results.append({
                        "chat_id": chat.get("id"),
                        "chat_title": chat.get("title"),
                        "message_index": msg_index,
                        "rating": rating_data.get("rating"),
                        "comment": rating_data.get("comment", ""),
                        "content_preview": str(message.get("content", ""))[:100],
                    })
        
        return results
    
    @staticmethod
    def search_by_reaction(chats: List[Dict], reaction_type: str, min_count: int = 1) -> List[Dict]:
        """Find messages with specific reactions."""
        results = []
        
        for chat in chats:
            reactions = chat.get("reactions", {})
            
            for reactions_key, reaction_dict in reactions.items():
                if reaction_dict.get(reaction_type, 0) >= min_count:
                    msg_index = int(reactions_key.split("_")[1])
                    message = chat.get("messages", [])[msg_index] if msg_index < len(chat.get("messages", [])) else {}
                    
                    results.append({
                        "chat_id": chat.get("id"),
                        "chat_title": chat.get("title"),
                        "message_index": msg_index,
                        "reaction_count": reaction_dict.get(reaction_type, 0),
                        "content_preview": str(message.get("content", ""))[:100],
                    })
        
        return results
    
    @staticmethod
    def smart_search(chats: List[Dict], query: str) -> List[Dict]:
        """
        Smart search that detects query type and applies appropriate search.
        
        Supported:
            - Natural language queries
            - Code snippets
            - Tags (#tag)
            - Ratings (@4star)
            - Reactions (@helpful)
        """
        results = []
        
        # Check for special prefixes
        if query.startswith("#"):
            # Tag search
            tag = query[1:].strip()
            return AdvancedSearcher.search_with_filters(chats, "", filters={"tags": [tag]})
        
        elif query.startswith("@"):
            # Special search
            special = query[1:].strip().lower()
            if "star" in special:
                rating = int(special[0])
                return AdvancedSearcher.search_by_rating(chats, rating)
            else:
                return AdvancedSearcher.search_by_reaction(chats, special)
        
        else:
            # Regular search
            return AdvancedSearcher.search_with_filters(chats, query)
