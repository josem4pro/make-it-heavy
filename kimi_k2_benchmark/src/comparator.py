"""Comparator module for aggregating and comparing benchmark metrics"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import statistics


def load_raw_results(results_dir: str = "results/raw") -> List[Dict[str, Any]]:
    """Load all raw result files from directory"""
    results = []
    results_path = Path(results_dir)

    if not results_path.exists():
        return results

    for file_path in results_path.glob("*.json"):
        with open(file_path, "r") as f:
            results.append(json.load(f))

    return results


def aggregate_metrics(results_dir: str) -> Dict[str, Dict[str, Any]]:
    """Aggregate metrics by model"""
    raw_results = load_raw_results(results_dir)

    if not raw_results:
        return {}

    # Group results by model
    model_results = {}
    for result in raw_results:
        model_id = result["model_id"]
        if model_id not in model_results:
            model_results[model_id] = []
        model_results[model_id].append(result)

    # Calculate aggregated metrics for each model
    aggregated = {}
    for model_id, results in model_results.items():
        # Filter out error results for some metrics
        valid_results = [r for r in results if "error" not in r or not r.get("error")]

        if not valid_results and all("error" in r for r in results):
            # All results have errors - model unavailable
            aggregated[model_id] = {
                "status": "unavailable",
                "avg_accuracy": 0.0,
                "avg_latency": 0.0,
                "tokens_per_second": 0.0,
                "error_rate": 1.0,
                "total_runs": len(results)
            }
        else:
            # Calculate metrics
            accuracies = [r.get("accuracy", 0.0) for r in results]
            latencies = [r.get("latency", 0.0) for r in results if r.get("latency", 0) > 0]
            tokens = []

            for r in valid_results:
                if r.get("latency", 0) > 0 and r.get("output_tokens", 0) > 0:
                    tokens.append(r["output_tokens"] / r["latency"])

            aggregated[model_id] = {
                "status": "available",
                "avg_accuracy": statistics.mean(accuracies) if accuracies else 0.0,
                "avg_latency": statistics.mean(latencies) if latencies else 0.0,
                "min_latency": min(latencies) if latencies else 0.0,
                "max_latency": max(latencies) if latencies else 0.0,
                "tokens_per_second": statistics.mean(tokens) if tokens else 0.0,
                "error_rate": sum(1 for r in results if "error" in r) / len(results),
                "total_runs": len(results),
                "successful_runs": len(valid_results)
            }

            # Add standard deviation if we have enough data points
            if len(accuracies) > 1:
                aggregated[model_id]["std_accuracy"] = statistics.stdev(accuracies)
            if len(latencies) > 1:
                aggregated[model_id]["std_latency"] = statistics.stdev(latencies)

    return aggregated


def create_comparison_table(aggregated: Dict[str, Dict[str, Any]]) -> str:
    """Create a comparison table in markdown format"""
    if not aggregated:
        return "No results to compare"

    # Headers
    headers = ["Model", "Status", "Avg Accuracy", "Avg Latency (s)", "Tokens/s", "Error Rate"]
    rows = []

    for model_id, metrics in aggregated.items():
        row = [
            model_id,
            metrics.get("status", "unknown"),
            f"{metrics.get('avg_accuracy', 0):.3f}",
            f"{metrics.get('avg_latency', 0):.2f}",
            f"{metrics.get('tokens_per_second', 0):.1f}",
            f"{metrics.get('error_rate', 0):.2%}"
        ]
        rows.append(row)

    # Build markdown table
    table = "| " + " | ".join(headers) + " |\n"
    table += "| " + " | ".join(["-" * len(h) for h in headers]) + " |\n"
    for row in rows:
        table += "| " + " | ".join(row) + " |\n"

    return table


def get_best_performer(aggregated: Dict[str, Dict[str, Any]], metric: str, minimize: bool = False) -> Optional[str]:
    """Identify best performing model for a given metric"""
    if not aggregated:
        return None

    valid_models = {
        model_id: metrics
        for model_id, metrics in aggregated.items()
        if metrics.get("status") != "unavailable" and metric in metrics
    }

    if not valid_models:
        return None

    if minimize:
        return min(valid_models.keys(), key=lambda m: valid_models[m][metric])
    else:
        return max(valid_models.keys(), key=lambda m: valid_models[m][metric])


def generate_summary_statistics(aggregated: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Generate summary statistics across all models"""
    if not aggregated:
        return {}

    available_models = [m for m, metrics in aggregated.items() if metrics.get("status") != "unavailable"]

    summary = {
        "total_models": len(aggregated),
        "available_models": len(available_models),
        "best_accuracy_model": get_best_performer(aggregated, "avg_accuracy"),
        "fastest_model": get_best_performer(aggregated, "avg_latency", minimize=True),
        "highest_throughput_model": get_best_performer(aggregated, "tokens_per_second")
    }

    # Calculate overall statistics
    all_accuracies = [m["avg_accuracy"] for m in aggregated.values() if "avg_accuracy" in m]
    all_latencies = [m["avg_latency"] for m in aggregated.values() if m.get("avg_latency", 0) > 0]

    if all_accuracies:
        summary["overall_avg_accuracy"] = statistics.mean(all_accuracies)
    if all_latencies:
        summary["overall_avg_latency"] = statistics.mean(all_latencies)

    return summary


if __name__ == "__main__":
    # Test aggregation when run directly
    aggregated = aggregate_metrics("results/raw")
    print("\nAggregated Metrics:")
    print(create_comparison_table(aggregated))

    summary = generate_summary_statistics(aggregated)
    print("\nSummary Statistics:")
    for key, value in summary.items():
        print(f"  {key}: {value}")