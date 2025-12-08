"""
Agent Evaluation Runner

This script runs the agent workflow on test queries and captures:
- Questions
- Agent-generated answers
- Retrieved contexts from Pinecone
- Ground truth answers

Output is saved as parquet for RAGAS evaluation.
"""

import yaml
import pandas as pd
from pathlib import Path
import logging
import sys
import os
from typing import List, Dict
from dotenv import load_dotenv

# Add parent directory to path to import from backend
current_dir = Path(__file__).parent
backend_dir = current_dir.parent
sys.path.insert(0, str(backend_dir))

from graph.workflow import run_agent_workflow
from services.pinecone_service import get_pinecone_service
from config import Config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


def load_test_dataset(testset_path: str) -> pd.DataFrame:
    """Load test dataset from parquet file."""
    if not os.path.exists(testset_path):
        logger.error(f"❌ Test dataset not found at {testset_path}")
        logger.error("   Run generate_test_queries.py first!")
        raise FileNotFoundError(f"Test dataset not found: {testset_path}")
    
    logger.info(f"Loading test dataset from: {testset_path}")
    df = pd.read_parquet(testset_path)
    logger.info(f"✅ Loaded {len(df)} test queries")
    
    return df


def run_agent_on_query(question: str, lecture_id: str = "lecture-7") -> Dict:
    """
    Run agent workflow on a single query and capture results.
    
    Args:
        question: The question to ask
        lecture_id: Lecture ID to use for context
        
    Returns:
        Dict with answer, contexts, and metadata
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"Processing: {question[:80]}...")
    logger.info(f"{'='*60}")
    
    try:
        # Run the agent workflow
        final_state = run_agent_workflow(
            query=question,
            lecture_id=lecture_id,
            conversation_history=None
        )
        
        # Extract answer
        answer = final_state.get('response', '')
        
        # Extract contexts from the state
        context_docs = final_state.get('context', [])
        
        # Format contexts as list of strings
        contexts = []
        for doc in context_docs:
            if hasattr(doc, 'page_content'):
                contexts.append(doc.page_content)
            elif isinstance(doc, dict):
                contexts.append(doc.get('text', str(doc)))
            else:
                contexts.append(str(doc))
        
        # Get metadata
        intent = final_state.get('intent', 'unknown')
        agents_called = final_state.get('agent_history', [])
        
        logger.info(f"✅ Answer generated ({len(answer)} chars)")
        logger.info(f"   Intent: {intent}")
        logger.info(f"   Agents: {agents_called}")
        logger.info(f"   Contexts retrieved: {len(contexts)}")
        
        return {
            'answer': answer,
            'contexts': contexts,
            'intent': intent,
            'agents_called': agents_called,
            'num_contexts': len(contexts)
        }
        
    except Exception as e:
        logger.error(f"❌ Error processing query: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            'answer': f"ERROR: {str(e)}",
            'contexts': [],
            'intent': 'error',
            'agents_called': [],
            'num_contexts': 0
        }


def run_evaluation(df_test: pd.DataFrame, lecture_id: str = "lecture-7") -> pd.DataFrame:
    """
    Run agent on all test queries and collect results.
    
    Args:
        df_test: DataFrame with test queries
        lecture_id: Lecture ID to use
        
    Returns:
        DataFrame with results
    """
    results = []
    
    for idx, row in df_test.iterrows():
        question = row['question']
        ground_truth = row['ground_truth']
        query_type = row['query_type']
        
        # Run agent
        result = run_agent_on_query(question, lecture_id)
        
        # Combine with test data
        results.append({
            'question': question,
            'answer': result['answer'],
            'contexts': result['contexts'],
            'ground_truth': ground_truth,
            'query_type': query_type,
            'intent': result['intent'],
            'agents_called': result['agents_called'],
            'num_contexts': result['num_contexts']
        })
        
        logger.info(f"Progress: {idx + 1}/{len(df_test)} queries completed\n")
    
    return pd.DataFrame(results)


def save_results(df_results: pd.DataFrame, output_path: str):
    """Save evaluation results as parquet file."""
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    df_results.to_parquet(output_file, index=False)
    logger.info(f"✅ Saved evaluation results to: {output_file}")


def main():
    """Main execution function."""
    # Load configuration
    config_path = current_dir / "config_eval.yaml"
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Get paths from config
    testset_path = backend_dir / config['evaluation']['testset_path']
    results_path = backend_dir / config['evaluation']['results_path']
    
    # Load test dataset
    df_test = load_test_dataset(str(testset_path))
    
    print("\n" + "="*60)
    print("🚀 Starting Agent Evaluation")
    print("="*60)
    print(f"Test queries: {len(df_test)}")
    print(f"Output: {results_path}")
    print("="*60 + "\n")
    
    # Run evaluation
    df_results = run_evaluation(df_test, lecture_id="lecture-7")
    
    # Save results
    save_results(df_results, str(results_path))
    
    print("\n" + "="*60)
    print("✅ Agent Evaluation Complete")
    print("="*60)
    print(f"Total queries: {len(df_results)}")
    print(f"Successful: {len(df_results[df_results['intent'] != 'error'])}")
    print(f"Errors: {len(df_results[df_results['intent'] == 'error'])}")
    print(f"\nResults saved to: {results_path}")
    print("="*60)


if __name__ == "__main__":
    main()
