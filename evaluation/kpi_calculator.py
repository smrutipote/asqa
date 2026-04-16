"""
KPI Calculator - computes all 5 key performance indicators from pipeline results.

KPIs:
1. Bug Detection Rate (BDR) - % of bugs exposed by generated tests
2. False Positive Rate (FPR) - % of incorrect bug reports
3. Test Generation Accuracy (TGA) - % of compilable test files
4. Cost per PR - average USD cost per bug analysis
5. Mean Time to Report (MTTR) - average seconds per bug
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Tuple
import pandas as pd


def calculate_bdr(results: List[Dict]) -> float:
    """
    Bug Detection Rate = (bugs where test_passed_on_buggy == False) / total
    
    Args:
        results: List of pipeline result dicts
        
    Returns:
        BDR as fraction (0.0-1.0)
    """
    if not results:
        return 0.0
    
    detected = sum(1 for r in results if r.get("test_passed_on_buggy") == False)
    return detected / len(results)


def calculate_fpr(results: List[Dict]) -> float:
    """
    False Positive Rate = (is_real_bug=True but ground truth says no) / total
    
    This requires manual validation. For now, return a placeholder.
    
    Args:
        results: List of pipeline result dicts
        
    Returns:
        FPR as fraction (0.0-1.0)
    """
    # Placeholder - would require manual labeling
    return 0.0


def calculate_tga(results: List[Dict]) -> float:
    """
    Test Generation Accuracy = (tests with no execution error on first attempt) / total
    
    Args:
        results: List of pipeline result dicts
        
    Returns:
        TGA as fraction (0.0-1.0)
    """
    if not results:
        return 0.0
    
    compilable = sum(1 for r in results if r.get("retry_count", 0) == 0)
    return compilable / len(results)


def calculate_avg_cost(results: List[Dict]) -> float:
    """
    Average cost per PR in USD.
    
    Args:
        results: List of pipeline result dicts
        
    Returns:
        Average USD cost
    """
    if not results:
        return 0.0
    
    costs = [r.get("cost_usd", 0.0) for r in results if r.get("cost_usd")]
    return sum(costs) / len(results) if costs else 0.0


def calculate_mttr(results: List[Dict]) -> float:
    """
    Mean Time to Report - average wall-clock seconds per bug.
    
    Args:
        results: List of pipeline result dicts
        
    Returns:
        Average seconds
    """
    if not results:
        return 0.0
    
    times = [r.get("mttr_seconds", 0.0) for r in results if r.get("mttr_seconds")]
    return sum(times) / len(times) if times else 0.0


def load_pipeline_results(results_path: str) -> List[Dict]:
    """
    Load pipeline results from JSONL file.
    
    Args:
        results_path: Path to pipeline_outputs.jsonl
        
    Returns:
        List of result dicts
    """
    results = []
    if os.path.exists(results_path):
        with open(results_path) as f:
            for line in f:
                if line.strip():
                    results.append(json.loads(line))
    return results


def generate_kpi_summary(results_path: str, output_csv: str) -> Dict:
    """
    Calculate all KPIs and write to CSV.
    
    Args:
        results_path: Path to pipeline_outputs.jsonl
        output_csv: Path to write KPI summary CSV
        
    Returns:
        Dictionary of KPI values
    """
    results = load_pipeline_results(results_path)
    
    kpis = {
        "Bug Detection Rate (%)": calculate_bdr(results) * 100,
        "False Positive Rate (%)": calculate_fpr(results) * 100,
        "Test Generation Accuracy (%)": calculate_tga(results) * 100,
        "Avg Cost per Bug (USD)": calculate_avg_cost(results),
        "Mean Time to Report (sec)": calculate_mttr(results),
        "Total Bugs Analyzed": len(results),
    }
    
    # Write to CSV
    df = pd.DataFrame([kpis])
    df.to_csv(output_csv, index=False)
    print(f"KPI summary written to {output_csv}")
    
    return kpis


if __name__ == "__main__":
    results_path = os.getenv("RESULTS_PATH", "./evaluation/results") + "/pipeline_outputs.jsonl"
    output_csv = os.getenv("RESULTS_PATH", "./evaluation/results") + "/kpi_summary.csv"
    
    kpis = generate_kpi_summary(results_path, output_csv)
    
    print("\nKPI Summary:")
    for key, value in kpis.items():
        print(f"  {key}: {value:.2f}")
