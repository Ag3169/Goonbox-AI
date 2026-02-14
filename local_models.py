"""Local model integration for LM Studio and Ollama."""

import requests
from typing import Dict, List, Optional
from datetime import datetime


class LocalModelManager:
    """Manage connections to local models via LM Studio or Ollama."""
    
    @staticmethod
    def test_lmstudio_connection(host: str = "localhost", port: int = 8000) -> bool:
        """
        Test connection to LM Studio.
        
        Args:
            host: LM Studio host (default: localhost)
            port: LM Studio port (default: 8000)
            
        Returns:
            bool: True if connection successful
        """
        try:
            url = f"http://{host}:{port}/v1/models"
            response = requests.get(url, timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"LM Studio connection failed: {e}")
            return False
    
    @staticmethod
    def test_ollama_connection(host: str = "localhost", port: int = 11434) -> bool:
        """
        Test connection to Ollama.
        
        Args:
            host: Ollama host (default: localhost)
            port: Ollama port (default: 11434)
            
        Returns:
            bool: True if connection successful
        """
        try:
            url = f"http://{host}:{port}/api/tags"
            response = requests.get(url, timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"Ollama connection failed: {e}")
            return False
    
    @staticmethod
    def get_lmstudio_models(host: str = "localhost", port: int = 8000) -> List[Dict]:
        """Get list of available models from LM Studio."""
        try:
            url = f"http://{host}:{port}/v1/models"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                return data.get("data", [])
            return []
        except Exception as e:
            print(f"Failed to get LM Studio models: {e}")
            return []
    
    @staticmethod
    def get_ollama_models(host: str = "localhost", port: int = 11434) -> List[Dict]:
        """Get list of available models from Ollama."""
        try:
            url = f"http://{host}:{port}/api/tags"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                models = data.get("models", [])
                return [{"id": m.get("name"), "name": m.get("name")} for m in models]
            return []
        except Exception as e:
            print(f"Failed to get Ollama models: {e}")
            return []
    
    @staticmethod
    def get_local_model_info(model_type: str, host: str, port: int) -> Dict:
        """Get information about a local model."""
        info = {
            "model_type": model_type,
            "host": host,
            "port": port,
            "connection_status": "connecting",
            "available_models": [],
            "timestamp": datetime.now().isoformat(),
        }
        
        if model_type == "lmstudio":
            if LocalModelManager.test_lmstudio_connection(host, port):
                info["connection_status"] = "connected"
                info["available_models"] = LocalModelManager.get_lmstudio_models(host, port)
            else:
                info["connection_status"] = "failed"
        
        elif model_type == "ollama":
            if LocalModelManager.test_ollama_connection(host, port):
                info["connection_status"] = "connected"
                info["available_models"] = LocalModelManager.get_ollama_models(host, port)
            else:
                info["connection_status"] = "failed"
        
        return info


class LMStudioClient:
    """Client for LM Studio (OpenAI-compatible API)."""
    
    def __init__(self, host: str = "localhost", port: int = 8000, model: str = ""):
        self.host = host
        self.port = port
        self.model = model
        self.base_url = f"http://{host}:{port}/v1"
        self.api_key = "not-needed"  # LM Studio doesn't require API key
    
    def send_message(self, messages: List[Dict], temperature: float = 0.7) -> str:
        """
        Send message to LM Studio and get response.
        
        Args:
            messages: List of message dicts with role and content
            temperature: Temperature for generation
            
        Returns:
            str: Model response
        """
        try:
            url = f"{self.base_url}/chat/completions"
            
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "stream": False,
            }
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=300)
            
            if response.status_code == 200:
                data = response.json()
                return data["choices"][0]["message"]["content"]
            else:
                return f"Error: {response.status_code} - {response.text}"
        
        except Exception as e:
            return f"Error: {str(e)}"
    
    def stream_message(self, messages: List[Dict], temperature: float = 0.7):
        """Stream response from LM Studio."""
        try:
            url = f"{self.base_url}/chat/completions"
            
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "stream": True,
            }
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            }
            
            response = requests.post(url, json=payload, headers=headers, stream=True, timeout=300)
            
            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        line = line.decode('utf-8')
                        if line.startswith("data: "):
                            try:
                                import json
                                data = json.loads(line[6:])
                                if "choices" in data:
                                    delta = data["choices"][0].get("delta", {})
                                    if "content" in delta:
                                        yield delta["content"]
                            except:
                                pass
        
        except Exception as e:
            yield f"Error: {str(e)}"


class OllamaClient:
    """Client for Ollama."""
    
    def __init__(self, host: str = "localhost", port: int = 11434, model: str = ""):
        self.host = host
        self.port = port
        self.model = model
        self.base_url = f"http://{host}:{port}/api"
    
    def send_message(self, messages: List[Dict], temperature: float = 0.7) -> str:
        """
        Send message to Ollama and get response.
        
        Args:
            messages: List of message dicts with role and content
            temperature: Temperature for generation
            
        Returns:
            str: Model response
        """
        try:
            # Convert messages to prompt format
            prompt = ""
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                prompt += f"{role}: {content}\n"
            
            url = f"{self.base_url}/generate"
            
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                }
            }
            
            response = requests.post(url, json=payload, timeout=300)
            
            if response.status_code == 200:
                data = response.json()
                return data.get("response", "")
            else:
                return f"Error: {response.status_code}"
        
        except Exception as e:
            return f"Error: {str(e)}"
    
    def stream_message(self, messages: List[Dict], temperature: float = 0.7):
        """Stream response from Ollama."""
        try:
            prompt = ""
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                prompt += f"{role}: {content}\n"
            
            url = f"{self.base_url}/generate"
            
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": True,
                "options": {
                    "temperature": temperature,
                }
            }
            
            response = requests.post(url, json=payload, stream=True, timeout=300)
            
            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        try:
                            import json
                            data = json.loads(line)
                            if "response" in data:
                                yield data["response"]
                        except:
                            pass
        
        except Exception as e:
            yield f"Error: {str(e)}"


class LocalModelConfig:
    """Manage local model configurations."""
    
    @staticmethod
    def save_local_config(config: Dict) -> bool:
        """Save local model configuration."""
        try:
            import json
            from pathlib import Path
            
            config_path = Path.home() / ".ai_goonbox_local_models.json"
            
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Failed to save config: {e}")
            return False
    
    @staticmethod
    def load_local_config() -> Dict:
        """Load local model configuration."""
        try:
            import json
            from pathlib import Path
            
            config_path = Path.home() / ".ai_goonbox_local_models.json"
            
            if config_path.exists():
                with open(config_path, 'r') as f:
                    return json.load(f)
            
            return {
                "lmstudio": {
                    "enabled": False,
                    "host": "localhost",
                    "port": 8000,
                    "model": ""
                },
                "ollama": {
                    "enabled": False,
                    "host": "localhost",
                    "port": 11434,
                    "model": ""
                }
            }
        except Exception as e:
            print(f"Failed to load config: {e}")
            return {}
