"""Conversation forking - create variations of a chat."""

import copy
from typing import Dict, List
from datetime import datetime


class ConversationForker:
    """Fork conversations to explore alternative paths."""
    
    @staticmethod
    def fork_at_message(chat: Dict, fork_index: int, fork_title: str = "") -> Dict:
        """
        Create a fork of a conversation at a specific message index.
        
        Args:
            chat: Original chat
            fork_index: Message index to fork at
            fork_title: Title for new fork
            
        Returns:
            dict: Forked chat
        """
        forked_chat = copy.deepcopy(chat)
        
        # Keep messages up to fork point
        messages = chat.get("messages", [])
        if fork_index < 0 or fork_index > len(messages):
            return {}
        
        forked_chat["messages"] = messages[:fork_index]
        forked_chat["id"] = f"{chat.get('id')}-fork-{datetime.now().timestamp()}"
        forked_chat["title"] = fork_title or f"{chat.get('title')} (Fork)"
        forked_chat["parent_chat_id"] = chat.get("id")
        forked_chat["fork_point"] = fork_index
        forked_chat["created_at"] = datetime.now().isoformat()
        
        if "forks" not in chat:
            chat["forks"] = []
        
        chat["forks"].append({
            "fork_id": forked_chat["id"],
            "fork_title": forked_chat["title"],
            "fork_point": fork_index,
            "created_at": forked_chat["created_at"],
        })
        
        return forked_chat
    
    @staticmethod
    def fork_with_new_message(chat: Dict, fork_index: int, 
                             new_message: Dict, fork_title: str = "") -> Dict:
        """
        Create a fork and add a new message instead of the original path.
        
        Args:
            chat: Original chat
            fork_index: Message index to fork at
            new_message: New message to add
            fork_title: Title for new fork
            
        Returns:
            dict: Forked chat with new message
        """
        forked_chat = ConversationForker.fork_at_message(chat, fork_index, fork_title)
        
        if forked_chat:
            forked_chat["messages"].append(new_message)
            forked_chat["fork_variation"] = {
                "fork_point": fork_index,
                "replaced_message": chat.get("messages", [])[fork_index] if fork_index < len(chat.get("messages", [])) else None,
                "new_message": new_message,
            }
        
        return forked_chat
    
    @staticmethod
    def merge_fork_back(original_chat: Dict, forked_chat: Dict, strategy: str = "append") -> bool:
        """
        Merge fork back into original chat.
        
        Strategies:
            append: Append fork messages after original
            replace: Replace messages from fork point
            interleave: Interleave fork and original messages
        
        Args:
            original_chat: Original chat
            forked_chat: Forked chat to merge
            strategy: Merge strategy
            
        Returns:
            bool: True if successful
        """
        original_messages = original_chat.get("messages", [])
        fork_messages = forked_chat.get("messages", [])
        fork_point = forked_chat.get("fork_point", 0)
        
        if strategy == "append":
            # Append fork messages
            original_chat["messages"] = original_messages + fork_messages[fork_point:]
        
        elif strategy == "replace":
            # Replace from fork point
            original_chat["messages"] = original_messages[:fork_point] + fork_messages[fork_point:]
        
        elif strategy == "interleave":
            # Interleave messages
            result = original_messages[:fork_point]
            fork_new = fork_messages[fork_point:]
            original_new = original_messages[fork_point:]
            
            for i in range(max(len(fork_new), len(original_new))):
                if i < len(fork_new):
                    result.append(fork_new[i])
                if i < len(original_new):
                    result.append(original_new[i])
            
            original_chat["messages"] = result
        
        # Track merge
        if "merged_forks" not in original_chat:
            original_chat["merged_forks"] = []
        
        original_chat["merged_forks"].append({
            "fork_id": forked_chat.get("id"),
            "merged_at": datetime.now().isoformat(),
            "strategy": strategy,
        })
        
        return True
    
    @staticmethod
    def get_fork_tree(chat: Dict) -> Dict:
        """Get tree structure of all forks."""
        tree = {
            "id": chat.get("id"),
            "title": chat.get("title"),
            "forks": [],
            "is_fork": "parent_chat_id" in chat,
            "parent_id": chat.get("parent_chat_id"),
        }
        
        # Add fork info
        for fork_info in chat.get("forks", []):
            tree["forks"].append({
                "fork_id": fork_info.get("fork_id"),
                "title": fork_info.get("fork_title"),
                "created_at": fork_info.get("created_at"),
            })
        
        return tree
    
    @staticmethod
    def list_forks(chat: Dict) -> List[Dict]:
        """Get list of all forks from this chat."""
        return chat.get("forks", [])
    
    @staticmethod
    def get_fork_differences(original_chat: Dict, forked_chat: Dict) -> Dict:
        """Get differences between original and fork."""
        original_messages = original_chat.get("messages", [])
        forked_messages = forked_chat.get("messages", [])
        fork_point = forked_chat.get("fork_point", 0)
        
        return {
            "fork_point": fork_point,
            "original_after_fork": len(original_messages) - fork_point,
            "fork_length": len(forked_messages) - fork_point,
            "messages_added_in_fork": forked_messages[fork_point:],
            "messages_in_original_branch": original_messages[fork_point:],
        }
