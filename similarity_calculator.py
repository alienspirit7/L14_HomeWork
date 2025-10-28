"""
Similarity Calculator Module
Calculates cosine distance between sentence embeddings.
"""

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Tuple
import config


class SimilarityCalculator:
    """Calculates semantic similarity between sentences using embeddings."""

    def __init__(self, model_name: str = None):
        """
        Initialize similarity calculator.

        Args:
            model_name: Name of sentence transformer model to use
        """
        self.model_name = model_name or config.EMBEDDING_MODEL
        print(f"Loading embedding model: {self.model_name}...")
        self.model = SentenceTransformer(self.model_name)
        print("Embedding model loaded successfully")

    def calculate_cosine_distance(self,
                                  sentence1: str,
                                  sentence2: str) -> float:
        """
        Calculate cosine distance between two sentences.

        Cosine distance = 1 - cosine similarity
        Range: [0, 2] where 0 = identical, 2 = opposite

        Args:
            sentence1: First sentence
            sentence2: Second sentence

        Returns:
            Cosine distance (float)
        """
        # Generate embeddings
        embedding1 = self.model.encode(sentence1, convert_to_numpy=True)
        embedding2 = self.model.encode(sentence2, convert_to_numpy=True)

        # Reshape for sklearn
        embedding1 = embedding1.reshape(1, -1)
        embedding2 = embedding2.reshape(1, -1)

        # Calculate cosine similarity
        similarity = cosine_similarity(embedding1, embedding2)[0][0]

        # Convert to cosine distance
        distance = 1 - similarity

        return float(distance)

    def calculate_batch_distances(self,
                                  sentences1: List[str],
                                  sentences2: List[str]) -> List[float]:
        """
        Calculate cosine distances for batches of sentence pairs.

        Args:
            sentences1: List of first sentences
            sentences2: List of second sentences (must be same length)

        Returns:
            List of cosine distances

        Raises:
            ValueError: If sentence lists have different lengths
        """
        if len(sentences1) != len(sentences2):
            raise ValueError("Sentence lists must have the same length")

        # Generate all embeddings at once (more efficient)
        embeddings1 = self.model.encode(sentences1, convert_to_numpy=True)
        embeddings2 = self.model.encode(sentences2, convert_to_numpy=True)

        # Calculate pairwise distances
        distances = []
        for emb1, emb2 in zip(embeddings1, embeddings2):
            emb1 = emb1.reshape(1, -1)
            emb2 = emb2.reshape(1, -1)
            similarity = cosine_similarity(emb1, emb2)[0][0]
            distance = 1 - similarity
            distances.append(float(distance))

        return distances

    def get_embedding(self, sentence: str) -> np.ndarray:
        """
        Get embedding vector for a sentence.

        Args:
            sentence: Input sentence

        Returns:
            Numpy array of embedding vector
        """
        return self.model.encode(sentence, convert_to_numpy=True)

    def calculate_statistics(self, distances: List[float]) -> dict:
        """
        Calculate statistics for a list of distances.

        Args:
            distances: List of cosine distances

        Returns:
            Dictionary with statistics:
            {
                'mean': float,
                'variance': float,
                'std': float,
                'min': float,
                'max': float,
                'median': float
            }
        """
        distances_array = np.array(distances)

        stats = {
            'mean': float(np.mean(distances_array)),
            'variance': float(np.var(distances_array)),
            'std': float(np.std(distances_array)),
            'min': float(np.min(distances_array)),
            'max': float(np.max(distances_array)),
            'median': float(np.median(distances_array))
        }

        return stats
