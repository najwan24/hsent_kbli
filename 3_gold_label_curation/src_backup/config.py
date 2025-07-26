"""
ACSES Pilot Study - Core Configuration
Centralized configuration management for the entire pipeline
"""
import os
from pathlib import Path
from typing import Dict, Optional
from dataclasses import dataclass

@dataclass
class ModelConfig:
    """Configuration for individual Gemini models"""
    name: str
    rpm_limit: int
    temperature: float = 0.7
    max_retries: int = 3
    
    @property
    def rate_delay(self) -> float:
        """Calculate minimum delay between requests"""
        return (60.0 / self.rpm_limit) * 1.1  # 10% buffer

@dataclass
class PipelineConfig:
    """Main pipeline configuration"""
    n_runs: int = 3
    retry_delay: int = 2
    temperature: float = 0.7
    max_output_tokens: int = 500
    
    def __post_init__(self):
        """Initialize model configurations"""
        self.models = {
            "gemini-1.5-flash-latest": ModelConfig("models/gemini-1.5-flash-latest", 15),
            "gemini-1.5-pro-latest": ModelConfig("models/gemini-1.5-pro-latest", 2),
            "gemini-2.5-flash-lite": ModelConfig("models/gemini-2.5-flash-lite", 15),
        }
    
    def get_model_config(self, model_name: str) -> ModelConfig:
        """Get configuration for a specific model"""
        # Handle both short and full model names
        if not model_name.startswith("models/"):
            model_name = f"models/{model_name}"
        
        return self.models.get(model_name, ModelConfig(model_name, 15))

class ProjectPaths:
    """Centralized path management"""
    
    def __init__(self, project_root: Optional[Path] = None):
        # Auto-detect project root from current file location
        if project_root is None:
            current_file = Path(__file__).resolve()
            # Navigate up to find the project root (contains data/, src/, etc.)
            project_root = current_file.parent.parent
        
        self.root = Path(project_root)
        self.src = self.root / "src"
        self.scripts = self.root / "scripts"
        self.data = self.root / "data"
        self.data_input = self.data / "input"
        self.data_output = self.data / "output"
        self.prompts = self.root / "prompts"
        self.notebooks = self.root / "notebooks"
        self.docs = self.root / "docs"
        self.tests = self.root / "tests"
    
    # Input file paths
    @property
    def kbli_codebook(self) -> Path:
        return self.data_input / "kbli_codebook.csv"
    
    @property
    def mini_test(self) -> Path:
        return self.data_input / "mini_test.csv"
    
    @property
    def mini_test_with_ids(self) -> Path:
        return self.data_input / "mini_test_with_ids.csv"
    
    @property
    def master_prompt(self) -> Path:
        return self.prompts / "master_prompt.txt"
    
    # Output file paths
    @property
    def hierarchical_codebook(self) -> Path:
        return self.data_output / "kbli_codebook_hierarchical.csv"
    
    def pilot_results_path(self, model_name: str) -> Path:
        """Generate pilot results path for a specific model"""
        safe_model_name = model_name.replace("models/", "").replace("-", "_").replace(".", "_")
        return self.data_output / f"pilot_results_{safe_model_name}.jsonl"
    
    def ensure_directories(self):
        """Create all necessary directories"""
        directories = [
            self.data_input, self.data_output, self.prompts, 
            self.notebooks, self.docs, self.tests
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

# Global configuration instances
CONFIG = PipelineConfig()
PATHS = ProjectPaths()

# Environment variable helpers
def load_api_key() -> str:
    """Load Gemini API key from environment"""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY environment variable not found. "
            "Please set it before running the pipeline."
        )
    return api_key

def load_env_file() -> bool:
    """Load .env file if present"""
    try:
        from dotenv import load_dotenv
        dotenv_path = PATHS.root / '.env'
        if dotenv_path.exists():
            load_dotenv(dotenv_path)
            return True
    except ImportError:
        pass
    return False
