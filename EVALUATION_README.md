# Med-GPT Multi-Model Evaluation Pipeline

## Overview

This evaluation pipeline enables scientific assessment of multiple Ollama models for medical RAG tasks, suitable for research papers and journal submissions.

## Features

- **Multi-model support**: phi, tinyllama, gemma:2b (easily extensible)
- **Automatic metrics**: Answer relevance and faithfulness scores
- **Human evaluation**: Placeholder column for manual scoring (1-5 scale)
- **Statistical analysis**: Paired t-tests for significance testing
- **Export formats**: CSV and JSON for reproducibility

## Installation

Ensure you have the required dependencies:

```bash
pip install pandas numpy scipy scikit-learn sentence-transformers
```

## Usage

### Basic Evaluation

Run the evaluation pipeline:

```bash
python evaluate_models.py
```

This will:
1. Load all configured models
2. Run each model on all evaluation questions
3. Compute automatic metrics
4. Generate statistics
5. Export results to `results/` directory

### Output Files

- `results/evaluation_results.csv` - Detailed results for each question/model
- `results/evaluation_results.json` - JSON format for reproducibility
- `results/model_statistics.csv` - Aggregated statistics per model

### Custom Questions

Edit the `EVALUATION_QUESTIONS` list in `evaluate_models.py`:

```python
EVALUATION_QUESTIONS = [
    "Your custom medical question here?",
    "Another question?",
    # Add more...
]
```

### Adding New Models

Add model names to the `MODELS` list:

```python
MODELS = ["phi", "tinyllama", "gemma:2b", "llama2:7b"]
```

Ensure the model is available in Ollama:

```bash
ollama pull llama2:7b
```

## Metrics

### Answer Relevance
Cosine similarity between question embedding and answer embedding.
- Range: 0.0 to 1.0
- Higher = more relevant answer

### Faithfulness
Cosine similarity between answer embedding and retrieved context embedding.
- Range: 0.0 to 1.0
- Higher = answer is more grounded in retrieved context

### Combined Score
Average of relevance and faithfulness (50% each).

## Human Evaluation

After automatic evaluation:

1. Open `results/evaluation_results.csv`
2. Add scores (1-5) to the `human_score` column
3. Use for qualitative analysis in your paper

## Statistical Significance

The pipeline automatically computes paired t-tests between models:

```
phi vs tinyllama:
  Relevance: t=2.145, p=0.0234 *
  Faithfulness: t=1.876, p=0.0567
```

`*` indicates p < 0.05 (statistically significant)

## Research Paper Integration

### Tables

Use `model_statistics.csv` for summary tables:

| Model | Mean Relevance | Mean Faithfulness | Combined Score |
|-------|----------------|-------------------|----------------|
| phi   | 0.78 ± 0.12    | 0.82 ± 0.09       | 0.80           |
| ...   | ...            | ...               | ...            |

### Reproducibility

Include `evaluation_results.json` as supplementary material for full reproducibility.

## Low RAM Usage

Models are evaluated **sequentially** (not in parallel) to minimize RAM usage. Typical usage: ~4-6GB RAM.

## Customization

### Modify Metrics

Edit `compute_answer_relevance()` and `compute_faithfulness()` in `evaluate_models.py`.

### Change Evaluation Set

Replace `EVALUATION_QUESTIONS` with your domain-specific questions.

### Adjust RAG Parameters

Modify `enhanced_rag_query()` call parameters:
- `top_k`: Number of chunks to retrieve
- `similarity_threshold`: Minimum similarity for retrieval

## Troubleshooting

### Model Not Found
```bash
ollama pull <model-name>
```

### Out of Memory
Reduce `top_k` or evaluate fewer questions at a time.

### Connection Error
Ensure Ollama is running:
```bash
ollama serve
```

## Citation

If using this evaluation pipeline in research, please cite your Med-GPT paper and mention the evaluation methodology.

## License

Same as Med-GPT project.
