import os
import yaml


def load_agents_config(filepath: str = None) -> dict:
    """
    Loads all agent definitions from agents.yaml.

    Returns a dict keyed by agent name, each containing 'role', 'goal', 'backstory'.
    """
    if filepath is None:
        filepath = os.path.join(os.path.dirname(__file__), 'agents.yaml')

    with open(filepath, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    return config


def get_agent_config(name: str, filepath: str = None, **format_kwargs) -> dict:
    """
    Returns the config for a single agent by name.

    Any keyword arguments are used to format the 'goal' string
    (e.g. topic="AI News" fills in {topic}).
    """
    all_configs = load_agents_config(filepath)

    if name not in all_configs:
        available = ', '.join(all_configs.keys())
        raise KeyError(f"Agent '{name}' not found in agents.yaml. Available: {available}")

    agent = all_configs[name]

    # Format the goal if placeholders are present
    if format_kwargs:
        agent['goal'] = agent['goal'].format(**format_kwargs)

    return agent
