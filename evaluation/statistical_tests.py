"""
Statistical tests for comparing ASQA against baselines.

Tests:
- McNemar's test for binary KPIs (BDR, FPR)
- Wilcoxon signed-rank test for continuous KPIs (Cost, MTTR)
"""

import json
import os
from typing import Dict, Tuple
import pandas as pd
from scipy.stats import wilcoxon
from statsmodels.stats.contingency_tables import mcnemar


def mcnemar_test(asqa_detected: list, baseline_detected: list, alpha: float = 0.05) -> Dict:
    """
    McNemar's test - compare binary outcomes (detected/missed).
    
    Args:
        asqa_detected: List of bool for ASQA bug detection
        baseline_detected: List of bool for baseline bug detection
        alpha: Significance level (default 0.05)
        
    Returns:
        Dictionary with test statistic, p-value, result
    """
    # Contingency table:
    # ASQA detected, baseline detected: a
    # ASQA detected, baseline missed: b
    # ASQA missed, baseline detected: c
    # ASQA missed, baseline missed: d
    
    a = sum(1 for asqa, baseline in zip(asqa_detected, baseline_detected)
            if asqa and baseline)
    b = sum(1 for asqa, baseline in zip(asqa_detected, baseline_detected)
            if asqa and not baseline)
    c = sum(1 for asqa, baseline in zip(asqa_detected, baseline_detected)
            if not asqa and baseline)
    d = sum(1 for asqa, baseline in zip(asqa_detected, baseline_detected)
            if not asqa and not baseline)
    
    table = [[a, b], [c, d]]
    
    try:
        result = mcnemar(table, exact=True)
        
        return {
            "test": "McNemar's Test",
            "statistic": result.statistic,
            "pvalue": result.pvalue,
            "significant": result.pvalue < alpha,
            "contingency_table": table,
        }
    except Exception as e:
        return {
            "test": "McNemar's Test",
            "error": str(e),
        }


def wilcoxon_test(asqa_values: list, baseline_values: list, alpha: float = 0.05) -> Dict:
    """
    Wilcoxon signed-rank test - compare continuous outcomes.
    
    Args:
        asqa_values: List of continuous values for ASQA
        baseline_values: List of continuous values for baseline
        alpha: Significance level (default 0.05)
        
    Returns:
        Dictionary with test statistic, p-value, result
    """
    if len(asqa_values) != len(baseline_values):
        raise ValueError("Lists must have same length")
    
    diffs = [a - b for a, b in zip(asqa_values, baseline_values)]
    
    try:
        result = wilcoxon(diffs, alternative='two-sided')
        
        return {
            "test": "Wilcoxon Signed-Rank Test",
            "statistic": result.statistic,
            "pvalue": result.pvalue,
            "significant": result.pvalue < alpha,
            "mean_diff": sum(diffs) / len(diffs),
        }
    except Exception as e:
        return {
            "test": "Wilcoxon Signed-Rank Test",
            "error": str(e),
        }


def compare_systems(asqa_results: list, baseline_results: list, output_file: str) -> None:
    """
    Run all statistical tests comparing ASQA to baseline.
    
    Args:
        asqa_results: List of ASQA result dicts
        baseline_results: List of baseline result dicts
        output_file: Path to write results
    """
    # Extract detected/missed for BDR comparison
    asqa_detected = [r.get("test_passed_on_buggy") == False for r in asqa_results]
    baseline_detected = [r.get("test_passed_on_buggy") == False for r in baseline_results]
    
    # Extract costs
    asqa_costs = [r.get("cost_usd", 0) for r in asqa_results]
    baseline_costs = [r.get("cost_usd", 0) for r in baseline_results]
    
    # Extract times
    asqa_times = [r.get("mttr_seconds", 0) for r in asqa_results]
    baseline_times = [r.get("mttr_seconds", 0) for r in baseline_results]
    
    results = {
        "bdr_mcnemar": mcnemar_test(asqa_detected, baseline_detected),
        "cost_wilcoxon": wilcoxon_test(asqa_costs, baseline_costs),
        "mttr_wilcoxon": wilcoxon_test(asqa_times, baseline_times),
    }
    
    # Write results
    with open(output_file, "w") as f:
        f.write("Statistical Test Results\n")
        f.write("=" * 60 + "\n\n")
        
        for test_name, test_result in results.items():
            f.write(f"{test_name}:\n")
            for key, value in test_result.items():
                f.write(f"  {key}: {value}\n")
            f.write("\n")
    
    print(f"Statistical test results written to {output_file}")


if __name__ == "__main__":
    # Example usage
    asqa_results = [
        {"bug_id": "b1", "test_passed_on_buggy": False, "cost_usd": 0.03, "mttr_seconds": 45},
        {"bug_id": "b2", "test_passed_on_buggy": True, "cost_usd": 0.02, "mttr_seconds": 30},
    ]
    
    baseline_results = [
        {"bug_id": "b1", "test_passed_on_buggy": True, "cost_usd": 0.05, "mttr_seconds": 60},
        {"bug_id": "b2", "test_passed_on_buggy": True, "cost_usd": 0.04, "mttr_seconds": 50},
    ]
    
    compare_systems(
        asqa_results,
        baseline_results,
        "./evaluation/results/statistical_tests.txt"
    )
