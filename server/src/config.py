import os
from kubernetes import config
import yaml

def load_external_config(filename="external_config.yaml"):
    """Load configurations from an external YAML file."""
    try:
        with open(filename, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print("No external configuration file found.")
        return {}

def load_environment_config():
    """Load configurations from environment variables."""
    return {
        'HTML_DIR': os.environ.get('HTML_DIR'),
        # Add more environment variable loads here
    }

def load_kubernetes_config():
    """Load Kubernetes configurations."""
    try:
        config.load_incluster_config()
    except config.ConfigException:
        try:
            config.load_kube_config()
        except:
            print("Could not load Kubernetes config.")

def load_all_configs():
    """Load all configurations."""
    external_config = load_external_config()
    env_config = load_environment_config()
    load_kubernetes_config()

    final_config = {}
    final_config.update(external_config)  # Lowest priority
    final_config.update(env_config)  # Higher priority

    return final_config

all_configs = load_all_configs()