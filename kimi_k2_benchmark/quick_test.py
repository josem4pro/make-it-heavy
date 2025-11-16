#!/usr/bin/env python3
"""
Quick test script - runs 1 task with 2 models for verification
"""

import sys
import os
import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src import evaluator


def quick_test():
    """Run a quick test with minimal benchmarks"""
    print("\n🧪 QUICK TEST - 1 task, 2 models")
    print("-" * 40)

    # Load configs
    with open("config/benchmarks.yaml", "r") as f:
        benchmarks = yaml.safe_load(f)

    # Test with first task and first two models
    test_task = benchmarks["benchmarks"][0]  # First task only
    test_models = ["kimi_k2_direct", "kimi_k2_via_make_it_heavy"]

    results = []
    for model_id in test_models:
        print(f"\n Testing {model_id} on {test_task['id']}...")
        try:
            result = evaluator.run_single_benchmark_case(model_id, test_task)
            results.append(result)
            print(f"  ✅ Completed - Accuracy: {result.get('accuracy', 0):.2f}")
        except Exception as e:
            print(f"  ❌ Error: {e}")

    print("\n" + "-" * 40)
    print(f"Quick test completed: {len(results)} successful runs")
    return results


if __name__ == "__main__":
    results = quick_test()