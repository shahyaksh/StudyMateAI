# RAGAS Evaluation Framework

## Overview

This evaluation framework assesses the quality of the Lecture RAG system using RAGAS (Retrieval Augmented Generation Assessment) metrics. It evaluates both retrieval quality and answer generation across lecture content (slides + transcripts) and research papers.

### Performance Metrics

Based on evaluation with **20 test queries** across lecture content and research papers:

| Metric | Mean Score | Std Dev | Min | Max | Interpretation |
|--------|-----------|---------|-----|-----|----------------|
| **Answer Relevancy** | **0.86** | 0.22 | 0.00 | 1.00 | ✅ Good - Answers generally address questions well |
| **Faithfulness** | **0.41** | 0.18 | 0.28 | 0.54 | ⚠️ Needs Improvement - Some hallucinations detected |
| **Context Recall** | **0.75** | N/A | 0.75 | 0.75 | ✅ Fair - Most ground truth retrieved |
| **Context Precision** | **0.93** | 0.27 | 0.00 | 1.00 | ✅ Very Good - Relevant contexts ranked highly |

### Key Findings

**Strengths:**
- ✅ **Excellent Context Precision (0.93)**: Relevant contexts are consistently prioritized in retrieval
- ✅ **Good Answer Relevancy (0.86)**: Answers generally address user questions appropriately
- ✅ **Fair Context Recall (0.75)**: Most ground truth information is retrieved from the knowledge base

**Areas for Improvement:**
- ⚠️ **Faithfulness (0.41)**: System shows tendency to add information beyond retrieved context
  - Need to strengthen grounding constraints in prompts
  - Review agent instructions to emphasize strict adherence to source material
- Answer Relevancy variance - some queries scored 0.0, indicating edge cases
- Fine-tune retrieval parameters for consistent precision across all query types

### Test Coverage

The evaluation includes:
- **12 Lecture Content Queries**: Questions about slides and transcripts
- **6 Paper Content Queries**: Research paper-specific questions
- **2 Mixed Queries**: Questions requiring both lecture and paper content

### System Performance

- **Success Rate**: 100% (20/20 queries processed successfully)
- **Average Response Time**: 2-4 seconds per query
- **Agent Routing Accuracy**: 100% correct intent classification
- **Average Contexts Retrieved**: 3-6 per query

## Metrics Evaluated

- **Faithfulness**: Measures if the generated answer is grounded in the retrieved context
- **Answer Relevancy**: Assesses if the answer addresses the question appropriately
- **Context Recall**: Evaluates if the ground truth information is present in retrieved contexts
- **Context Precision**: Measures if relevant contexts are ranked higher than irrelevant ones

## Directory Structure

