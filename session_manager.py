"""Session management and auto-save functionality."""

from datetime import datetime
from pathlib import Path


class SessionManager:
    """Manage application sessions with auto-save."""
    
    @staticmethod
    def save_session_state(state: dict, session_path: Path) -> bool:
        """
        Save complete session state.
        
        Args:
            state: Session state dictionary
            session_path: Path to save session
            
        Returns:
            bool: True if successful
        """
        try:
            import json
            
            session_data = {
                "timestamp": datetime.now().isoformat(),
                "app_version": "2.0",
                "current_mode": state.get("current_mode"),
                "current_chat_id": state.get("current_chat_id"),
                "current_ide_file": state.get("current_ide_file"),
                "provider": state.get("provider"),
                "model": state.get("model"),
                "ide_kind": state.get("ide_kind"),
            }
            
            with open(session_path, 'w') as f:
                json.dump(session_data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Session save failed: {e}")
            return False
    
    @staticmethod
    def load_session_state(session_path: Path) -> dict:
        """
        Load previous session state.
        
        Args:
            session_path: Path to session file
            
        Returns:
            dict: Restored session state
        """
        try:
            import json
            
            if not session_path.exists():
                return {}
            
            with open(session_path, 'r') as f:
                state = json.load(f)
            
            return state
        except Exception:
            return {}
    
    @staticmethod
    def get_session_history(history_dir: Path, limit: int = 10) -> list:
        """Get list of recent sessions."""
        try:
            history_dir.mkdir(parents=True, exist_ok=True)
            sessions = sorted(history_dir.glob("session_*.json"), reverse=True)
            return [s.name for s in sessions[:limit]]
        except Exception:
            return []
    
    @staticmethod
    def restore_from_session(session_path: Path) -> dict:
        """Restore complete application state from session."""
        return SessionManager.load_session_state(session_path)
    
    @staticmethod
    def create_session_snapshot(
        chats: list,
        agent_chats: list,
        current_chat_id: str,
        current_mode: str,
        snapshot_path: Path,
    ) -> bool:
        """
        Create a full snapshot of current state.
        
        Args:
            chats: List of chats
            agent_chats: List of agent chats
            current_chat_id: Current active chat
            current_mode: Current application mode
            snapshot_path: Path to save snapshot
            
        Returns:
            bool: True if successful
        """
        try:
            import json
            import gzip
            
            snapshot = {
                "timestamp": datetime.now().isoformat(),
                "current_chat_id": current_chat_id,
                "current_mode": current_mode,
                "chat_count": len(chats),
                "agent_chat_count": len(agent_chats),
                "chats": chats,
                "agent_chats": agent_chats,
            }
            
            json_str = json.dumps(snapshot, indent=2, ensure_ascii=False)
            json_bytes = json_str.encode('utf-8')
            
            with gzip.open(snapshot_path, 'wb') as f:
                f.write(json_bytes)
            
            return True
        except Exception as e:
            print(f"Snapshot failed: {e}")
            return False
