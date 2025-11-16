"""Evaluator module for running benchmarks and calculating metrics"""

import os
import json
import time
import yaml
from datetime import datetime
from typing import Dict, Any, List, Tuple, Optional
from pathlib import Path

from . import model_clients


def load_configs() -> Tuple[Dict, Dict, Dict]:
    """Load configuration files"""
    config_dir = Path("config")

    with open(config_dir / "models.yaml", "r") as f:
        models = yaml.safe_load(f)

    with open(config_dir / "benchmarks.yaml", "r") as f:
        benchmarks = yaml.safe_load(f)

    with open(config_dir / "metrics.yaml", "r") as f:
        metrics = yaml.safe_load(f)

    return models, benchmarks, metrics


def calculate_accuracy(response: str, ground_truth: Any) -> float:
    """Calculate accuracy for tasks with ground truth"""
    if response is None:
        return 0.0

    # Clean response
    response = response.strip().lower()

    # Handle numerical ground truth
    if isinstance(ground_truth, (int, float)):
        # Try to extract number from response
        import re
        numbers = re.findall(r'-?\d+\.?\d*', response)
        if numbers:
            try:
                response_num = float(numbers[0])
                return 1.0 if abs(response_num - ground_truth) < 0.01 else 0.0
            except:
                return 0.0
        return 0.0

    # Handle string ground truth
    if isinstance(ground_truth, str):
        ground_truth = ground_truth.strip().lower()
        return 1.0 if ground_truth in response or response in ground_truth else 0.0

    return 0.0


def evaluate_qualitative_task(response: str, task_spec: Dict) -> float:
    """Evaluate tasks without ground truth using criteria"""
    if response is None:
        return 0.0

    criteria = task_spec.get("evaluation_criteria", [])
    if not criteria:
        return 0.5  # Default score if no criteria

    score = 0.0
    response_lower = response.lower()

    for criterion in criteria:
        # Simple keyword matching for criteria
        criterion_lower = criterion.lower()
        key_terms = [
            term.strip() for term in criterion_lower.replace(",", " ").split()
            if len(term.strip()) > 2
        ]

        # Check if key terms appear in response
        matches = sum(1 for term in key_terms if term in response_lower)
        if matches >= len(key_terms) * 0.5:  # At least half the terms match
            score += 1.0

    return score / len(criteria) if criteria else 0.5


def run_single_benchmark_case(model_id: str, task_spec: Dict) -> Dict[str, Any]:
    """Run a single benchmark case (one model, one task)"""
    result = {
        "model_id": model_id,
        "task_id": task_spec["id"],
        "category": task_spec.get("category", "unknown"),
        "timestamp": datetime.now().isoformat()
    }

    try:
        # Select appropriate client function
        if model_id == "kimi_k2_direct":
            response_data = model_clients.run_kimi_direct(task_spec["prompt"])
        elif model_id == "kimi_k2_via_make_it_heavy":
            response_data = model_clients.run_kimi_via_make_it_heavy(task_spec["prompt"])
        elif model_id == "qwen3_coder_30b":
            response_data = model_clients.run_qwen_coder(task_spec["prompt"])
        else:
            raise ValueError(f"Unknown model: {model_id}")

        # Check for errors
        if "error" in response_data:
            result["error"] = response_data["error"]
            result["accuracy"] = 0.0
            result["latency"] = response_data.get("latency", 0)
            result["completion"] = None
        else:
            result["completion"] = response_data["completion"]
            result["latency"] = response_data["latency"]
            result["meta"] = response_data.get("meta", {})

            # Calculate accuracy
            if task_spec.get("has_ground_truth"):
                result["accuracy"] = calculate_accuracy(
                    response_data["completion"],
                    task_spec.get("ground_truth")
                )
            else:
                result["qualitative_score"] = evaluate_qualitative_task(
                    response_data["completion"],
                    task_spec
                )
                result["accuracy"] = result["qualitative_score"]  # For consistency

            # Estimate tokens (rough approximation)
            if response_data["completion"]:
                # Rough estimate: 1 token ≈ 4 characters
                result["output_tokens"] = len(response_data["completion"]) // 4

    except Exception as e:
        result["error"] = str(e)
        result["accuracy"] = 0.0
        result["latency"] = 0
        result["completion"] = None

    # Save result to file
    os.makedirs("results/raw", exist_ok=True)
    filename = f"results/raw/{model_id}_{task_spec['id']}_{int(time.time())}.json"
    with open(filename, "w") as f:
        json.dump(result, f, indent=2)

    return result


def run_all_benchmarks() -> List[Dict[str, Any]]:
    """Run all benchmark combinations"""
    models, benchmarks, metrics = load_configs()

    all_results = []

    for model_id in models["models"].keys():
        for task in benchmarks["benchmarks"]:
            print(f"Running: {model_id} on {task['id']}...")
            result = run_single_benchmark_case(model_id, task)
            all_results.append(result)
            print(f"  Completed - Accuracy: {result.get('accuracy', 0):.2f}, "
                  f"Latency: {result.get('latency', 0):.2f}s")

    return all_results


if __name__ == "__main__":
    # Run all benchmarks when executed directly
    results = run_all_benchmarks()
    print(f"\nCompleted {len(results)} benchmark runs")
    print(f"Results saved to results/raw/")