import os

model_ = ''
version_ = ''
modelList = []

# When sharing one library across multiple repos, use an env var to enable GUI (avoids duplicate config.py).
# Unset defaults to False (CLI scripts, MindPlus, OpenCat demos, etc.).
# Desktop apps should set PETOI_SHOW_GUI=1 (or true/yes) before starting the Python process.
def _env_truthy(name: str) -> bool:
    v = os.environ.get(name, "").strip().lower()
    return v in ("1", "true", "yes", "on")


SHOW_GUI = _env_truthy("PETOI_SHOW_GUI")
