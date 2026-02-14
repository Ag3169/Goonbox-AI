"""Code snippet management and organization."""

from typing import List, Dict


class CodeSnippetManager:
    """Manage code snippets from IDE."""
    
    @staticmethod
    def save_snippet(code: str, language: str, description: str = "", tags: List[str] = None) -> Dict:
        """
        Save a code snippet.
        
        Args:
            code: Code content
            language: Programming language (python, html, css, javascript)
            description: Human-readable description
            tags: Optional tags for categorization
            
        Returns:
            dict: Snippet data
        """
        import hashlib
        from datetime import datetime
        
        snippet_id = hashlib.md5((code + str(datetime.now())).encode()).hexdigest()[:8]
        
        return {
            "id": snippet_id,
            "code": code,
            "language": language,
            "description": description,
            "tags": tags or [],
            "created": datetime.now().isoformat(),
            "usage_count": 0,
        }
    
    @staticmethod
    def search_snippets(snippets: List[Dict], query: str) -> List[Dict]:
        """Search snippets by description or tags."""
        results = []
        query_lower = query.lower()
        
        for snippet in snippets:
            if (query_lower in snippet.get("description", "").lower() or
                query_lower in str(snippet.get("tags", [])).lower()):
                results.append(snippet)
        
        return results
    
    @staticmethod
    def get_snippets_by_language(snippets: List[Dict], language: str) -> List[Dict]:
        """Get all snippets of a specific language."""
        return [s for s in snippets if s.get("language") == language]
    
    @staticmethod
    def get_snippets_by_tag(snippets: List[Dict], tag: str) -> List[Dict]:
        """Get all snippets with a specific tag."""
        return [s for s in snippets if tag in s.get("tags", [])]
    
    @staticmethod
    def increment_usage(snippet: Dict) -> None:
        """Increment usage count for a snippet."""
        snippet["usage_count"] = snippet.get("usage_count", 0) + 1
    
    @staticmethod
    def get_popular_snippets(snippets: List[Dict], limit: int = 10) -> List[Dict]:
        """Get most used snippets."""
        sorted_snippets = sorted(snippets, key=lambda x: x.get("usage_count", 0), reverse=True)
        return sorted_snippets[:limit]
    
    @staticmethod
    def export_snippets(snippets: List[Dict], format: str = "json") -> str:
        """Export snippets in various formats."""
        if format == "json":
            import json
            return json.dumps(snippets, indent=2)
        
        elif format == "markdown":
            lines = ["# Code Snippets\n"]
            
            for snippet in snippets:
                lines.append(f"## {snippet.get('description', 'Untitled')}")
                lines.append(f"**Language**: {snippet.get('language')}")
                lines.append(f"**Tags**: {', '.join(snippet.get('tags', []))}")
                lines.append(f"**Used**: {snippet.get('usage_count', 0)} times\n")
                lines.append(f"```{snippet.get('language')}")
                lines.append(snippet.get('code', ''))
                lines.append("```\n")
            
            return "\n".join(lines)
        
        return str(snippets)
