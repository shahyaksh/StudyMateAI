"""
RAGAS Evaluation Wrapper

This script calculates RAGAS metrics on the agent evaluation results:
- Faithfulness: Is the answer grounded in the retrieved context?
- Answer Relevancy: Does the answer address the question?
- Context Recall: Is the ground truth present in retrieved contexts?
- Context Precision: Are relevant contexts ranked higher?
"""

import yaml
import pandas as pd
from ragas import evaluate
from datasets import Dataset
from ragas.metrics import Faithfulness, AnswerRelevancy, ContextRecall, ContextPrecision
from pathlib import Path
import sys
import os
import logging
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    logger.error("❌ OPENAI_API_KEY not found in environment variables.")
    sys.exit(1)


def load_config():
    """Load evaluation configuration."""
    current_dir = Path(__file__).parent
    config_path = current_dir / "config_eval.yaml"
    
    if not os.path.exists(config_path):
        logger.error(f"❌ Config not found at {config_path}")
        sys.exit(1)
    
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def load_results(results_path: str) -> pd.DataFrame:
    """Load evaluation results from parquet file."""
    if not os.path.exists(results_path):
        logger.error(f"❌ Results file not found at {results_path}")
        logger.error("   Run agent_evaluation_runner.py first!")
        sys.exit(1)
    
    logger.info(f"Loading evaluation results from: {results_path}")
    df = pd.read_parquet(results_path)
    logger.info(f"✅ Loaded {len(df)} evaluation results")
    
    return df


def prepare_ragas_dataset(df: pd.DataFrame) -> Dataset:
    """
    Prepare dataset for RAGAS evaluation.
    
    RAGAS expects:
    - question: The question asked
    - answer: The model's answer
    - contexts: List of retrieved context strings
    - ground_truth: The ground truth answer
    """
    logger.info("Preparing dataset for RAGAS...")
    
    # Create a copy with required columns
    df_ragas = df[['question', 'answer', 'contexts', 'ground_truth']].copy()
    
    # Ensure contexts is a list of strings
    def ensure_list(x):
        if isinstance(x, list):
            return x
        elif x is None:
            return []
        else:
            return [str(x)]
    
    df_ragas['contexts'] = df_ragas['contexts'].apply(ensure_list)
    
    # Filter out rows with errors
    df_ragas = df_ragas[~df_ragas['answer'].str.startswith('ERROR:', na=False)].copy()
    
    logger.info(f"✅ Prepared {len(df_ragas)} rows for RAGAS evaluation")
    
    # Convert to HuggingFace Dataset
    dataset = Dataset.from_pandas(df_ragas)
    
    return dataset


def run_ragas_evaluation(dataset: Dataset, config: dict):
    """
    Run RAGAS evaluation with configured metrics.
    
    Args:
        dataset: HuggingFace Dataset with question, answer, contexts, ground_truth
        config: Configuration dict
    """
    # Initialize LLM for RAGAS
    llm = ChatOpenAI(
        model=config['llm']['model'],
        temperature=config['llm']['temperature'],
        openai_api_key=OPENAI_API_KEY,
    )
    
    # Initialize Embeddings for RAGAS
    embeddings = OpenAIEmbeddings(
        model=config['embeddings']['model'],
        openai_api_key=OPENAI_API_KEY
    )
    
    # Configure metrics using recommended approach from RAGAS team
    # Reference: https://github.com/explodinggradients/ragas/issues/2473
    metrics_to_run = [
        AnswerRelevancy(llm=llm, embeddings=embeddings, strictness=1),  # strictness=1 reduces complexity
        Faithfulness(llm=llm),
        ContextRecall(llm=llm),  # Use ContextRecall from collections (not LLMContextRecall)
        ContextPrecision(llm=llm),
    ]
    
    logger.info("Starting RAGAS evaluation...")
    logger.info(f"Metrics: {[m.__class__.__name__ for m in metrics_to_run]}")
    logger.info("Using strictness=1 for AnswerRelevancy to reduce API calls")
    
    # Run evaluation
    result = evaluate(
        dataset=dataset,
        metrics=metrics_to_run,
        raise_exceptions=False  # Continue on errors
    )
    
    return result


def save_metrics(result, output_path: str):
    """Save RAGAS metrics to parquet file."""
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        df_result = result.to_pandas()
    except Exception as e:
        logger.error(f"Failed to convert RAGAS result to DataFrame: {e}")
        logger.info("Outputting raw result...")
        df_result = pd.DataFrame([result])
    
    df_result.to_parquet(output_file, index=False)
    logger.info(f"✅ Saved RAGAS metrics to: {output_file}")
    
    return df_result


def print_metrics_summary(df_metrics: pd.DataFrame):
    """Print summary of RAGAS metrics."""
    print("\n" + "="*60)
    print("📊 RAGAS Metrics Summary")
    print("="*60)
    
    # Get only numeric columns (the actual metrics)
    numeric_cols = df_metrics.select_dtypes(include=['float64', 'int64']).columns
    
    if len(numeric_cols) == 0:
        print("No numeric metrics found in results.")
        print(f"Available columns: {list(df_metrics.columns)}")
    else:
        for metric in numeric_cols:
            mean_val = df_metrics[metric].mean()
            std_val = df_metrics[metric].std()
            min_val = df_metrics[metric].min()
            max_val = df_metrics[metric].max()
            
            print(f"\n{metric}:")
            print(f"  Mean:  {mean_val:.4f}")
            print(f"  Std:   {std_val:.4f}")
            print(f"  Min:   {min_val:.4f}")
            print(f"  Max:   {max_val:.4f}")
    
    print("\n" + "="*60)


def main():
    """Main execution function."""
    # Load configuration
    config = load_config()
    
    # Get paths
    current_dir = Path(__file__).parent
    backend_dir = current_dir.parent
    
    results_path = backend_dir / config['evaluation']['results_path']
    metrics_path = backend_dir / config['evaluation']['metrics_path']
    
    # Load evaluation results
    df_results = load_results(str(results_path))
    
    # Prepare dataset for RAGAS
    dataset = prepare_ragas_dataset(df_results)
    
    print("\n" + "="*60)
    print("🚀 Starting RAGAS Evaluation")
    print("="*60)
    print(f"Queries to evaluate: {len(dataset)}")
    print(f"Metrics: Faithfulness, Answer Relevancy, Context Recall, Context Precision")
    print("="*60 + "\n")
    
    # Run RAGAS evaluation
    result = run_ragas_evaluation(dataset, config)
    
    print("\n✅ RAGAS evaluation complete!")
    
    # Save metrics
    df_metrics = save_metrics(result, str(metrics_path))
    
    # Print summary
    print_metrics_summary(df_metrics)
    
    print(f"\nDetailed metrics saved to: {metrics_path}")
    print("="*60)


if __name__ == "__main__":
    main()
