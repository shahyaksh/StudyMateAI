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
import json
import logging
from datetime import datetime
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

    metrics_to_run = [
        AnswerRelevancy(llm=llm, embeddings=embeddings, strictness=1), 
        Faithfulness(llm=llm),
        ContextRecall(llm=llm), 
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


def save_metrics_to_json(df_metrics: pd.DataFrame, config: dict, output_dir: str):
    """
    Save RAGAS metrics to a structured JSON file.
    
    Args:
        df_metrics: DataFrame containing RAGAS metrics
        config: Configuration dict
        output_dir: Directory to save JSON file
    """
    output_path = Path(output_dir) / "results" / "ragas_scores.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Get numeric columns (the actual metrics)
    numeric_cols = df_metrics.select_dtypes(include=['float64', 'int64']).columns
    
    # Calculate metric statistics
    metrics_data = {}
    for metric in numeric_cols:
        mean_val = float(df_metrics[metric].mean())
        metrics_data[metric] = {
            "score": round(mean_val, 2),
            "description": get_metric_description(metric),
            "interpretation": get_metric_interpretation(metric, mean_val)
        }
    
    # Identify strengths and areas for improvement
    strengths = []
    improvements = []
    
    for metric, data in metrics_data.items():
        if data["score"] >= 0.95:
            strengths.append(f"{metric.replace('_', ' ').title()}: {data['score']:.2f} - {data['interpretation']}")
        elif data["score"] < 0.90:
            improvements.append(f"{metric.replace('_', ' ').title()} could be optimized (current: {data['score']:.2f})")
    
    # Build JSON structure
    json_data = {
        "evaluation_metadata": {
            "framework": "RAGAS",
            "model": config['llm']['model'],
            "embedding_model": config['embeddings']['model'],
            "test_queries": len(df_metrics),
            "evaluation_date": datetime.now().strftime("%Y-%m-%d"),
            "dataset": "Lecture Transcripts + Research Papers"
        },
        "metrics": metrics_data,
        "summary": {
            "overall_performance": get_overall_performance(metrics_data),
            "key_strengths": strengths if strengths else ["All metrics performing well"],
            "areas_for_improvement": improvements if improvements else ["System performing optimally"]
        },
        "system_configuration": {
            "retrieval_method": "Hybrid (Dense Vector + Metadata Filtering)",
            "vector_database": "Pinecone",
            "embedding_dimensions": 3072,
            "chunk_size": 500,
            "top_k_retrieval": 5,
            "agent_architecture": "Multi-Agent (Supervisor-Worker Pattern)"
        }
    }
    
    # Save to JSON
    with open(output_path, 'w') as f:
        json.dump(json_data, f, indent=2)
    
    logger.info(f"✅ Saved JSON metrics to: {output_path}")
    return output_path


def get_metric_description(metric_name: str) -> str:
    """Get description for a metric."""
    descriptions = {
        "faithfulness": "Measures factual consistency with source material",
        "answer_relevancy": "Measures how relevant answers are to the questions",
        "context_recall": "Measures if all relevant information was retrieved",
        "context_precision": "Measures ranking quality of retrieved contexts"
    }
    return descriptions.get(metric_name, "Performance metric")


def get_metric_interpretation(metric_name: str, score: float) -> str:
    """Get interpretation for a metric score."""
    if score >= 0.95:
        return "Excellent - Outstanding performance"
    elif score >= 0.90:
        return "Very Good - Strong performance"
    elif score >= 0.80:
        return "Good - Solid performance"
    elif score >= 0.70:
        return "Fair - Acceptable performance"
    else:
        return "Needs Improvement"


def get_overall_performance(metrics_data: dict) -> str:
    """Determine overall performance based on all metrics."""
    avg_score = sum(m["score"] for m in metrics_data.values()) / len(metrics_data)
    
    if avg_score >= 0.95:
        return "Excellent"
    elif avg_score >= 0.90:
        return "Very Good"
    elif avg_score >= 0.80:
        return "Good"
    elif avg_score >= 0.70:
        return "Fair"
    else:
        return "Needs Improvement"



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
    
    # Save metrics to JSON
    json_path = save_metrics_to_json(df_metrics, config, str(current_dir))
    
    # Print summary
    print_metrics_summary(df_metrics)
    
    print(f"\nDetailed metrics saved to: {metrics_path}")
    print(f"JSON metrics saved to: {json_path}")
    print("="*60)


if __name__ == "__main__":
    main()
