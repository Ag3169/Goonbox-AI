"""Conversation templates and starters."""

from typing import List, Dict


class ConversationTemplate:
    """Pre-built conversation templates."""
    
    TEMPLATES = {
        "code_review": {
            "name": "Code Review",
            "description": "Get feedback on code quality",
            "starter": "Can you review this code and suggest improvements?",
            "context": ["Check for performance issues", "Verify best practices", "Suggest refactoring"],
            "category": "Development"
        },
        "debugging": {
            "name": "Debugging Session",
            "description": "Help debug code issues",
            "starter": "I'm getting an error. Can you help me debug this?",
            "context": ["Show error message", "Show relevant code", "Describe expected behavior"],
            "category": "Development"
        },
        "learning": {
            "name": "Learn New Concept",
            "description": "Learn programming concepts",
            "starter": "Can you explain how [concept] works?",
            "context": ["Explain with examples", "Show use cases", "Common pitfalls"],
            "category": "Learning"
        },
        "architecture": {
            "name": "System Architecture",
            "description": "Design system architecture",
            "starter": "How should I architect a [system type]?",
            "context": ["Scalability concerns", "Technology choices", "Best practices"],
            "category": "Architecture"
        },
        "optimization": {
            "name": "Performance Optimization",
            "description": "Optimize code performance",
            "starter": "This code is slow. How can I optimize it?",
            "context": ["Profile the code", "Identify bottlenecks", "Suggest improvements"],
            "category": "Performance"
        },
        "web_design": {
            "name": "Web Design Help",
            "description": "Design responsive web UIs",
            "starter": "Can you help me design a [component] for my website?",
            "context": ["Mobile responsive", "Accessibility", "Best practices"],
            "category": "Web Design"
        },
    }
    
    @staticmethod
    def get_template(template_id: str) -> Dict:
        """Get a conversation template."""
        return ConversationTemplate.TEMPLATES.get(template_id, {})
    
    @staticmethod
    def get_all_templates() -> Dict:
        """Get all available templates."""
        return ConversationTemplate.TEMPLATES
    
    @staticmethod
    def get_templates_by_category(category: str) -> List[Dict]:
        """Get templates filtered by category."""
        return [
            template for template in ConversationTemplate.TEMPLATES.values()
            if template.get("category") == category
        ]
    
    @staticmethod
    def get_categories() -> List[str]:
        """Get all available categories."""
        categories = set()
        for template in ConversationTemplate.TEMPLATES.values():
            categories.add(template.get("category"))
        return sorted(list(categories))
    
    @staticmethod
    def apply_template(template_id: str, custom_context: str = "") -> str:
        """Apply template and return starter message."""
        template = ConversationTemplate.get_template(template_id)
        if not template:
            return ""
        
        message = template.get("starter", "")
        if custom_context:
            message += f"\n\nContext: {custom_context}"
        
        # Add context hints
        context_items = template.get("context", [])
        if context_items:
            message += "\n\nPlease also:\n"
            message += "\n".join([f"- {item}" for item in context_items])
        
        return message
