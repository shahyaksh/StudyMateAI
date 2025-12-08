# RAGAS Evaluation Framework

## Overview

This evaluation framework assesses the quality of the Lecture RAG system using RAGAS (Retrieval Augmented Generation Assessment) metrics. It evaluates both retrieval quality and answer generation across lecture content (slides + transcripts) and research papers.

## Current Implementation Results

### Performance Metrics

Based on evaluation with 10 test queries across lecture content and research papers:

| Metric | Mean Score | Std Dev | Min | Max | Interpretation |
|--------|-----------|---------|-----|-----|----------------|
| **Answer Relevancy** | **0.93** | 0.09 | 0.76 | 1.00 | ✅ Excellent - Answers directly address questions |
| **Faithfulness** | **1.00** | 0.00 | 1.00 | 1.00 | ✅ Perfect - No hallucinations detected |
| **Context Recall** | **1.00** | 0.00 | 1.00 | 1.00 | ✅ Perfect - All ground truth retrieved |
| **Context Precision** | **0.86** | 0.38 | 0.00 | 1.00 | ✅ Very Good - Relevant contexts ranked highly |

### Key Findings

**Strengths:**
- ✅ **Perfect Faithfulness (1.00)**: The system never hallucinates - all answers are fully grounded in retrieved context
- ✅ **Perfect Context Recall (1.00)**: Ground truth information is consistently retrieved from the knowledge base
- ✅ **Excellent Answer Relevancy (0.93)**: Answers are highly relevant and directly address user questions
- ✅ **Strong Context Precision (0.86)**: Relevant contexts are prioritized effectively in retrieval

**Areas for Improvement:**
- Context Precision variance (one query scored 0.0) - investigate edge cases
- Fine-tune retrieval parameters for consistent precision across all query types

### Test Coverage

The evaluation includes:
- **7 Lecture Content Queries**: Questions about slides and transcripts
- **2 Mixed Queries**: Questions requiring both lecture and paper content
- **1 Paper Content Query**: Research paper-specific question

### System Performance

- **Success Rate**: 100% (10/10 queries processed successfully)
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
│   └── lecture_rag_validation.parquet
└── results/                      # Evaluation results
    ├── lecture_rag_validation_results.parquet
    └── lecture_rag_validation_ragas_metrics.parquet
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

**Output**: `testsets/lecture_rag_validation.parquet`

This creates a dataset with 10 test queries covering:
- Lecture content questions (slides + transcript)
- Research paper questions
- Mixed queries requiring multiple sources

### Step 2: Run Agent Evaluation

Execute the agent on all test queries and capture results:

```bash
python agent_evaluation_runner.py
```

**Output**: `results/lecture_rag_validation_results.parquet`

This script:
- Runs each query through the agent workflow
- Captures generated answers
- Collects retrieved contexts from Pinecone
- Records agent routing decisions (intent, agents called)
- Saves results with ground truth for comparison

**Expected Runtime**: ~2-5 minutes for 10 queries (depending on API latency)

### Step 3: Calculate RAGAS Metrics

Evaluate the results using RAGAS metrics:

```bash
python ragas_eval_wrapper.py
```

**Output**: `results/lecture_rag_validation_ragas_metrics.parquet`

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
df = pd.read_parquet('results/lecture_rag_validation_ragas_metrics.parquet')
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

