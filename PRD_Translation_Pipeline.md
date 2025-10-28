# Product Requirements Document: Multi-Agent Translation Quality Assessment Pipeline

## 1. Overview

A system that evaluates translation quality degradation through sequential multi-language translation. The system processes English sentences through a chain of three translation agents (English → Russian → Hebrew → English) and measures semantic drift using vector similarity metrics.

## 2. Objectives

- Quantify semantic degradation in sequential machine translation
- Identify patterns in translation quality loss across language pairs
- Provide statistical analysis and visualization of translation fidelity
- Implement robust error handling for agent failures

## 3. Functional Requirements

### 3.1 Sentence Generation
- **FR-1**: System shall generate 100 unique English sentences
- **FR-2**: Each sentence shall contain 10-20 words
- **FR-3**: Sentences should be grammatically correct and semantically diverse

### 3.2 Translation Pipeline
- **FR-4**: Agent 1 shall translate English text to Russian
- **FR-5**: Agent 2 shall translate Russian text to Hebrew
- **FR-6**: Agent 3 shall translate Hebrew text to English
- **FR-7**: System shall process all 100 sentences sequentially through the pipeline
- **FR-8**: System shall preserve sentence index throughout the pipeline

### 3.3 Similarity Measurement
- **FR-9**: System shall compute vector embeddings for both original and final English sentences
- **FR-10**: System shall calculate cosine distance between embedding vectors
- **FR-11**: System shall store the following for each sentence:
  - Sentence index (1-100)
  - Original English sentence
  - Final English sentence (after triple translation)
  - Cosine distance value

### 3.4 Statistical Analysis
- **FR-12**: System shall calculate average cosine distance across all 100 sentences
- **FR-13**: System shall calculate variance of cosine distances
- **FR-14**: System shall generate a line/scatter plot with:
  - X-axis: Sentence index (1-100)
  - Y-axis: Cosine distance
  - Title and axis labels

### 3.5 Error Handling
- **FR-15**: System shall implement timeout mechanism for each agent call
- **FR-16**: System shall implement retry mechanism with configurable max attempts
- **FR-17**: System shall terminate process if agent exceeds timeout threshold
- **FR-18**: System shall terminate process if agent exceeds maximum retry attempts
- **FR-19**: System shall log all errors and failures with context

## 4. Non-Functional Requirements

### 4.1 Performance
- **NFR-1**: Each agent call timeout: configurable (suggested: 30-60 seconds)
- **NFR-2**: Maximum retry attempts per agent: configurable (suggested: 3 attempts)
- **NFR-3**: Total pipeline execution time: < 30 minutes for 100 sentences

### 4.2 Reliability
- **NFR-4**: System shall gracefully handle agent failures without data loss
- **NFR-5**: System shall save intermediate results to prevent data loss on crash

### 4.3 Maintainability
- **NFR-6**: Code shall follow PEP 8 style guidelines (if Python)
- **NFR-7**: All functions shall include docstrings
- **NFR-8**: Configuration parameters shall be externalized

### 4.4 Usability
- **NFR-9**: System shall provide progress indicators during execution
- **NFR-10**: Output visualization shall be clear and professionally formatted
- **NFR-11**: Results shall be saved to file for later analysis

## 5. Technical Specifications

