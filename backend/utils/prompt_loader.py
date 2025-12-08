"""
Prompt loader utility to load prompts from YAML configuration file.
"""

import os
import yaml
from typing import Dict, Any

_prompts_cache: Dict[str, Any] = None

def load_prompts() -> Dict[str, Any]:
    """
    Load prompts from the prompts.yaml configuration file.
    
    Returns:
        Dictionary containing all prompts
    """
    global _prompts_cache
    
    if _prompts_cache is not None:
        return _prompts_cache
    
    # Get the path to prompts.yaml
    current_dir = os.path.dirname(os.path.abspath(__file__))
    prompts_path = os.path.join(current_dir, '..', 'config', 'prompts.yaml')
    
    try:
        with open(prompts_path, 'r', encoding='utf-8') as f:
            _prompts_cache = yaml.safe_load(f)
        print(f"✓ Loaded prompts from {prompts_path}")
        return _prompts_cache
    except FileNotFoundError:
        print(f"Error: prompts.yaml not found at {prompts_path}")
        raise
    except yaml.YAMLError as e:
        print(f"Error parsing prompts.yaml: {e}")
        raise

def get_prompt(agent: str, prompt_type: str = 'system_prompt') -> str:
    """
    Get a specific prompt for an agent.
    
    Args:
        agent: Agent name (e.g., 'supervisor', 'paper', 'slides')
        prompt_type: Type of prompt (e.g., 'system_prompt', 'current_teaching_check')
        
    Returns:
        Prompt string
    """
    prompts = load_prompts()
    
    if agent not in prompts:
        raise ValueError(f"Agent '{agent}' not found in prompts.yaml")
    
    if prompt_type not in prompts[agent]:
        raise ValueError(f"Prompt type '{prompt_type}' not found for agent '{agent}'")
    
    return prompts[agent][prompt_type]

def reload_prompts():
    """
    Reload prompts from YAML file (useful for development).
    """
    global _prompts_cache
    _prompts_cache = None
    return load_prompts()