```
backend/evaluation/
├── config_eval.yaml              # Evaluation configuration
├── test_queries.yaml             # Test queries with ground truth
├── requirements_eval.txt         # RAGAS dependencies
├── generate_test_queries.py      # Step 1: Generate test dataset
├── agent_evaluation_runner.py    # Step 2: Run agent and collect results
├── ragas_eval_wrapper.py         # Step 3: Calculate RAGAS metrics
├── README.md                     # This file
├── testsets/                     # Generated test datasets
│   └── lecture_rag_evaluation.parquet
└── results/                      # Evaluation results
    ├── lecture_rag_evaluation_results.parquet
    ├── lecture_rag_evaluation_ragas_metrics.parquet
    └── ragas_scores.json
```

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r evaluation/requirements_eval.txt
```

### 2. Environment Variables

Ensure your `.env` file in the `backend/` directory contains:

```ini
OPENAI_API_KEY=your_openai_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENVIRONMENT=your_pinecone_environment
```

### 3. Verify Data

Ensure your Pinecone indexes are populated with:
- Lecture slides (namespace: `slides`)
- Research papers (namespace: `papers`)
- Lecture transcripts (namespace: `transcript`)

## Running the Evaluation

### Step 1: Generate Test Dataset

Create the test dataset from predefined queries with ground truth answers:

```bash
cd backend/evaluation
python generate_test_queries.py
```

**Output**: `testsets/lecture_rag_evaluation.parquet`

This creates a dataset with 20 test queries covering:
- Lecture content questions (slides + transcript)
- Research paper questions
- Mixed queries requiring multiple sources

### Step 2: Run Agent Evaluation

Execute the agent on all test queries and capture results:

```bash
python agent_evaluation_runner.py
```

**Output**: `results/lecture_rag_evaluation_results.parquet`

This script:
- Runs each query through the agent workflow
- Captures generated answers
- Collects retrieved contexts from Pinecone
- Records agent routing decisions (intent, agents called)
- Saves results with ground truth for comparison

**Expected Runtime**: ~5-10 minutes for 20 queries (depending on API latency)

### Step 3: Calculate RAGAS Metrics

Evaluate the results using RAGAS metrics:

```bash
python ragas_eval_wrapper.py
```

**Outputs**: 
- `results/lecture_rag_evaluation_ragas_metrics.parquet`
- `results/ragas_scores.json`

This script:
- Loads agent evaluation results
- Prepares data for RAGAS format
- Calculates Faithfulness, Answer Relevancy, Context Recall, Context Precision
- Saves detailed metrics per query
- Prints summary statistics

**Expected Runtime**: ~3-10 minutes (RAGAS uses LLM for evaluation)

**Note**: Uses `strictness=1` for AnswerRelevancy to reduce API calls and improve JSON parsing reliability.

## Understanding the Results

### Metrics Interpretation

- **Faithfulness (0-1)**: Higher is better
  - 1.0 = Answer is fully grounded in retrieved context
  - 0.0 = Answer contains hallucinated information

- **Answer Relevancy (0-1)**: Higher is better
  - 1.0 = Answer directly addresses the question
  - 0.0 = Answer is off-topic or irrelevant

- **Context Recall (0-1)**: Higher is better
  - 1.0 = All ground truth information was retrieved
  - 0.0 = Ground truth not found in contexts

- **Context Precision (0-1)**: Higher is better
  - 1.0 = All retrieved contexts are relevant
  - 0.0 = Retrieved contexts are mostly irrelevant

### Viewing Results

```python
import pandas as pd

# View detailed metrics per query
df = pd.read_parquet('results/lecture_rag_evaluation_ragas_metrics.parquet')
print(df[['user_input', 'faithfulness', 'answer_relevancy', 'context_recall', 'context_precision']])

# View overall statistics
print(df[['faithfulness', 'answer_relevancy', 'context_recall', 'context_precision']].describe())
```

## Customizing Evaluation

### Adding New Test Queries

Edit `test_queries.yaml` to add new queries:

```yaml
queries:
  - question: "Your question here"
    ground_truth: "The correct answer"
    query_type: "lecture_content|paper_content|mixed"
    expected_namespaces: ["slides", "papers", "transcript"]
```

Then re-run Step 1 to regenerate the test dataset.

### Modifying Configuration

Edit `config_eval.yaml` to:
- Change LLM model for RAGAS evaluation (currently: `gpt-4o`)
- Adjust number of test queries
- Modify output paths
- Select different lectures to evaluate

## Troubleshooting

### "Test dataset not found"
- Run `generate_test_queries.py` first

### "Results file not found"
- Run `agent_evaluation_runner.py` before `ragas_eval_wrapper.py`

### "OPENAI_API_KEY not found"
- Ensure `.env` file exists in `backend/` directory
- Verify API key is valid

### Low Context Recall scores
- Check if Pinecone indexes contain relevant documents
- Verify embedding model matches the one used for indexing
- Review retrieved contexts in results file

### Low Faithfulness scores
- Agent may be hallucinating or adding information not in context
- Review prompts in `config/prompts.yaml`
- Check if retrieved contexts are relevant

### JSON Parsing Errors
- Ensure using `gpt-4o` model (better JSON compliance than `gpt-4o-mini`)
- Check `config_eval.yaml` has `strictness: 1` for AnswerRelevancy

## Next Steps

1. **Analyze Results**: Identify queries with low scores
2. **Improve Retrieval**: Adjust chunking, embedding model, or retrieval parameters
3. **Refine Prompts**: Update agent prompts in `config/prompts.yaml`
4. **Expand Test Set**: Add more diverse queries to `test_queries.yaml`
5. **Iterate**: Re-run evaluation after improvements

## References

- [RAGAS Documentation](https://docs.ragas.io/)
- [RAGAS Metrics Guide](https://docs.ragas.io/en/latest/concepts/metrics/index.html)
- [RAGAS GitHub Issue #2473](https://github.com/explodinggradients/ragas/issues/2473) - JSON parsing solutions

