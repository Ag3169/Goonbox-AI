"""Search functionality for chat conversations."""

from typing import List, Dict
import re


class ChatSearcher:
    """Search through chat messages."""
    
    @staticmethod
    def search_in_chat(chat: dict, query: str, case_sensitive: bool = False) -> List[Dict]:
        """
        Search for messages in a chat.
        
        Args:
            chat: Chat dictionary with messages
            query: Search query string
            case_sensitive: Whether to be case-sensitive
            
        Returns:
            List of matching message dictionaries with match info
        """
        results = []
        messages = chat.get("messages", [])
        
        if not query:
            return results
        
        search_query = query if case_sensitive else query.lower()
        
        for idx, msg in enumerate(messages):
            if not isinstance(msg, dict):
                continue
            
            content = str(msg.get("content", ""))
            search_content = content if case_sensitive else content.lower()
            
            if search_query in search_content:
                # Calculate position in content
                start_pos = search_content.find(search_query)
                end_pos = start_pos + len(search_query)
                
                # Get context (50 chars before and after)
                context_start = max(0, start_pos - 50)
                context_end = min(len(content), end_pos + 50)
                context = content[context_start:context_end]
                
                results.append({
                    "message_index": idx,
                    "role": msg.get("role", "unknown"),
                    "content": content,
                    "context": context,
                    "position": (start_pos, end_pos),
                })
        
        return results
    
    @staticmethod
    def search_in_all_chats(chats: list, query: str, case_sensitive: bool = False) -> Dict:
        """
        Search across all chats.
        
        Args:
            chats: List of chat dictionaries
            query: Search query string
            case_sensitive: Whether to be case-sensitive
            
        Returns:
            Dictionary with chat_id as key and list of results as value
        """
        results = {}
        
        for chat in chats:
            chat_results = ChatSearcher.search_in_chat(chat, query, case_sensitive)
            if chat_results:
                chat_id = chat.get("id", "unknown")
                chat_title = chat.get("title", "Unknown Chat")
                results[chat_id] = {
                    "title": chat_title,
                    "matches": len(chat_results),
                    "messages": chat_results,
                }
        
        return results
    
    @staticmethod
    def regex_search(chat: dict, pattern: str) -> List[Dict]:
        """
        Search using regex pattern.
        
        Args:
            chat: Chat dictionary
            pattern: Regex pattern string
            
        Returns:
            List of matching messages
        """
        results = []
        messages = chat.get("messages", [])
        
        try:
            regex = re.compile(pattern)
        except re.error:
            return results
        
        for idx, msg in enumerate(messages):
            if not isinstance(msg, dict):
                continue
            
            content = str(msg.get("content", ""))
            match = regex.search(content)
            
            if match:
                results.append({
                    "message_index": idx,
                    "role": msg.get("role", "unknown"),
                    "content": content,
                    "match": match.group(0),
                    "position": match.span(),
                })
        
        return results
