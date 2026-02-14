"""Code execution history and diff tracking."""

from datetime import datetime
from typing import Dict, List


class CodeExecutionHistory:
    """Track code execution history with output."""
    
    @staticmethod
    def record_execution(code: str, output: str, error: str = "", 
                        language: str = "python", execution_time: float = 0.0) -> Dict:
        """Record a code execution."""
        return {
            "timestamp": datetime.now().isoformat(),
            "code": code,
            "output": output,
            "error": error,
            "language": language,
            "execution_time": execution_time,
            "status": "error" if error else "success",
        }
    
    @staticmethod
    def save_to_chat(chat: dict, execution: Dict) -> bool:
        """Save execution to chat history."""
        if "code_history" not in chat:
            chat["code_history"] = []
        
        chat["code_history"].append(execution)
        return True
    
    @staticmethod
    def get_execution_history(chat: dict, limit: int = 10) -> List[Dict]:
        """Get recent code executions."""
        history = chat.get("code_history", [])
        return history[-limit:]
    
    @staticmethod
    def get_successful_executions(chat: dict) -> List[Dict]:
        """Get all successful code executions."""
        history = chat.get("code_history", [])
        return [h for h in history if h.get("status") == "success"]
    
    @staticmethod
    def get_failed_executions(chat: dict) -> List[Dict]:
        """Get all failed code executions."""
        history = chat.get("code_history", [])
        return [h for h in history if h.get("status") == "error"]
    
    @staticmethod
    def get_execution_by_language(chat: dict, language: str) -> List[Dict]:
        """Get executions filtered by language."""
        history = chat.get("code_history", [])
        return [h for h in history if h.get("language") == language]


class CodeDiffTracker:
    """Track changes to code over time."""
    
    @staticmethod
    def record_code_change(file_path: str, old_code: str, new_code: str, 
                          description: str = "") -> Dict:
        """Record a code change."""
        import difflib
        
        diff = list(difflib.unified_diff(
            old_code.splitlines(keepends=True),
            new_code.splitlines(keepends=True),
            lineterm=''
        ))
        
        return {
            "timestamp": datetime.now().isoformat(),
            "file": file_path,
            "old_code": old_code,
            "new_code": new_code,
            "description": description,
            "diff": diff,
            "lines_added": len([l for l in diff if l.startswith("+")]),
            "lines_removed": len([l for l in diff if l.startswith("-")]),
        }
    
    @staticmethod
    def get_code_changes(chat: dict, file_path: str = None) -> List[Dict]:
        """Get code changes for a file."""
        changes = chat.get("code_changes", [])
        
        if file_path:
            changes = [c for c in changes if c.get("file") == file_path]
        
        return changes
    
    @staticmethod
    def save_change(chat: dict, change: Dict) -> bool:
        """Save a code change."""
        if "code_changes" not in chat:
            chat["code_changes"] = []
        
        chat["code_changes"].append(change)
        return True
    
    @staticmethod
    def get_file_timeline(chat: dict, file_path: str) -> List[Dict]:
        """Get timeline of changes for a specific file."""
        changes = CodeDiffTracker.get_code_changes(chat, file_path)
        return sorted(changes, key=lambda x: x.get("timestamp", ""))
    
    @staticmethod
    def generate_diff_summary(chat: dict, file_path: str) -> str:
        """Generate a summary of changes for a file."""
        changes = CodeDiffTracker.get_code_changes(chat, file_path)
        
        lines = [f"# Changes to {file_path}\n"]
        
        total_added = sum(c.get("lines_added", 0) for c in changes)
        total_removed = sum(c.get("lines_removed", 0) for c in changes)
        
        lines.append(f"Total changes: {len(changes)}")
        lines.append(f"Lines added: {total_added}")
        lines.append(f"Lines removed: {total_removed}\n")
        
        for change in changes:
            lines.append(f"## {change.get('timestamp')}")
            if change.get("description"):
                lines.append(f"Description: {change.get('description')}")
            lines.append("")
        
        return "\n".join(lines)
