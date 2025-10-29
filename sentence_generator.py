"""
Sentence Generator Module
Generates English sentences for translation quality assessment.
Supports both Gemini and Anthropic APIs.
"""

import random
from typing import List
import google.generativeai as genai
from anthropic import Anthropic
import config


class SentenceGenerator:
    """Generates diverse English sentences of specified word length."""

    def __init__(self, api_key: str = None, provider: str = None):
        """
        Initialize the sentence generator.

        Args:
            api_key: API key (uses config if not provided)
            provider: API provider ("gemini" or "anthropic")
        """
        self.provider = provider or config.API_PROVIDER

        # Get appropriate API key based on provider
        if self.provider == "gemini":
            self.api_key = api_key or config.GOOGLE_API_KEY
        elif self.provider == "anthropic":
            self.api_key = api_key or config.ANTHROPIC_API_KEY
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

        if not self.api_key:
            raise ValueError(f"API key is required for provider {self.provider}")

        # Initialize the appropriate API client
        if self.provider == "gemini":
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(
                model_name=config.TRANSLATION_MODEL,
                generation_config={
                    "temperature": 0.7,  # Some creativity for diversity
                    "max_output_tokens": 4000,
                }
            )
        elif self.provider == "anthropic":
            self.client = Anthropic(api_key=self.api_key)

    def generate_sentences(self,
                          num_sentences: int = 100,
                          min_words: int = 10,
                          max_words: int = 20) -> List[str]:
        """
        Generate diverse English sentences.

        Args:
            num_sentences: Number of sentences to generate
            min_words: Minimum words per sentence
            max_words: Maximum words per sentence

        Returns:
            List of generated sentences
        """
        print(f"Generating {num_sentences} sentences ({min_words}-{max_words} words)...")

        prompt = f"""Generate {num_sentences} diverse, grammatically correct English sentences.
Each sentence should be between {min_words} and {max_words} words long.
The sentences should cover various topics: technology, nature, daily life, science, culture, history, etc.
Make them interesting and varied in structure.

Return ONLY the sentences, one per line, numbered from 1 to {num_sentences}.
Format: "1. [sentence]" on each line."""

        try:
            if self.provider == "gemini":
                response = self.model.generate_content(prompt)
                content = response.text.strip()
            elif self.provider == "anthropic":
                response = self.client.messages.create(
                    model=config.TRANSLATION_MODEL,
                    max_tokens=4000,
                    temperature=0.7,
                    messages=[{
                        "role": "user",
                        "content": prompt
                    }]
                )
                content = response.content[0].text.strip()

            # Parse sentences from numbered list
            sentences = []
            for line in content.split('\n'):
                line = line.strip()
                if line and any(line.startswith(f"{i}.") for i in range(1, num_sentences + 1)):
                    # Remove the number prefix
                    sentence = line.split('.', 1)[1].strip()
                    # Validate word count
                    word_count = len(sentence.split())
                    if min_words <= word_count <= max_words:
                        sentences.append(sentence)

            # If we don't have enough sentences, generate more
            if len(sentences) < num_sentences:
                print(f"Warning: Only generated {len(sentences)} valid sentences. Generating more...")
                additional_needed = num_sentences - len(sentences)
                additional_sentences = self._generate_additional_sentences(
                    additional_needed, min_words, max_words
                )
                sentences.extend(additional_sentences)

            # Take exactly the number requested
            sentences = sentences[:num_sentences]

            print(f"Successfully generated {len(sentences)} sentences")
            return sentences

        except Exception as e:
            print(f"Error generating sentences: {e}")
            # Fallback to template-based generation
            print("Falling back to template-based generation...")
            return self._generate_template_sentences(num_sentences, min_words, max_words)

    def _generate_additional_sentences(self, count: int, min_words: int, max_words: int) -> List[str]:
        """Generate additional sentences if needed."""
        prompt = f"""Generate {count} more diverse, grammatically correct English sentences.
Each sentence should be between {min_words} and {max_words} words long.
Return ONLY the sentences, one per line, without numbering."""

        try:
            if self.provider == "gemini":
                # Create a new model instance with higher temperature for more diversity
                model = genai.GenerativeModel(
                    model_name=config.TRANSLATION_MODEL,
                    generation_config={
                        "temperature": 0.8,
                        "max_output_tokens": 2000,
                    }
                )
                response = model.generate_content(prompt)
                content = response.text.strip()
            elif self.provider == "anthropic":
                response = self.client.messages.create(
                    model=config.TRANSLATION_MODEL,
                    max_tokens=2000,
                    temperature=0.8,
                    messages=[{
                        "role": "user",
                        "content": prompt
                    }]
                )
                content = response.content[0].text.strip()

            sentences = [s.strip() for s in content.split('\n') if s.strip()]

            # Validate word count
            valid_sentences = []
            for sentence in sentences:
                word_count = len(sentence.split())
                if min_words <= word_count <= max_words:
                    valid_sentences.append(sentence)

            return valid_sentences

        except Exception as e:
            print(f"Error generating additional sentences: {e}")
            return []

    def _generate_template_sentences(self, count: int, min_words: int, max_words: int) -> List[str]:
        """Fallback method using templates."""
        templates = [
            "The {adj} {noun} {verb} across the {place} while the {weather} {verb2}.",
            "Scientists have discovered that {noun} can {verb} in unexpected ways when exposed to {condition}.",
            "Every morning, the {profession} would {verb} before heading to the {place} to start work.",
            "In the distant {place}, ancient {noun} still {verb} beneath the {adj} {noun2}.",
            "Technology has revolutionized how we {verb} and interact with {noun} in modern society.",
            "The {adj} landscape stretched endlessly, with {noun} visible in every direction we looked.",
            "Children often {verb} when they encounter {noun} for the first time in their lives.",
            "Historical records suggest that {profession} used to {verb} differently than they do today.",
            "The {weather} conditions made it difficult to {verb} safely through the {place} yesterday.",
            "Researchers believe that understanding {noun} could help us {verb} more effectively in the future."
        ]

        words = {
            "adj": ["beautiful", "ancient", "modern", "mysterious", "vibrant", "quiet", "massive", "tiny"],
            "noun": ["mountain", "river", "city", "technology", "culture", "tradition", "discovery", "innovation"],
            "verb": ["flows", "develops", "transforms", "appears", "grows", "changes", "evolves", "operates"],
            "verb2": ["continues", "persists", "remains", "develops"],
            "place": ["valley", "marketplace", "forest", "ocean", "countryside", "metropolis"],
            "weather": ["sun", "wind", "rain", "storm"],
            "condition": ["sunlight", "pressure", "temperature", "darkness"],
            "profession": ["teacher", "doctor", "engineer", "artist", "scientist"],
            "noun2": ["horizon", "surface", "canopy", "structure"]
        }

        sentences = []
        for i in range(count):
            template = random.choice(templates)
            sentence = template
            for key, values in words.items():
                if f"{{{key}}}" in sentence:
                    sentence = sentence.replace(f"{{{key}}}", random.choice(values))
            sentences.append(sentence)

        return sentences
