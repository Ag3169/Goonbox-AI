"""Chat backup and restore functionality."""

import json
import gzip
from datetime import datetime
from pathlib import Path


class ChatBackupManager:
    """Manage chat backups and restoration."""
    
    @staticmethod
    def create_backup(chats: list, backup_path: Path) -> bool:
        """
        Create a compressed backup of all chats.
        
        Args:
            chats: List of chat dictionaries
            backup_path: Path to save backup file
            
        Returns:
            bool: True if successful
        """
        try:
            backup_data = {
                "timestamp": datetime.now().isoformat(),
                "version": "2.0",
                "chat_count": len(chats),
                "chats": chats,
            }
            
            # Compress the backup
            json_str = json.dumps(backup_data, indent=2, ensure_ascii=False)
            json_bytes = json_str.encode('utf-8')
            
            with gzip.open(backup_path, 'wb') as f:
                f.write(json_bytes)
            
            return True
        except Exception as e:
            print(f"Backup failed: {e}")
            return False
    
    @staticmethod
    def restore_backup(backup_path: Path) -> tuple[bool, list, str]:
        """
        Restore chats from a backup file.
        
        Args:
            backup_path: Path to backup file
            
        Returns:
            tuple: (success, restored_chats, message)
        """
        try:
            with gzip.open(backup_path, 'rb') as f:
                json_bytes = f.read()
            
            json_str = json_bytes.decode('utf-8')
            backup_data = json.loads(json_str)
            
            chats = backup_data.get("chats", [])
            timestamp = backup_data.get("timestamp", "Unknown")
            
            message = f"Restored {len(chats)} chats from backup (created: {timestamp})"
            
            return True, chats, message
        except Exception as e:
            return False, [], f"Restore failed: {str(e)}"
    
    @staticmethod
    def get_backup_info(backup_path: Path) -> dict:
        """Get information about a backup file."""
        try:
            with gzip.open(backup_path, 'rb') as f:
                json_bytes = f.read()
            
            json_str = json_bytes.decode('utf-8')
            backup_data = json.loads(json_str)
            
            return {
                "timestamp": backup_data.get("timestamp"),
                "version": backup_data.get("version"),
                "chat_count": backup_data.get("chat_count"),
                "file_size": backup_path.stat().st_size,
            }
        except Exception:
            return {}
    
    @staticmethod
    def auto_backup(chats: list, backup_dir: Path, max_backups: int = 5) -> bool:
        """
        Create automatic backup with rotation.
        
        Args:
            chats: List of chat dictionaries
            backup_dir: Directory to store backups
            max_backups: Maximum number of backups to keep
            
        Returns:
            bool: True if successful
        """
        try:
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = backup_dir / f"backup_{timestamp}.gz"
            
            success = ChatBackupManager.create_backup(chats, backup_path)
            
            if success:
                # Cleanup old backups
                backups = sorted(backup_dir.glob("backup_*.gz"))
                while len(backups) > max_backups:
                    old_backup = backups.pop(0)
                    old_backup.unlink()
            
            return success
        except Exception as e:
            print(f"Auto backup failed: {e}")
            return False
