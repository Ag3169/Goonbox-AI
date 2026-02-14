"""Token and cost tracking for API usage."""

from typing import Dict, List
from datetime import datetime


class TokenTracker:
    """Track token usage and estimated costs."""
    
    # Approximate token-to-price mappings (per 1K tokens)
    PRICING = {
        "groq": {
            "llama-3.3-70b-versatile": {"input": 0.0, "output": 0.0},
            "llama-3.1-8b-instant": {"input": 0.0, "output": 0.0},  # Often free tier
            "mixtral-8x7b-32768": {"input": 0.0, "output": 0.0},
        },
        "openai": {
            "gpt-4": {"input": 0.03, "output": 0.06},
            "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
            "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        },
        "anthropic": {
            "claude-3": {"input": 0.015, "output": 0.075},
            "claude-3-sonnet": {"input": 0.003, "output": 0.015},
        },
        "google": {
            "gemini-pro": {"input": 0.0005, "output": 0.0015},
            "gemini-pro-vision": {"input": 0.001, "output": 0.002},
        },
    }
    
    @staticmethod
    def estimate_tokens(text: str) -> int:
        """Estimate token count from text (rough approximation)."""
        # Rough estimate: 1 token ≈ 4 characters or 0.75 words
        words = len(text.split())
        return int(words * 1.3)  # Conservative estimate
    
    @staticmethod
    def track_message(message: Dict, provider: str, model: str) -> Dict:
        """Track token usage for a message."""
        content = str(message.get("content", ""))
        
        input_tokens = TokenTracker.estimate_tokens(content)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "provider": provider,
            "model": model,
            "role": message.get("role"),
            "input_tokens": input_tokens,
            "output_tokens": 0,  # Will be updated when we get response
            "input_cost": TokenTracker.calculate_cost(input_tokens, provider, model, "input"),
            "output_cost": 0.0,
        }
    
    @staticmethod
    def calculate_cost(tokens: int, provider: str, model: str, token_type: str = "input") -> float:
        """Calculate cost for tokens."""
        pricing = TokenTracker.PRICING.get(provider, {}).get(model, {})
        
        if not pricing:
            return 0.0
        
        price_per_k = pricing.get(token_type, 0.0)
        return (tokens / 1000) * price_per_k
    
    @staticmethod
    def get_chat_token_stats(chat: Dict) -> Dict:
        """Get token statistics for a chat."""
        token_usage = chat.get("token_usage", [])
        
        if not token_usage:
            return {
                "total_input_tokens": 0,
                "total_output_tokens": 0,
                "total_cost": 0.0,
                "usage_count": 0,
            }
        
        total_input = sum(t.get("input_tokens", 0) for t in token_usage)
        total_output = sum(t.get("output_tokens", 0) for t in token_usage)
        total_cost = sum(t.get("input_cost", 0) + t.get("output_cost", 0) for t in token_usage)
        
        return {
            "total_input_tokens": total_input,
            "total_output_tokens": total_output,
            "total_tokens": total_input + total_output,
            "total_cost": round(total_cost, 4),
            "usage_count": len(token_usage),
            "average_tokens_per_message": int((total_input + total_output) / len(token_usage)) if token_usage else 0,
        }
    
    @staticmethod
    def get_provider_costs(chats: List[Dict]) -> Dict[str, Dict]:
        """Get costs breakdown by provider."""
        provider_stats = {}
        
        for chat in chats:
            token_usage = chat.get("token_usage", [])
            
            for usage in token_usage:
                provider = usage.get("provider", "unknown")
                
                if provider not in provider_stats:
                    provider_stats[provider] = {
                        "total_cost": 0.0,
                        "usage_count": 0,
                        "total_tokens": 0,
                    }
                
                provider_stats[provider]["total_cost"] += usage.get("input_cost", 0) + usage.get("output_cost", 0)
                provider_stats[provider]["usage_count"] += 1
                provider_stats[provider]["total_tokens"] += usage.get("input_tokens", 0) + usage.get("output_tokens", 0)
        
        return provider_stats
    
    @staticmethod
    def get_total_costs(chats: List[Dict]) -> float:
        """Get total costs across all chats."""
        total = 0.0
        
        for chat in chats:
            token_usage = chat.get("token_usage", [])
            for usage in token_usage:
                total += usage.get("input_cost", 0) + usage.get("output_cost", 0)
        
        return round(total, 4)
    
    @staticmethod
    def generate_cost_report(chats: List[Dict]) -> str:
        """Generate a formatted cost report."""
        total_cost = TokenTracker.get_total_costs(chats)
        provider_costs = TokenTracker.get_provider_costs(chats)
        
        lines = [
            "# Token & Cost Report",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            f"**Total Cost**: ${total_cost}",
            "",
            "## By Provider",
        ]
        
        for provider, stats in provider_costs.items():
            lines.append(f"- **{provider}**: ${stats['total_cost']} ({stats['usage_count']} uses)")
        
        return "\n".join(lines)
