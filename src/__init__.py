from pathlib import Path

# Classic global variables
PROJECT_PATH = Path(__file__).parents[1]
SOURCE_PATH = Path(__file__).parents[0]
ENV_PATH = PROJECT_PATH / ".env"

# Global variables for the project
TEMPLATES_PATH = SOURCE_PATH / "templates"
