"""
Generate Test Queries for RAGAS Evaluation

This script loads predefined test queries with ground truth answers
and saves them as a parquet file for evaluation.
"""

import yaml
import pandas as pd
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_test_queries(queries_file: str = "test_queries.yaml") -> pd.DataFrame:
    """
    Load test queries from YAML file.
    
    Args:
        queries_file: Path to YAML file containing test queries
        
    Returns:
        DataFrame with columns: question, ground_truth, query_type, expected_namespaces
    """
    current_dir = Path(__file__).parent
    queries_path = current_dir / queries_file
    
    if not queries_path.exists():
        logger.error(f"❌ Test queries file not found at {queries_path}")
        raise FileNotFoundError(f"Test queries file not found: {queries_path}")
    
    logger.info(f"Loading test queries from: {queries_path}")
    
    with open(queries_path, 'r') as f:
        data = yaml.safe_load(f)
    
    queries = data.get('queries', [])
    
    if not queries:
        logger.error("❌ No queries found in test_queries.yaml")
        raise ValueError("No queries found in test_queries.yaml")
    
    logger.info(f"✅ Loaded {len(queries)} test queries")
    
    return pd.DataFrame(queries)


def save_test_dataset(df: pd.DataFrame, output_path: str):
    """
    Save test dataset as parquet file.
    
    Args:
        df: DataFrame containing test queries
        output_path: Path to save parquet file
    """
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    df.to_parquet(output_file, index=False)
    logger.info(f"✅ Saved test dataset to: {output_file}")
    logger.info(f"   Total queries: {len(df)}")
    logger.info(f"   Query types: {df['query_type'].value_counts().to_dict()}")


def main():
    """Main execution function."""
    # Load configuration
    current_dir = Path(__file__).parent
    config_path = current_dir / "config_eval.yaml"
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Load test queries
    df = load_test_queries()
    
    # Get output path from config
    testset_path = config['evaluation']['testset_path']
    
    # Resolve path relative to backend directory
    backend_dir = current_dir.parent
    output_path = backend_dir / testset_path
    
    # Save dataset
    save_test_dataset(df, str(output_path))
    
    print("\n" + "="*60)
    print("✅ Test Query Generation Complete")
    print("="*60)
    print(f"Output: {output_path}")
    print(f"Queries: {len(df)}")
    print("\nQuery Distribution:")
    for query_type, count in df['query_type'].value_counts().items():
        print(f"  - {query_type}: {count}")
    print("="*60)


if __name__ == "__main__":
    main()
