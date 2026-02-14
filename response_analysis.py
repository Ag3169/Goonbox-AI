"""Model comparison and response analysis."""

from datetime import datetime
from typing import Dict, List


class ResponseAnalyzer:
    """Analyze and compare AI responses."""
    
    @staticmethod
    def analyze_response(message: dict, model: str, provider: str) -> Dict:
        """Analyze a response for quality metrics."""
        content = str(message.get("content", ""))
        
        return {
            "model": model,
            "provider": provider,
            "timestamp": datetime.now().isoformat(),
            "length": len(content),
            "word_count": len(content.split()),
            "has_code": "```" in content or "`" in content,
            "has_links": "http" in content or "www" in content,
            "has_formatting": any(f in content for f in ["**", "__", "##", "> "]),
            "estimated_tokens": len(content.split()) * 1.3,
        }
    
    @staticmethod
    def record_response(chat: dict, analysis: Dict) -> bool:
        """Record response analysis."""
        if "response_analysis" not in chat:
            chat["response_analysis"] = []
        
        chat["response_analysis"].append(analysis)
        return True
    
    @staticmethod
    def compare_responses(chat: dict, question_index: int) -> Dict:
        """Compare responses for same question from different models."""
        analyses = chat.get("response_analysis", [])
        
        if question_index >= len(analyses):
            return {}
        
        comparison = {
            "question_index": question_index,
            "responses": [],
        }
        
        # Group by question and compare responses
        for analysis in analyses:
            if analysis.get("question_index") == question_index:
                comparison["responses"].append(analysis)
        
        return comparison
    
    @staticmethod
    def get_model_performance(chat: dict) -> Dict[str, Dict]:
        """Get performance statistics by model."""
        analyses = chat.get("response_analysis", [])
        model_stats = {}
        
        for analysis in analyses:
            model = analysis.get("model", "unknown")
            
            if model not in model_stats:
                model_stats[model] = {
                    "count": 0,
                    "total_length": 0,
                    "avg_length": 0,
                    "total_words": 0,
                    "avg_words": 0,
                }
            
            model_stats[model]["count"] += 1
            model_stats[model]["total_length"] += analysis.get("length", 0)
            model_stats[model]["total_words"] += analysis.get("word_count", 0)
        
        # Calculate averages
        for model, stats in model_stats.items():
            if stats["count"] > 0:
                stats["avg_length"] = int(stats["total_length"] / stats["count"])
                stats["avg_words"] = int(stats["total_words"] / stats["count"])
        
        return model_stats
    
    @staticmethod
    def get_best_responding_model(chat: dict, metric: str = "length") -> str:
        """Determine best responding model by metric."""
        stats = ResponseAnalyzer.get_model_performance(chat)
        
        if not stats:
            return "unknown"
        
        if metric == "length":
            return max(stats.items(), key=lambda x: x[1]["avg_length"])[0]
        elif metric == "conciseness":
            return min(stats.items(), key=lambda x: x[1]["avg_length"])[0]
        elif metric == "usage":
            return max(stats.items(), key=lambda x: x[1]["count"])[0]
        
        return list(stats.keys())[0]


class ResponseMetadataTracker:
    """Track response metadata and timing."""
    
    @staticmethod
    def record_response_time(message: dict, response_time: float) -> bool:
        """Record response generation time."""
        if "metadata" not in message:
            message["metadata"] = {}
        
        message["metadata"]["response_time_ms"] = response_time
        return True
    
    @staticmethod
    def get_response_time(message: dict) -> float:
        """Get response time for a message."""
        return message.get("metadata", {}).get("response_time_ms", 0.0)
    
    @staticmethod
    def get_average_response_time(chat: dict) -> float:
        """Get average response time for chat."""
        messages = chat.get("messages", [])
        response_times = []
        
        for msg in messages:
            if isinstance(msg, dict):
                rt = ResponseMetadataTracker.get_response_time(msg)
                if rt > 0:
                    response_times.append(rt)
        
        if not response_times:
            return 0.0
        
        return sum(response_times) / len(response_times)
    
    @staticmethod
    def get_fastest_response(chat: dict) -> float:
        """Get fastest response time."""
        messages = chat.get("messages", [])
        response_times = [
            ResponseMetadataTracker.get_response_time(msg)
            for msg in messages
            if isinstance(msg, dict) and ResponseMetadataTracker.get_response_time(msg) > 0
        ]
        
        return min(response_times) if response_times else 0.0
    
    @staticmethod
    def get_slowest_response(chat: dict) -> float:
        """Get slowest response time."""
        messages = chat.get("messages", [])
        response_times = [
            ResponseMetadataTracker.get_response_time(msg)
            for msg in messages
            if isinstance(msg, dict) and ResponseMetadataTracker.get_response_time(msg) > 0
        ]
        
        return max(response_times) if response_times else 0.0
