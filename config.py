import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for Ray execution environments."""
    
    @staticmethod
    def get_local_config() -> Dict[str, Any]:
        """Get configuration for local Ray execution."""
        return {
            'address': 'local',
            'namespace': 'local',
            'runtime_env': {
                'working_dir': '.',
                'py_modules': ['jobs']
            }
        }
    
    @staticmethod
    def get_kubernetes_config() -> Dict[str, Any]:
        """Get configuration for Kubernetes Ray execution."""
        return {
            'address': os.getenv('RAY_KUBERNETES_ADDRESS', 'kubernetes://ray-cluster'),
            'namespace': os.getenv('RAY_KUBERNETES_NAMESPACE', 'ray'),
            'runtime_env': {
                'working_dir': '.',
                'py_modules': ['jobs'],
                'container': {
                    'image': os.getenv('RAY_IMAGE', 'rayproject/ray:latest'),
                    'name': 'ray-worker'
                }
            }
        } 