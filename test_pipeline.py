"""
Test Script for Translation Quality Assessment Pipeline

This script runs a quick test with just 2 sentences to verify setup.
Useful for testing before running the full pipeline.

Usage:
    python test_pipeline.py
"""

import os
import sys

# Temporarily modify config for testing
import config
original_num_sentences = config.NUM_SENTENCES
config.NUM_SENTENCES = 2  # Test with just 2 sentences

from sentence_generator import SentenceGenerator
from translation_agents import TranslationPipeline
from similarity_calculator import SimilarityCalculator
from agent_wrapper import AgentWrapper


def test_components():
    """Test each component individually."""
    print("=" * 60)
    print("COMPONENT TESTS")
    print("=" * 60)

    # Test 1: API Key
    print("\n[Test 1] Checking API Key...")
    if config.GOOGLE_API_KEY:
        print("  ✓ Google API key found")
    else:
        print("  ✗ API key missing!")
        print("  Please set GOOGLE_API_KEY in .env file")
        return False

    # Test 2: Sentence Generator
    print("\n[Test 2] Testing Sentence Generator...")
    try:
        generator = SentenceGenerator()
        test_sentences = generator.generate_sentences(num_sentences=2, min_words=10, max_words=15)
        print(f"  ✓ Generated {len(test_sentences)} sentences")
        print(f"    Example: {test_sentences[0]}")
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False

    # Test 3: Translation Agents
    print("\n[Test 3] Testing Translation Agents...")
    try:
        pipeline = TranslationPipeline()
        test_text = "The weather is beautiful today."

        # Test EN → RU
        russian = pipeline.agent1.translate(test_text)
        print(f"  ✓ EN → RU: {russian}")

        # Test RU → HE
        hebrew = pipeline.agent2.translate(russian)
        print(f"  ✓ RU → HE: {hebrew}")

        # Test HE → EN
        final = pipeline.agent3.translate(hebrew)
        print(f"  ✓ HE → EN: {final}")

    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False

    # Test 4: Similarity Calculator
    print("\n[Test 4] Testing Similarity Calculator...")
    try:
        calculator = SimilarityCalculator()
        distance = calculator.calculate_cosine_distance(test_text, final)
        print(f"  ✓ Cosine distance calculated: {distance:.4f}")
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False

    # Test 5: Agent Wrapper
    print("\n[Test 5] Testing Agent Wrapper with Retry...")
    try:
        wrapper = AgentWrapper(max_retries=2, timeout=30)
        success, result = wrapper.call_with_retry(
            pipeline.agent1.translate,
            "This is a test sentence."
        )
        if success:
            print(f"  ✓ Agent wrapper works: {result}")
        else:
            print(f"  ✗ Agent wrapper failed: {result}")
            return False
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED!")
    print("=" * 60)
    return True


def run_mini_pipeline():
    """Run a mini version of the full pipeline with 2 sentences."""
    print("\n" + "=" * 60)
    print(f"MINI PIPELINE TEST ({config.NUM_SENTENCES} sentences)")
    print("=" * 60)

    try:
        from pipeline import TranslationQualityPipeline

        print("\nRunning mini pipeline...")
        print("This will take less than a minute...\n")

        pipeline = TranslationQualityPipeline()
        pipeline.run()

        print("\n" + "=" * 60)
        print("MINI PIPELINE COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print(f"\nCheck the results in: {config.OUTPUT_DIR}/")
        print("\nYou can now run the full pipeline with:")
        print("  python main.py")

        return True

    except Exception as e:
        print(f"\n✗ Mini pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test execution."""
    print("\n" + "=" * 60)
    print("TRANSLATION PIPELINE TEST SUITE")
    print("=" * 60)
    print("\nThis script will test all components before running")
    print(f"a mini pipeline with just {config.NUM_SENTENCES} sentences.\n")

    # Run component tests
    if not test_components():
        print("\n⚠ Component tests failed. Please fix the issues above.")
        sys.exit(1)

    # Ask if user wants to run mini pipeline
    print("\n" + "=" * 60)
    try:
        response = input(f"\nRun mini pipeline with {config.NUM_SENTENCES} sentences? (yes/no): ").strip().lower()
        if response in ['yes', 'y']:
            if run_mini_pipeline():
                sys.exit(0)
            else:
                sys.exit(1)
        else:
            print("\nMini pipeline skipped.")
            print("All component tests passed. You're ready to run:")
            print("  python main.py")
            sys.exit(0)
    except KeyboardInterrupt:
        print("\n\nTest cancelled.")
        sys.exit(0)


if __name__ == "__main__":
    main()
