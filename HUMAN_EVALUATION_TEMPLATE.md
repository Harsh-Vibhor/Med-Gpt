# Human Evaluation Template for Med-GPT

## Instructions

After running the automatic evaluation, use this template to add human scores to your results.

## Scoring Criteria

### Score: 1 (Poor)
- Answer is incorrect or irrelevant
- Contains significant medical inaccuracies
- Does not address the question
- Potentially harmful information

### Score: 2 (Fair)
- Partially correct but incomplete
- Missing key information
- Some inaccuracies present
- Vague or unclear

### Score: 3 (Good)
- Generally correct and relevant
- Addresses main points of question
- Minor inaccuracies or omissions
- Could be more specific

### Score: 4 (Very Good)
- Accurate and comprehensive
- Well-structured answer
- Addresses all aspects of question
- Minor improvements possible

### Score: 5 (Excellent)
- Highly accurate and complete
- Clear, concise, and well-organized
- Fully addresses question
- Clinically appropriate
- No improvements needed

## Evaluation Dimensions

When scoring, consider:

1. **Medical Accuracy**
   - Is the information medically correct?
   - Are there any dangerous inaccuracies?

2. **Completeness**
   - Does it answer all parts of the question?
   - Are key details included?

3. **Clarity**
   - Is the answer easy to understand?
   - Is it well-organized?

4. **Clinical Relevance**
   - Is the information practically useful?
   - Is it appropriate for the context?

5. **Grounding**
   - Is the answer based on the retrieved context?
   - Are there hallucinations?

## Evaluation Process

### Step 1: Open Results
```bash
# Open the CSV file
results/evaluation_results.csv
```

### Step 2: Review Each Answer
For each row:
1. Read the **question**
2. Read the **answer**
3. Check the **retrieved_chunks** (optional)
4. Assign a **human_score** (1-5)

### Step 3: Fill in Scores
Add your score to the `human_score` column.

### Step 4: Save
Save the CSV file with your scores.

## Example Evaluation

### Question
"What are the diagnostic criteria for severe malaria according to WHO?"

### Answer (Model: phi)
"Severe malaria is diagnosed based on clinical and laboratory criteria. Clinical features include impaired consciousness, severe anemia, respiratory distress, and multiple convulsions. Laboratory findings include parasitemia >5%, hypoglycemia, and acidosis."

### Evaluation
- **Medical Accuracy:** ✓ Correct
- **Completeness:** ✓ Covers main criteria
- **Clarity:** ✓ Well-organized
- **Clinical Relevance:** ✓ Practical
- **Grounding:** ✓ Based on WHO guidelines

**Human Score:** 4 (Very Good)
*Rationale: Accurate and comprehensive, but could include more specific thresholds.*

---

### Question
"What is the treatment for malaria?"

### Answer (Model: tinyllama)
"Malaria can be treated with various medications including antimalarial drugs."

### Evaluation
- **Medical Accuracy:** ✓ Technically correct but vague
- **Completeness:** ✗ Missing specific drugs, dosages
- **Clarity:** ✓ Clear but not informative
- **Clinical Relevance:** ✗ Not practically useful
- **Grounding:** ? Unclear if grounded

**Human Score:** 2 (Fair)
*Rationale: Too vague, missing critical details like ACTs, dosages, and WHO recommendations.*

## Batch Evaluation Tips

### 1. Randomize Order
Evaluate answers in random order to avoid bias.

### 2. Blind Evaluation
Don't look at model names until after scoring.

### 3. Multiple Raters
Have 2-3 people evaluate independently, then average scores.

### 4. Take Breaks
Evaluate in batches of 10-15 to maintain consistency.

### 5. Use Reference
Keep WHO guidelines open for fact-checking.

## Inter-Rater Reliability

If using multiple raters, compute agreement:

### Cohen's Kappa
```python
from sklearn.metrics import cohen_kappa_score

rater1_scores = [4, 3, 5, 2, 4]
rater2_scores = [4, 3, 4, 2, 5]

kappa = cohen_kappa_score(rater1_scores, rater2_scores)
print(f"Cohen's Kappa: {kappa:.3f}")
```

**Interpretation:**
- < 0.20: Poor agreement
- 0.21-0.40: Fair agreement
- 0.41-0.60: Moderate agreement
- 0.61-0.80: Substantial agreement
- 0.81-1.00: Almost perfect agreement

## Analysis After Scoring

### Correlation with Automatic Metrics
```python
import pandas as pd
from scipy.stats import pearsonr

df = pd.read_csv('results/evaluation_results.csv')

# Correlation between human score and relevance
corr_rel, p_rel = pearsonr(df['human_score'], df['relevance_score'])
print(f"Human vs Relevance: r={corr_rel:.3f}, p={p_rel:.4f}")

# Correlation between human score and faithfulness
corr_faith, p_faith = pearsonr(df['human_score'], df['faithfulness_score'])
print(f"Human vs Faithfulness: r={corr_faith:.3f}, p={p_faith:.4f}")
```

### Model Comparison
```python
# Average human scores per model
model_scores = df.groupby('model')['human_score'].agg(['mean', 'std'])
print(model_scores)
```

## Common Pitfalls to Avoid

### 1. Leniency Bias
Don't be too generous with scores. Use the full 1-5 range.

### 2. Halo Effect
Don't let one good/bad answer influence scores for other answers.

### 3. Anchoring
Don't anchor on the first score. Each answer should be evaluated independently.

### 4. Fatigue
Take breaks. Tired evaluators are inconsistent.

### 5. Model Bias
Don't favor certain models. Evaluate blindly if possible.

## Reporting Results

### In Your Paper

**Table: Human Evaluation Results**
| Model | Mean Score | Std Dev | Median |
|-------|-----------|---------|--------|
| Phi | 3.8 | 0.9 | 4 |
| TinyLlama | 3.2 | 1.1 | 3 |
| Gemma:2b | 4.1 | 0.7 | 4 |

**Text:**
```
Human evaluation (n=10 questions) revealed that Gemma:2b 
achieved the highest average score (M=4.1, SD=0.7), followed 
by Phi (M=3.8, SD=0.9) and TinyLlama (M=3.2, SD=1.1). 
Inter-rater reliability was substantial (κ=0.72).
```

## Quality Control Checklist

Before finalizing scores:

- [ ] All answers evaluated
- [ ] Scores are in 1-5 range
- [ ] No missing scores
- [ ] Consistent criteria applied
- [ ] Notes added for edge cases
- [ ] File saved properly
- [ ] Backup created

## Notes Section

Use this space for notes on specific answers:

**Question 1 (Model: phi):**
- Note: Answer was accurate but used technical jargon

**Question 5 (Model: tinyllama):**
- Note: Hallucinated a drug name not in context

**Question 8 (Model: gemma:2b):**
- Note: Excellent answer, cited specific WHO criteria

---

## Contact

For questions about the evaluation process, refer to `EVALUATION_README.md` or contact the research team.
