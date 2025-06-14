# apps/utils/feature_flags.py

import os

def ai_enabled():
    """
    Returns True if AI features are enabled via environment variable.
    """
    return os.getenv("ENABLE_AI", "false").lower() == "true"