### 5.1 System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Main Controller                         │
│  - Orchestrates pipeline                                 │
│  - Manages error handling                                │
│  - Collects results                                      │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│              Sentence Generator                          │
│  - Generates 100 English sentences (10-20 words)         │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│              Translation Pipeline                        │
│  ┌─────────────────────────────────────────────────┐    │
│  │  Agent 1: EN → RU Translator                    │    │
│  │  - Input: English text                          │    │
│  │  - Output: Russian text                         │    │
│  └─────────────────────────────────────────────────┘    │
│                          │                               │
│                          ▼                               │
│  ┌─────────────────────────────────────────────────┐    │
│  │  Agent 2: RU → HE Translator                    │    │
│  │  - Input: Russian text                          │    │
│  │  - Output: Hebrew text                          │    │
│  └─────────────────────────────────────────────────┘    │
│                          │                               │
│                          ▼                               │
│  ┌─────────────────────────────────────────────────┐    │
│  │  Agent 3: HE → EN Translator                    │    │
│  │  - Input: Hebrew text                           │    │
│  │  - Output: English text                         │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│           Similarity Calculator                          │
│  - Generates embeddings using sentence transformer       │
│  - Computes cosine distance                              │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│          Results Analyzer & Visualizer                   │
│  - Calculates statistics (mean, variance)                │
│  - Generates plots                                       │
│  - Saves results to file                                 │
└─────────────────────────────────────────────────────────┘
```

### 5.2 Data Structures

#### Translation Result
```python
{
    "index": int,                    # 1-100
    "original_sentence": str,        # Original English
    "russian_translation": str,      # After Agent 1
    "hebrew_translation": str,       # After Agent 2
    "final_sentence": str,           # After Agent 3
    "cosine_distance": float,        # 0.0 to 2.0
    "timestamp": datetime
}
```

#### Agent Response
```python
{
    "success": bool,
    "translation": str,
    "attempts": int,
    "duration": float,
    "error": str or None
}
```

### 5.3 Agent Specifications

#### Agent Interface
Each agent must implement:
- **Input**: Source text (string)
- **Output**: Translated text (string)
- **Timeout**: Configurable per-call timeout
- **Retry Logic**: Automatic retry on failure
- **Error Reporting**: Detailed error messages

#### Agent 1: English → Russian
- **Model**: Professional translation model or API
- **Language Pair**: en → ru
- **Specialty**: Technical and general text

#### Agent 2: Russian → Hebrew
- **Model**: Professional translation model or API
- **Language Pair**: ru → he
- **Specialty**: Technical and general text

#### Agent 3: Hebrew → English
- **Model**: Professional translation model or API
- **Language Pair**: he → en
- **Specialty**: Technical and general text

### 5.4 Configuration Parameters

```python
CONFIG = {
    "num_sentences": 100,
    "min_words": 10,
    "max_words": 20,
    "agent_timeout": 60,          # seconds
    "max_retries": 3,
    "retry_delay": 2,             # seconds between retries
    "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
    "output_dir": "./results",
    "save_intermediate": True
}
```

### 5.5 Technology Stack

**Recommended Technologies:**
- **Language**: Python 3.8+
- **Translation Agents**: OpenAI API, Anthropic Claude, or Google Translate API
- **Embeddings**: sentence-transformers library
- **Similarity**: scikit-learn (cosine_similarity) or NumPy
- **Visualization**: matplotlib or plotly
- **Data Storage**: JSON or CSV for results
- **Progress Tracking**: tqdm library

## 6. Detailed Workflow

### 6.1 Main Process Flow

1. **Initialize System**
   - Load configuration
   - Validate agent connections
   - Create output directory

2. **Generate Sentences**
   - Generate 100 unique English sentences (10-20 words)
   - Validate sentence quality

3. **For Each Sentence (1-100)**
   - Log progress (sentence X/100)
   - Call Agent 1 (EN → RU) with retry/timeout
   - If failure: Log error and terminate
   - Call Agent 2 (RU → HE) with retry/timeout
   - If failure: Log error and terminate
   - Call Agent 3 (HE → EN) with retry/timeout
   - If failure: Log error and terminate
   - Calculate cosine distance
   - Save result to collection
   - Optional: Save intermediate checkpoint

4. **Analyze Results**
   - Calculate mean distance
   - Calculate variance
   - Generate visualization
   - Save all results to file

5. **Output Final Report**
   - Display statistics
   - Show/save plot
   - Provide summary

### 6.2 Error Handling Strategy

```python
def call_agent_with_retry(agent, text, max_retries, timeout):
    """
    Calls agent with retry logic and timeout.

    Returns:
        - (True, translated_text) on success
        - (False, error_message) on failure after all retries
    """
    for attempt in range(1, max_retries + 1):
        try:
            result = agent.translate(text, timeout=timeout)
            return (True, result)
        except TimeoutError:
            if attempt == max_retries:
                return (False, f"Timeout after {max_retries} attempts")
            wait(retry_delay)
        except Exception as e:
            if attempt == max_retries:
                return (False, f"Error: {str(e)}")
            wait(retry_delay)
