"""
Configuration settings for the Translation Quality Assessment Pipeline.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Sentence generation settings
NUM_SENTENCES = 5
MIN_WORDS = 10
MAX_WORDS = 20

# Agent settings
AGENT_TIMEOUT = 60  # seconds
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds between retries

# Embedding model
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Output settings
OUTPUT_DIR = "./results"
SAVE_INTERMEDIATE = True
PLOT_FILENAME = "distance_plot.png"
RESULTS_FILENAME = "translation_results.json"

# API Keys (load from environment)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# API Provider Selection
# Options: "gemini" or "anthropic"
API_PROVIDER = os.getenv("API_PROVIDER", "gemini").lower()

# Translation model settings
# Gemini model
GEMINI_MODEL = "gemini-2.0-flash-exp"  # Gemini 2.0 Flash
# Anthropic model
ANTHROPIC_MODEL = "claude-3-5-sonnet-20241022"  # Claude 3.5 Sonnet

# Select model based on provider
TRANSLATION_MODEL = GEMINI_MODEL if API_PROVIDER == "gemini" else ANTHROPIC_MODEL
TEMPERATURE = 0.0  # For deterministic translations

# Wait time between sentences (in seconds)
WAIT_TIME_BETWEEN_SENTENCES = 60  # 1 minute wait between sentences
