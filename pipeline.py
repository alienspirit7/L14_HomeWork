"""
Main Pipeline Orchestrator
Coordinates the entire translation quality assessment process.
"""

import os
import json
import time
from datetime import datetime
from typing import List, Dict
from tqdm import tqdm

from sentence_generator import SentenceGenerator
from translation_agents import TranslationPipeline
from similarity_calculator import SimilarityCalculator
from agent_wrapper import AgentWrapper, AgentTimeoutError, AgentMaxRetriesError
import config


class TranslationQualityPipeline:
    """Main pipeline orchestrator for translation quality assessment."""

    def __init__(self):
        """Initialize the pipeline with all components."""
        print("=" * 60)
        print("Translation Quality Assessment Pipeline")
        print("=" * 60)

        # Create output directory
        os.makedirs(config.OUTPUT_DIR, exist_ok=True)

        # Initialize components
        print("\nInitializing components...")
        self.sentence_generator = SentenceGenerator()
        self.translation_pipeline = TranslationPipeline()
        self.similarity_calculator = SimilarityCalculator()
        self.agent_wrapper = AgentWrapper()

        # Storage for results
        self.results: List[Dict] = []
        self.start_time = None
        self.end_time = None

    def run(self):
        """Execute the entire pipeline."""
        try:
            self.start_time = datetime.now()

            # Step 1: Generate sentences
            sentences = self._generate_sentences()

            # Step 2: Process each sentence through translation pipeline
            self._process_sentences(sentences)

            # Step 3: Analyze results
            self._analyze_and_visualize()

            self.end_time = datetime.now()
            duration = (self.end_time - self.start_time).total_seconds()

            print(f"\n{'=' * 60}")
            print(f"Pipeline completed successfully in {duration:.2f} seconds")
            print(f"{'=' * 60}")

        except (AgentTimeoutError, AgentMaxRetriesError) as e:
            print(f"\n{'!' * 60}")
            print(f"PIPELINE STOPPED: {str(e)}")
            print(f"{'!' * 60}")
            print(f"\nProcessed {len(self.results)} sentences before failure.")
            if self.results:
                print("Saving partial results...")
                self._save_partial_results()
            raise

        except Exception as e:
            print(f"\n{'!' * 60}")
            print(f"ERROR: {str(e)}")
            print(f"{'!' * 60}")
            raise

    def _generate_sentences(self) -> List[str]:
        """Generate sentences for testing."""
        print(f"\n{'=' * 60}")
        print("Step 1: Generating Sentences")
        print(f"{'=' * 60}")

        sentences = self.sentence_generator.generate_sentences(
            num_sentences=config.NUM_SENTENCES,
            min_words=config.MIN_WORDS,
            max_words=config.MAX_WORDS
        )

        print(f"\nSample sentences:")
        for i, sentence in enumerate(sentences[:3], 1):
            print(f"  {i}. {sentence}")
        print(f"  ... ({len(sentences)} total)")

        return sentences

    def _process_sentences(self, sentences: List[str]):
        """Process all sentences through the translation pipeline."""
        print(f"\n{'=' * 60}")
        print("Step 2: Translation Pipeline Processing")
        print(f"{'=' * 60}")

        for idx, sentence in enumerate(tqdm(sentences, desc="Processing sentences"), 1):
            print(f"\nSentence {idx}/{len(sentences)}")
            print(f"  Original: {sentence[:60]}...")

            start_time = time.time()

            try:
                # Translate through pipeline with retry logic
                russian_text = self._call_agent_with_retry(
                    self.translation_pipeline.agent1.translate,
                    sentence,
                    "EN → RU"
                )

                hebrew_text = self._call_agent_with_retry(
                    self.translation_pipeline.agent2.translate,
                    russian_text,
                    "RU → HE"
                )

                final_text = self._call_agent_with_retry(
                    self.translation_pipeline.agent3.translate,
                    hebrew_text,
                    "HE → EN"
                )

                # Calculate similarity
                cosine_distance = self.similarity_calculator.calculate_cosine_distance(
                    sentence, final_text
                )

                duration = time.time() - start_time

                # Store result
                result = {
                    'index': idx,
                    'original_sentence': sentence,
                    'russian_translation': russian_text,
                    'hebrew_translation': hebrew_text,
                    'final_sentence': final_text,
                    'cosine_distance': cosine_distance,
                    'processing_time': duration,
                    'timestamp': datetime.now().isoformat()
                }

                self.results.append(result)

                print(f"  Final: {final_text[:60]}...")
                print(f"  Cosine distance: {cosine_distance:.4f}")
                print(f"  Time: {duration:.2f}s")

                # Save intermediate results periodically
                if config.SAVE_INTERMEDIATE and idx % 10 == 0:
                    self._save_intermediate_results(idx)

            except (AgentTimeoutError, AgentMaxRetriesError) as e:
                print(f"\n  ✗ Failed: {str(e)}")
                raise

    def _call_agent_with_retry(self, agent_func, text: str, label: str) -> str:
        """
        Call an agent with retry logic.

        Args:
            agent_func: Agent translation function
            text: Text to translate
            label: Label for logging (e.g., "EN → RU")

        Returns:
            Translated text

        Raises:
            AgentTimeoutError: If agent times out
            AgentMaxRetriesError: If max retries exceeded
        """
        start = time.time()
        success, result = self.agent_wrapper.call_with_retry(agent_func, text)
        duration = time.time() - start

        if success:
            print(f"  {label}: ✓ ({duration:.1f}s)")
            return result
        else:
            print(f"  {label}: ✗ ({result})")
            raise Exception(result)

    def _analyze_and_visualize(self):
        """Analyze results and create visualizations."""
        print(f"\n{'=' * 60}")
        print("Step 3: Analysis and Visualization")
        print(f"{'=' * 60}")

        if not self.results:
            print("No results to analyze!")
            return

        # Extract distances
        distances = [r['cosine_distance'] for r in self.results]

        # Calculate statistics
        stats = self.similarity_calculator.calculate_statistics(distances)

        # Print statistics
        print("\nStatistics:")
        print(f"  Average cosine distance: {stats['mean']:.4f}")
        print(f"  Variance: {stats['variance']:.4f}")
        print(f"  Standard deviation: {stats['std']:.4f}")
        print(f"  Min distance: {stats['min']:.4f}")
        print(f"  Max distance: {stats['max']:.4f}")
        print(f"  Median distance: {stats['median']:.4f}")

        # Create visualization
        self._create_plot(distances, stats)

        # Save results
        self._save_results(stats)

    def _create_plot(self, distances: List[float], stats: dict):
        """Create and save distance plot."""
        import matplotlib.pyplot as plt

        plt.figure(figsize=(12, 6))

        # Plot distances
        indices = list(range(1, len(distances) + 1))
        plt.plot(indices, distances, 'b-', alpha=0.6, linewidth=1, label='Cosine Distance')
        plt.scatter(indices, distances, c='blue', s=20, alpha=0.5)

        # Add mean line
        plt.axhline(y=stats['mean'], color='r', linestyle='--',
                   label=f'Mean: {stats["mean"]:.4f}', linewidth=2)

        # Add std deviation band
        plt.fill_between(indices,
                        stats['mean'] - stats['std'],
                        stats['mean'] + stats['std'],
                        alpha=0.2, color='red',
                        label=f'±1 Std Dev: {stats["std"]:.4f}')

        plt.xlabel('Sentence Index', fontsize=12)
        plt.ylabel('Cosine Distance', fontsize=12)
        plt.title('Translation Quality Degradation:\nOriginal vs Final English Sentences (EN→RU→HE→EN)',
                 fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.legend(loc='best')
        plt.tight_layout()

        # Save plot
        plot_path = os.path.join(config.OUTPUT_DIR, config.PLOT_FILENAME)
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        print(f"\nPlot saved to: {plot_path}")

        plt.close()

    def _save_results(self, stats: dict):
        """Save complete results to JSON file."""
        output = {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'total_sentences': len(self.results),
                'start_time': self.start_time.isoformat() if self.start_time else None,
                'end_time': self.end_time.isoformat() if self.end_time else None,
                'duration_seconds': (self.end_time - self.start_time).total_seconds() if self.end_time and self.start_time else None,
                'config': {
                    'num_sentences': config.NUM_SENTENCES,
                    'min_words': config.MIN_WORDS,
                    'max_words': config.MAX_WORDS,
                    'agent_timeout': config.AGENT_TIMEOUT,
                    'max_retries': config.MAX_RETRIES,
                    'embedding_model': config.EMBEDDING_MODEL,
                    'translation_model': config.TRANSLATION_MODEL
                }
            },
            'statistics': stats,
            'sentences': self.results
        }

        results_path = os.path.join(config.OUTPUT_DIR, config.RESULTS_FILENAME)
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        print(f"Results saved to: {results_path}")

    def _save_intermediate_results(self, current_idx: int):
        """Save intermediate results during processing."""
        filename = f"intermediate_results_{current_idx}.json"
        filepath = os.path.join(config.OUTPUT_DIR, filename)

        data = {
            'processed_count': current_idx,
            'timestamp': datetime.now().isoformat(),
            'sentences': self.results
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _save_partial_results(self):
        """Save partial results when pipeline fails."""
        if not self.results:
            return

        distances = [r['cosine_distance'] for r in self.results]
        stats = self.similarity_calculator.calculate_statistics(distances)

        output = {
            'metadata': {
                'status': 'PARTIAL - Pipeline stopped early',
                'timestamp': datetime.now().isoformat(),
                'sentences_processed': len(self.results),
                'sentences_expected': config.NUM_SENTENCES
            },
            'statistics': stats,
            'sentences': self.results
        }

        filename = f"partial_results_{len(self.results)}_sentences.json"
        filepath = os.path.join(config.OUTPUT_DIR, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        print(f"Partial results saved to: {filepath}")