```

## 7. Success Metrics

### 7.1 Functional Success
- All 100 sentences processed successfully
- Valid cosine distance calculated for each sentence
- Statistics computed correctly
- Visualization generated and saved

### 7.2 Quality Metrics
- Average cosine distance: Expected range 0.1 - 0.8
- Variance: Should indicate consistency of degradation
- Process completion rate: 100% of sentences

### 7.3 Performance Metrics
- Total execution time < 30 minutes
- Agent timeout occurrences: < 5%
- Retry success rate: > 90%

## 8. Output Specifications

### 8.1 Console Output
```
Translation Quality Assessment Pipeline
========================================
Generating 100 sentences...
Processing sentence 1/100...
  EN → RU: ✓ (0.8s)
  RU → HE: ✓ (1.2s)
  HE → EN: ✓ (0.9s)
  Cosine distance: 0.234

Processing sentence 2/100...
...

Results:
--------
Average cosine distance: 0.312
Variance: 0.045
Plot saved to: ./results/distance_plot.png
Full results saved to: ./results/translation_results.json
```

### 8.2 Visualization
- **Plot Type**: Line plot with scatter points
- **X-axis**: Sentence Index (1-100)
- **Y-axis**: Cosine Distance (0.0 - 2.0)
- **Title**: "Translation Quality Degradation: Original vs Final English Sentences"
- **Grid**: Enabled
- **Format**: PNG/PDF
- **Size**: 10x6 inches

### 8.3 Results File (JSON)
```json
{
    "metadata": {
        "timestamp": "2025-10-28T10:30:00Z",
        "total_sentences": 100,
        "config": {...}
    },
    "statistics": {
        "average_distance": 0.312,
        "variance": 0.045,
        "min_distance": 0.089,
        "max_distance": 0.678
    },
    "sentences": [
        {
            "index": 1,
            "original_sentence": "The quick brown fox...",
            "final_sentence": "The fast brown fox...",
            "cosine_distance": 0.234,
            "intermediate_translations": {
                "russian": "Быстрая коричневая лиса...",
                "hebrew": "השועל החום המהיר..."
            }
        },
        ...
    ]
}
```

## 9. Out of Scope

The following items are explicitly out of scope for this version:
- Real-time translation monitoring UI
- Multi-threaded parallel processing
- Support for additional language pairs
- Quality assessment beyond cosine distance
- Human evaluation of translations
- Translation model training or fine-tuning
- Cost optimization for API calls

## 10. Dependencies

### 10.1 External Services
- Translation API access (OpenAI, Anthropic, Google, or similar)
- API keys and authentication

### 10.2 Python Libraries
- `openai` or `anthropic` (for translation agents)
- `sentence-transformers` (for embeddings)
- `numpy` (for vector operations)
- `scikit-learn` (for cosine similarity)
- `matplotlib` or `plotly` (for visualization)
- `tqdm` (for progress bars)
- `python-dotenv` (for configuration)

## 11. Risks and Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| API rate limiting | High | Medium | Implement backoff, use multiple API keys |
| Agent timeout/failure | High | Medium | Robust retry logic, save checkpoints |
| Inconsistent translations | Medium | High | Use deterministic models, set temperature=0 |
| High API costs | Medium | Medium | Monitor costs, implement budget limits |
| Embedding model issues | Medium | Low | Use well-tested models, fallback options |
| Memory issues with 100 sentences | Low | Low | Process in batches, clear memory |

## 12. Future Enhancements

- Support for configurable number of sentences
- Multiple language chain configurations
- Additional similarity metrics (BLEU, ROUGE, semantic similarity)
- Parallel processing for faster execution
- Web dashboard for real-time monitoring
- Comparative analysis across different translation models
- Export to multiple formats (CSV, Excel, PDF report)

## 13. Acceptance Criteria

The system shall be considered complete when:
1. All 100 sentences are generated and processed successfully
2. All three agents perform translations with < 5% failure rate
3. Cosine distances are calculated for all sentence pairs
4. Mean and variance are computed correctly
5. Visualization is generated and saved
6. Results file is created with all required data
7. Error handling works as specified
8. System completes within 30 minutes
9. Code is documented and follows style guidelines
10. Manual testing confirms accuracy of results

## 14. Timeline Estimate

- **Sentence Generation**: 2 hours
- **Agent Integration**: 8 hours
- **Pipeline Implementation**: 6 hours
- **Error Handling**: 4 hours
- **Similarity Calculation**: 3 hours
- **Visualization & Stats**: 3 hours
- **Testing & Documentation**: 4 hours

**Total Estimated Development Time**: 30 hours

---

**Document Version**: 1.0
**Date**: 2025-10-28
**Author**: Product Requirements
**Status**: Ready for Development
