"""Auto-complete and smart suggestions."""

from typing import List, Dict
from collections import Counter


class AutoCompleter:
    """Provide auto-complete suggestions from chat history."""
    
    @staticmethod
    def get_suggestions(chats: List[Dict], prefix: str, limit: int = 5) -> List[str]:
        """
        Get auto-complete suggestions based on chat history.
        
        Args:
            chats: List of chats
            prefix: Text prefix to complete
            limit: Maximum suggestions
            
        Returns:
            list: Suggested completions
        """
        suggestions = set()
        prefix_lower = prefix.lower()
        
        for chat in chats:
            messages = chat.get("messages", [])
            
            for msg in messages:
                if not isinstance(msg, dict):
                    continue
                
                content = str(msg.get("content", ""))
                
                # Split into words and sentences
                sentences = content.split(". ")
                
                for sentence in sentences:
                    words = sentence.split()
                    
                    # Look for words starting with prefix
                    for word in words:
                        if word.lower().startswith(prefix_lower):
                            # Clean word
                            clean_word = word.strip(".,!?;:")
                            if len(clean_word) > len(prefix):
                                suggestions.add(clean_word)
        
        return sorted(list(suggestions))[:limit]
    
    @staticmethod
    def get_phrase_suggestions(chats: List[Dict], prefix: str, limit: int = 5) -> List[str]:
        """Get multi-word phrase suggestions."""
        suggestions = []
        prefix_lower = prefix.lower()
        
        for chat in chats:
            messages = chat.get("messages", [])
            
            for msg in messages:
                if not isinstance(msg, dict):
                    continue
                
                content = str(msg.get("content", ""))
                
                # Look for phrases starting with prefix
                if prefix_lower in content.lower():
                    start_idx = content.lower().find(prefix_lower)
                    # Get next 50 characters as phrase
                    phrase = content[start_idx:start_idx + 100].split("\n")[0]
                    if len(phrase) > len(prefix):
                        suggestions.append(phrase)
        
        # Return most common
        counter = Counter(suggestions)
        return [phrase for phrase, _ in counter.most_common(limit)]
    
    @staticmethod
    def get_context_suggestions(chat: Dict, context_type: str = "next") -> List[str]:
        """
        Get suggestions based on conversation context.
        
        Types:
            next: What typically comes next
            follow_up: Common follow-up questions
            related: Related topics
        """
        messages = chat.get("messages", [])
        if not messages:
            return []
        
        suggestions = []
        
        if context_type == "next":
            # Find last user message and see what assistant typically says
            for i in range(len(messages) - 1, -1, -1):
                if messages[i].get("role") == "user":
                    # Look for common response patterns
                    if i + 1 < len(messages) and messages[i + 1].get("role") == "assistant":
                        response = str(messages[i + 1].get("content", ""))
                        # Get first sentence as suggestion
                        first_sentence = response.split(".")[0] + "."
                        suggestions.append(first_sentence)
                    break
        
        elif context_type == "follow_up":
            # Suggest common follow-up questions
            follow_ups = [
                "Can you explain that in more detail?",
                "Can you provide an example?",
                "How does that work?",
                "What are the best practices?",
                "Can you provide code for this?",
            ]
            return follow_ups
        
        elif context_type == "related":
            # Find related topics from all messages
            all_content = " ".join([str(m.get("content", "")) for m in messages if isinstance(m, dict)])
            keywords = set()
            for word in all_content.split():
                if len(word) > 5:  # Focus on longer words (likely more meaningful)
                    keywords.add(word.strip(".,!?;:"))
            return list(keywords)[:5]
        
        return suggestions
    
    @staticmethod
    def get_code_completions(chats: List[Dict], language: str = "python", prefix: str = "") -> List[str]:
        """Get code snippet completions."""
        completions = set()
        
        for chat in chats:
            messages = chat.get("messages", [])
            
            for msg in messages:
                if not isinstance(msg, dict):
                    continue
                
                content = str(msg.get("content", ""))
                
                # Extract code blocks
                if f"```{language}" in content:
                    code_start = content.find(f"```{language}") + len(f"```{language}") + 1
                    code_end = content.find("```", code_start)
                    if code_end > code_start:
                        code = content[code_start:code_end].strip()
                        
                        # If prefix specified, find matching lines
                        if prefix:
                            for line in code.split("\n"):
                                if prefix.lower() in line.lower():
                                    completions.add(line.strip())
                        else:
                            # Get first few lines as suggestions
                            for line in code.split("\n")[:3]:
                                completions.add(line.strip())
        
        return list(completions)[:10]
    
    @staticmethod
    def suggest_next_action(chat: Dict) -> List[str]:
        """Suggest what user might want to do next."""
        messages = chat.get("messages", [])
        
        suggestions = []
        
        # Check if chat has been solved
        tags = chat.get("tags", [])
        if "solved" in tags:
            suggestions.append("Export this conversation")
            suggestions.append("Bookmark important messages")
        
        # Check message count
        if len(messages) > 20:
            suggestions.append("Consider creating a new chat")
            suggestions.append("Save snippets from this chat")
        
        # Check if code-heavy
        code_count = sum(1 for m in messages if isinstance(m, dict) and "```" in str(m.get("content", "")))
        if code_count > 3:
            suggestions.append("Export code snippets")
            suggestions.append("Review and bookmark code solutions")
        
        return suggestions
