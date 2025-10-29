"""
Translation Agents Module
Implements three translation agents: EN→RU, RU→HE, HE→EN
Supports both Gemini and Anthropic APIs
"""

import google.generativeai as genai
from anthropic import Anthropic
from typing import Optional
import config


class TranslationAgent:
    """Base class for translation agents."""

    def __init__(self,
                 source_lang: str,
                 target_lang: str,
                 api_key: str = None,
                 model: str = None,
                 provider: str = None):
        """
        Initialize translation agent.

        Args:
            source_lang: Source language code/name
            target_lang: Target language code/name
            api_key: API key for translation service
            model: Model to use for translation
            provider: API provider ("gemini" or "anthropic")
        """
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.provider = provider or config.API_PROVIDER
        self.model_name = model or config.TRANSLATION_MODEL

        # Get appropriate API key based on provider
        if self.provider == "gemini":
            self.api_key = api_key or config.GOOGLE_API_KEY
        elif self.provider == "anthropic":
            self.api_key = api_key or config.ANTHROPIC_API_KEY
        else:
            raise ValueError(f"Unsupported provider: {self.provider}. Choose 'gemini' or 'anthropic'")

        if not self.api_key:
            raise ValueError(f"API key required for {self.__class__.__name__} with provider {self.provider}")

        # Initialize the appropriate API client
        if self.provider == "gemini":
            # Configure Gemini API
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config={
                    "temperature": config.TEMPERATURE,
                    "max_output_tokens": 500,
                }
            )
        elif self.provider == "anthropic":
            # Initialize Anthropic client
            self.client = Anthropic(api_key=self.api_key)

    def translate(self, text: str) -> str:
        """
        Translate text from source to target language.

        Args:
            text: Text to translate

        Returns:
            Translated text

        Raises:
            Exception: If translation fails
        """
        prompt = self._get_translation_prompt(text)

        try:
            if self.provider == "gemini":
                response = self.model.generate_content(prompt)
                translation = response.text.strip()
            elif self.provider == "anthropic":
                response = self.client.messages.create(
                    model=self.model_name,
                    max_tokens=500,
                    temperature=config.TEMPERATURE,
                    messages=[{
                        "role": "user",
                        "content": prompt
                    }]
                )
                translation = response.content[0].text.strip()

            # Remove any explanations or additional text
            # Sometimes models add quotes or explanations
            translation = self._clean_translation(translation)

            return translation

        except Exception as e:
            raise Exception(f"Translation failed ({self.source_lang}→{self.target_lang}): {str(e)}")

    def _get_translation_prompt(self, text: str) -> str:
        """Get complete prompt for translation."""
        return f"""You are a professional translator specializing in {self.source_lang} to {self.target_lang} translation.
Provide accurate, natural translations that preserve the meaning and tone of the original text.
Return ONLY the translated text without any explanations, quotes, or additional commentary.

Translate the following {self.source_lang} text to {self.target_lang}:

{text}"""

    def _clean_translation(self, translation: str) -> str:
        """Clean up translation output."""
        # Remove surrounding quotes if present
        if translation.startswith('"') and translation.endswith('"'):
            translation = translation[1:-1]
        elif translation.startswith("'") and translation.endswith("'"):
            translation = translation[1:-1]

        # Remove common prefixes that models sometimes add
        prefixes_to_remove = [
            "Translation: ",
            "Here is the translation: ",
            "The translation is: ",
            f"{self.target_lang}: ",
        ]

        for prefix in prefixes_to_remove:
            if translation.startswith(prefix):
                translation = translation[len(prefix):].strip()

        return translation.strip()


class EnglishToRussianAgent(TranslationAgent):
    """Agent for translating English to Russian."""

    def __init__(self, api_key: str = None, model: str = None, provider: str = None):
        """Initialize English to Russian translator."""
        super().__init__(
            source_lang="English",
            target_lang="Russian",
            api_key=api_key,
            model=model,
            provider=provider
        )


class RussianToHebrewAgent(TranslationAgent):
    """Agent for translating Russian to Hebrew."""

    def __init__(self, api_key: str = None, model: str = None, provider: str = None):
        """Initialize Russian to Hebrew translator."""
        super().__init__(
            source_lang="Russian",
            target_lang="Hebrew",
            api_key=api_key,
            model=model,
            provider=provider
        )


class HebrewToEnglishAgent(TranslationAgent):
    """Agent for translating Hebrew to English."""

    def __init__(self, api_key: str = None, model: str = None, provider: str = None):
        """Initialize Hebrew to English translator."""
        super().__init__(
            source_lang="Hebrew",
            target_lang="English",
            api_key=api_key,
            model=model,
            provider=provider
        )


class TranslationPipeline:
    """Manages the three-agent translation pipeline."""

    def __init__(self,
                 api_key: str = None,
                 model: str = None,
                 provider: str = None):
        """
        Initialize translation pipeline with all three agents.

        Args:
            api_key: API key for translation service
            model: Model to use for all agents
            provider: API provider ("gemini" or "anthropic")
        """
        self.provider = provider or config.API_PROVIDER
        self.agent1 = EnglishToRussianAgent(api_key=api_key, model=model, provider=self.provider)
        self.agent2 = RussianToHebrewAgent(api_key=api_key, model=model, provider=self.provider)
        self.agent3 = HebrewToEnglishAgent(api_key=api_key, model=model, provider=self.provider)

    def translate_full_pipeline(self, english_text: str) -> dict:
        """
        Translate through entire pipeline: EN→RU→HE→EN

        Args:
            english_text: Original English text

        Returns:
            Dictionary with all intermediate translations:
            {
                'original': str,
                'russian': str,
                'hebrew': str,
                'final': str
            }

        Raises:
            Exception: If any translation step fails
        """
        results = {
            'original': english_text,
            'russian': None,
            'hebrew': None,
            'final': None
        }

        # Step 1: English → Russian
        results['russian'] = self.agent1.translate(english_text)

        # Step 2: Russian → Hebrew
        results['hebrew'] = self.agent2.translate(results['russian'])

        # Step 3: Hebrew → English
        results['final'] = self.agent3.translate(results['hebrew'])

        return results
