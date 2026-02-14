"""Analytics and usage tracking."""

from datetime import datetime
from typing import Dict


class AnalyticsTracker:
    """Track application usage and analytics."""
    
    @staticmethod
    def track_message(message: dict, provider: str, model: str) -> Dict:
        """Track individual message metrics."""
        return {
            "timestamp": datetime.now().isoformat(),
            "provider": provider,
            "model": model,
            "role": message.get("role"),
            "content_length": len(str(message.get("content", ""))),
            "token_estimate": len(str(message.get("content", "")).split()) * 1.3,  # Rough estimate
        }
    
    @staticmethod
    def calculate_session_stats(chats: list) -> Dict:
        """Calculate statistics for current session."""
        total_messages = 0
        total_characters = 0
        provider_usage = {}
        
        for chat in chats:
            messages = chat.get("messages", [])
            total_messages += len(messages)
            
            for msg in messages:
                if isinstance(msg, dict):
                    total_characters += len(str(msg.get("content", "")))
        
        return {
            "total_chats": len(chats),
            "total_messages": total_messages,
            "total_characters": total_characters,
            "average_message_length": int(total_characters / total_messages) if total_messages > 0 else 0,
            "session_duration": "0:00",  # Should be calculated from session start
        }
    
    @staticmethod
    def get_provider_stats(chats: list) -> Dict:
        """Get usage statistics by provider."""
        provider_stats = {}
        
        for chat in chats:
            # Provider would be tracked in chat metadata
            provider = chat.get("provider", "unknown")
            if provider not in provider_stats:
                provider_stats[provider] = {
                    "chats": 0,
                    "messages": 0,
                    "total_characters": 0,
                }
            
            provider_stats[provider]["chats"] += 1
            messages = chat.get("messages", [])
            provider_stats[provider]["messages"] += len(messages)
            provider_stats[provider]["total_characters"] += sum(
                len(str(m.get("content", ""))) for m in messages if isinstance(m, dict)
            )
        
        return provider_stats
    
    @staticmethod
    def get_most_used_features() -> Dict:
        """Get statistics about feature usage."""
        return {
            "export_count": 0,
            "search_count": 0,
            "package_installations": 0,
            "code_executions": 0,
            "file_operations": 0,
        }
    
    @staticmethod
    def generate_usage_report(chats: list, agent_chats: list) -> str:
        """Generate a formatted usage report."""
        session_stats = AnalyticsTracker.calculate_session_stats(chats)
        
        lines = [
            "# Application Usage Report",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Session Statistics",
            f"Total Chats: {session_stats['total_chats']}",
            f"Total Messages: {session_stats['total_messages']}",
            f"Total Characters: {session_stats['total_characters']:,}",
            f"Average Message Length: {session_stats['average_message_length']} chars",
            "",
            "## Chat Breakdown",
            f"Regular Chats: {len(chats)}",
            f"Agent Chats: {len(agent_chats)}",
        ]
        
        return "\n".join(lines)
