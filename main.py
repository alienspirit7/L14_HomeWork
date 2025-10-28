"""
Main Entry Point
Translation Quality Assessment Pipeline

Usage:
    python main.py

Requirements:
    - Google AI API key in .env file or GOOGLE_API_KEY environment variable
    - Install dependencies: pip install -r requirements.txt
"""

import sys
import os
from pipeline import TranslationQualityPipeline
import config


def check_prerequisites():
    """Check if all prerequisites are met."""
    issues = []

    # Check API key
    if not config.GOOGLE_API_KEY:
        issues.append("Missing Google AI API key. Please set GOOGLE_API_KEY in .env file or environment.")

    # Check if output directory can be created
    try:
        os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    except Exception as e:
        issues.append(f"Cannot create output directory: {e}")

    if issues:
        print("Prerequisites check failed:")
        for issue in issues:
            print(f"  ✗ {issue}")
        print("\nPlease fix the issues above before running the pipeline.")
        return False

    print("Prerequisites check passed:")
    print(f"  ✓ API key configured")
    print(f"  ✓ Output directory: {config.OUTPUT_DIR}")
    print(f"  ✓ Translation model: {config.TRANSLATION_MODEL}")
    print(f"  ✓ Embedding model: {config.EMBEDDING_MODEL}")
    return True


def print_configuration():
    """Print current configuration."""
    print("\nConfiguration:")
    print(f"  Number of sentences: {config.NUM_SENTENCES}")
    print(f"  Words per sentence: {config.MIN_WORDS}-{config.MAX_WORDS}")
    print(f"  Agent timeout: {config.AGENT_TIMEOUT}s")
    print(f"  Max retries: {config.MAX_RETRIES}")
    print(f"  Retry delay: {config.RETRY_DELAY}s")
    print()


def main():
    """Main execution function."""
    print("\n" + "=" * 60)
    print("TRANSLATION QUALITY ASSESSMENT PIPELINE")
    print("=" * 60)
    print("\nThis pipeline will:")
    print(f"  1. Generate {config.NUM_SENTENCES} English sentences (10-20 words)")
    print("  2. Translate each through: EN → RU → HE → EN")
    print("  3. Measure semantic drift using cosine distance")
    print("  4. Generate statistics and visualization")
    print(f"\nEstimated time: {config.NUM_SENTENCES * 0.2:.0f}-{config.NUM_SENTENCES * 0.3:.0f} minutes")
    print("=" * 60)

    # Check prerequisites
    if not check_prerequisites():
        sys.exit(1)

    # Print configuration
    print_configuration()

    # Confirm execution
    try:
        response = input("Do you want to proceed? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("Execution cancelled.")
            sys.exit(0)
    except KeyboardInterrupt:
        print("\nExecution cancelled.")
        sys.exit(0)

    # Run pipeline
    try:
        pipeline = TranslationQualityPipeline()
        pipeline.run()

        print("\n" + "=" * 60)
        print("SUCCESS!")
        print("=" * 60)
        print(f"\nResults saved to: {config.OUTPUT_DIR}/")
        print(f"  - {config.RESULTS_FILENAME} (JSON data)")
        print(f"  - {config.PLOT_FILENAME} (Visualization)")
        print("\nThank you for using Translation Quality Assessment Pipeline!")

    except KeyboardInterrupt:
        print("\n\nPipeline interrupted by user.")
        sys.exit(1)

    except Exception as e:
        print(f"\n\nPipeline failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
