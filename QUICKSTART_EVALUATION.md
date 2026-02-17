# Quick Start: Multi-Model Evaluation

## Prerequisites

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Ensure Ollama models are available:**
```bash
ollama pull phi
ollama pull tinyllama
ollama pull gemma:2b
```

3. **Verify Ollama is running:**
```bash
ollama serve
```

## Running Evaluation

### Step 1: Run the evaluation pipeline
```bash
python evaluate_models.py
```

This will:
- Evaluate 3 models (phi, tinyllama, gemma:2b)
- Run 10 medical questions per model
- Compute automatic metrics
- Generate results in `results/` directory

**Expected time:** 5-10 minutes (depending on your hardware)

### Step 2: Review results

Open the generated files:
- `results/evaluation_results.csv` - Detailed results
- `results/model_statistics.csv` - Summary statistics

### Step 3: Add human scores (optional)

1. Open `results/evaluation_results.csv`
2. Fill in the `human_score` column (1-5 scale)
3. Save the file

## Customization

### Use different questions

Edit `evaluate_models.py` and modify:
```python
EVALUATION_QUESTIONS = [
    "Your question 1?",
    "Your question 2?",
    # ...
]
```

Or use the question manager:
```bash
python custom_questions.py
```

### Add more models

Edit `evaluate_models.py`:
```python
MODELS = ["phi", "tinyllama", "gemma:2b", "llama2:7b"]
```

Then pull the new model:
```bash
ollama pull llama2:7b
```

## Output Format

### evaluation_results.csv
| Column | Description |
|--------|-------------|
| question | The evaluation question |
| model | Model name (phi, tinyllama, etc.) |
| answer | Generated answer |
| num_retrieved_chunks | Number of chunks retrieved |
| retrieved_chunks | JSON of retrieved chunks |
| confidence | RAG confidence score |
| relevance_score | Question-answer similarity |
| faithfulness_score | Answer-context similarity |
| human_score | Manual score (1-5) |
| timestamp | When the evaluation ran |

### model_statistics.csv
| Column | Description |
|--------|-------------|
| model | Model name |
| num_questions | Number of questions evaluated |
| mean_relevance | Average relevance score |
| std_relevance | Standard deviation of relevance |
| mean_faithfulness | Average faithfulness score |
| std_faithfulness | Standard deviation of faithfulness |
| mean_confidence | Average RAG confidence |
| combined_score | Overall score (relevance + faithfulness) / 2 |

## Troubleshooting

### "Model not found" error
```bash
ollama pull <model-name>
```

### "Connection refused" error
Start Ollama:
```bash
ollama serve
```

### Out of memory
Reduce the number of questions or evaluate one model at a time by editing `MODELS` list.

### Slow evaluation
This is normal - each question requires:
1. Embedding generation
2. Vector search
3. LLM inference

Expect ~30-60 seconds per question depending on model size.

## Next Steps

1. **Analyze results** - Compare models using the statistics
2. **Add human evaluation** - Fill in human_score column
3. **Run statistical tests** - The script automatically computes paired t-tests
4. **Use in paper** - Export tables and figures for your research paper

## Example Results

After running evaluation, you'll see output like:

```
MODEL STATISTICS
================
model        mean_relevance  mean_faithfulness  combined_score
phi          0.782           0.845              0.814
tinyllama    0.756           0.823              0.790
gemma:2b     0.791           0.851              0.821

STATISTICAL SIGNIFICANCE
========================
phi vs tinyllama:
  Relevance: t=2.145, p=0.0234 *
  Faithfulness: t=1.876, p=0.0567

phi vs gemma:2b:
  Relevance: t=-0.876, p=0.3912
  Faithfulness: t=-0.654, p=0.5234
```

## Support

For issues or questions, refer to `EVALUATION_README.md` for detailed documentation.
