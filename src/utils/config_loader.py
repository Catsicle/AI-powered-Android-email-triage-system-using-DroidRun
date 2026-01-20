"""Configuration loader utilities"""

from pathlib import Path
from droidrun import DroidrunConfig
from llama_index.llms.google_genai import GoogleGenAI


def get_droidrun_config(max_steps: int = 20, config_path: str = "config.yaml") -> DroidrunConfig:
    """
    Load DroidRun configuration from YAML file.
    
    Args:
        max_steps: Maximum number of agent steps
        config_path: Path to config.yaml file (can be relative or absolute)
        
    Returns:
        Configured DroidrunConfig instance
    """
    # Ensure config_path is absolute - resolve relative to project root if needed
    config_file = Path(config_path)
    if not config_file.is_absolute():
        # If relative, resolve from project root
        project_root = Path(__file__).parent.parent.parent
        config_file = project_root / config_path
    
    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_file}")
    
    config = DroidrunConfig.from_yaml(str(config_file))
    config.agent.max_steps = max_steps
    config.tracing.enabled = True
    config.agent.reasoning = False
    return config


def get_llm(model: str = "models/gemini-2.5-flash") -> GoogleGenAI:
    """
    Get Gemini LLM instance for DroidRun agents.
    
    Args:
        model: Gemini model name (default: gemini-2.5-flash for cost efficiency)
        
    Returns:
        Configured GoogleGenAI LLM instance
    """
    return GoogleGenAI(model=model)
