import os
import yaml
from dotenv import load_dotenv
from types import SimpleNamespace

# Load environment variables from .env
load_dotenv()

# Function to load YAML file
def load_yaml(file_name):
    """Load constants from a YAML file."""
    path = os.path.join(os.path.dirname(__file__), "..", "config", file_name)  # Updated path
    with open(path, "r") as file:
        return yaml.safe_load(file)

# Load constants
constants = SimpleNamespace(**load_yaml("constants.yaml"))
sc = SimpleNamespace(**constants.source)


