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

# Translation model settings
TRANSLATION_MODEL = "gemini-2.0-flash-exp"  # Gemini 2.0 Flash
TEMPERATURE = 0.0  # For deterministic translations
