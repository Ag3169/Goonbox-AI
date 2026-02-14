"""Chat merging and combining functionality."""

from typing import List, Dict
from datetime import datetime


class ChatMerger:
    """Merge and combine multiple conversations."""
    
    @staticmethod
    def merge_chats(source_chats: List[Dict], target_chat: Dict, 
                   keep_source: bool = False) -> bool:
        """
        Merge multiple chats into a target chat.
        
        Args:
            source_chats: List of chats to merge
            target_chat: Chat to merge into
            keep_source: Whether to keep source chats
            
        Returns:
            bool: True if successful
        """
        if "merged_from" not in target_chat:
            target_chat["merged_from"] = []
        
        for source_chat in source_chats:
            # Add source messages
            source_messages = source_chat.get("messages", [])
            target_messages = target_chat.get("messages", [])
            
            # Add separator and source info
            separator = {
                "role": "system",
                "content": f"--- Merged from: {source_chat.get('title', 'Unknown')} ---",
                "timestamp": datetime.now().isoformat(),
            }
            target_messages.append(separator)
            target_messages.extend(source_messages)
            
            # Track merge source
            target_chat["merged_from"].append({
                "source_id": source_chat.get("id"),
                "source_title": source_chat.get("title"),
                "message_count": len(source_messages),
                "merged_at": datetime.now().isoformat(),
            })
        
        return True
    
    @staticmethod
    def split_chat(chat: Dict, split_index: int) -> tuple[Dict, Dict]:
        """
        Split a chat at a specific message index.
        
        Args:
            chat: Chat to split
            split_index: Index to split at
            
        Returns:
            tuple: (first_chat, second_chat)
        """
        import copy
        
        messages = chat.get("messages", [])
        if split_index <= 0 or split_index >= len(messages):
            return chat, {}
        
        first_chat = copy.deepcopy(chat)
        first_chat["messages"] = messages[:split_index]
        first_chat["title"] = f"{chat.get('title')} (Part 1)"
        
        second_chat = copy.deepcopy(chat)
        second_chat["messages"] = messages[split_index:]
        second_chat["title"] = f"{chat.get('title')} (Part 2)"
        second_chat["id"] = f"{chat.get('id')}-part2"
        
        return first_chat, second_chat
    
    @staticmethod
    def combine_parallel_chats(chats: List[Dict], interleave: bool = False) -> Dict:
        """
        Combine multiple chats, optionally interleaving messages.
        
        Args:
            chats: List of chats to combine
            interleave: Whether to interleave messages from each chat
            
        Returns:
            dict: Combined chat
        """
        if not chats:
            return {}
        
        combined_chat = {
            "id": "combined-" + str(datetime.now().timestamp()),
            "title": "Combined Conversation",
            "messages": [],
            "combined_chats": [c.get("id") for c in chats],
        }
        
        if interleave:
            # Interleave messages from each chat
            max_len = max(len(c.get("messages", [])) for c in chats)
            
            for i in range(max_len):
                for chat in chats:
                    messages = chat.get("messages", [])
                    if i < len(messages):
                        combined_chat["messages"].append(messages[i])
        else:
            # Append sequentially with separators
            for chat in chats:
                separator = {
                    "role": "system",
                    "content": f"--- From: {chat.get('title', 'Unknown')} ---",
                }
                combined_chat["messages"].append(separator)
                combined_chat["messages"].extend(chat.get("messages", []))
        
        return combined_chat
    
    @staticmethod
    def get_merge_history(chat: Dict) -> List[Dict]:
        """Get history of merges for a chat."""
        return chat.get("merged_from", [])
