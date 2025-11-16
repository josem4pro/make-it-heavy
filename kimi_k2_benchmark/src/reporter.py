"""Reporter module for generating final benchmark reports"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List


def generate_markdown_content(aggregated_metrics: Dict[str, Dict[str, Any]]) -> str:
    """Generate markdown report content"""
    report = []

    # Header
    report.append("# Benchmark Results: Kimi K2 Thinking Comparison")
    report.append(f"\n**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("\n---\n")

    # Executive Summary
    report.append("## Summary")
    summary = generate_executive_summary(aggregated_metrics)
    report.append(summary)
    report.append("")

    # Model Comparison Table
    report.append("## Model Comparison")
    report.append("")
    table = format_metrics_table(aggregated_metrics)
    report.append(table)
    report.append("")

    # Detailed Metrics
    report.append("## Detailed Metrics")
    report.append("")
    for model_id, metrics in aggregated_metrics.items():
        report.append(f"### {model_id}")
        report.append("")
        for key, value in metrics.items():
            if isinstance(value, float):
                report.append(f"- **{key}**: {value:.3f}")
            else:
                report.append(f"- **{key}**: {value}")
        report.append("")

    # Performance Chart
    report.append("## Performance Visualization")
    report.append("")
    chart = create_text_chart(aggregated_metrics, "avg_accuracy")
    report.append(chart)
    report.append("")

    # Recommendations
    report.append("## Recommendations")
    recommendations = generate_recommendations(aggregated_metrics)
    report.append(recommendations)
    report.append("")

    return "\n".join(report)


def generate_executive_summary(aggregated_metrics: Dict[str, Dict[str, Any]]) -> str:
    """Generate executive summary of results"""
    summary_points = []

    # Count available models
    available = sum(1 for m in aggregated_metrics.values() if m.get("status") != "unavailable")
    total = len(aggregated_metrics)
    summary_points.append(f"- Tested **{total}** model configurations, **{available}** were available")

    # Find best accuracy
    best_accuracy = max(
        ((model, metrics["avg_accuracy"]) for model, metrics in aggregated_metrics.items()
         if "avg_accuracy" in metrics and metrics.get("status") != "unavailable"),
        key=lambda x: x[1],
        default=(None, 0)
    )
    if best_accuracy[0]:
        summary_points.append(f"- **Best accuracy**: {best_accuracy[0]} ({best_accuracy[1]:.1%})")

    # Find best latency
    best_latency = min(
        ((model, metrics["avg_latency"]) for model, metrics in aggregated_metrics.items()
         if metrics.get("avg_latency", float('inf')) > 0 and metrics.get("status") != "unavailable"),
        key=lambda x: x[1],
        default=(None, float('inf'))
    )
    if best_latency[0]:
        summary_points.append(f"- **Fastest response**: {best_latency[0]} ({best_latency[1]:.2f}s average)")

    # Check for unavailable models
    unavailable = [m for m, metrics in aggregated_metrics.items() if metrics.get("status") == "unavailable"]
    if unavailable:
        summary_points.append(f"- **Unavailable models**: {', '.join(unavailable)}")

    # Compare make-it-heavy vs direct if both available
    if "kimi_k2_direct" in aggregated_metrics and "kimi_k2_via_make_it_heavy" in aggregated_metrics:
        direct = aggregated_metrics["kimi_k2_direct"]
        heavy = aggregated_metrics["kimi_k2_via_make_it_heavy"]

        if direct.get("status") != "unavailable" and heavy.get("status") != "unavailable":
            acc_diff = heavy.get("avg_accuracy", 0) - direct.get("avg_accuracy", 0)
            lat_diff = heavy.get("avg_latency", 0) - direct.get("avg_latency", 0)

            if acc_diff > 0:
                summary_points.append(f"- **Make-it-heavy improvement**: +{acc_diff:.1%} accuracy (but +{lat_diff:.1f}s latency)")
            else:
                summary_points.append(f"- **Direct mode advantage**: Better latency (-{abs(lat_diff):.1f}s) with similar accuracy")

    return "\n".join(summary_points)


def format_metrics_table(metrics_data: Dict[str, Dict[str, Any]]) -> str:
    """Format metrics into markdown table"""
    if not metrics_data:
        return "No data available"

    # Define columns
    columns = ["Model", "Accuracy", "Latency (s)", "Tokens/s", "Error Rate", "Status"]

    # Build header
    table = "| " + " | ".join(columns) + " |\n"
    table += "|" + "|".join([" --- " for _ in columns]) + "|\n"

    # Add rows
    for model_id, metrics in metrics_data.items():
        row = [
            model_id.replace("_", " ").title(),
            f"{metrics.get('avg_accuracy', 0):.3f}",
            f"{metrics.get('avg_latency', 0):.2f}",
            f"{metrics.get('tokens_per_second', 0):.1f}",
            f"{metrics.get('error_rate', 0):.1%}",
            metrics.get("status", "unknown")
        ]
        table += "| " + " | ".join(row) + " |\n"

    return table


def create_text_chart(aggregated_metrics: Dict[str, Dict[str, Any]], metric: str) -> str:
    """Create text-based bar chart for visualization"""
    chart_lines = [f"### {metric.replace('_', ' ').title()} Comparison\n"]
    chart_lines.append("```")

    # Get values and sort
    values = []
    for model, metrics in aggregated_metrics.items():
        if metric in metrics and metrics.get("status") != "unavailable":
            values.append((model, metrics[metric]))

    values.sort(key=lambda x: x[1], reverse=True)

    if not values:
        chart_lines.append("No data available")
    else:
        # Normalize to max 50 chars width
        max_value = max(v[1] for v in values)
        if max_value > 0:
            for model, value in values:
                bar_length = int((value / max_value) * 50)
                bar = "█" * bar_length
                label = f"{model[:20]:20s}"
                chart_lines.append(f"{label} {bar} {value:.3f}")

    chart_lines.append("```")
    return "\n".join(chart_lines)


def generate_recommendations(aggregated_metrics: Dict[str, Dict[str, Any]]) -> str:
    """Generate recommendations based on results"""
    recommendations = []

    # Analyze trade-offs
    if "kimi_k2_direct" in aggregated_metrics and "kimi_k2_via_make_it_heavy" in aggregated_metrics:
        direct = aggregated_metrics["kimi_k2_direct"]
        heavy = aggregated_metrics["kimi_k2_via_make_it_heavy"]

        if direct.get("status") != "unavailable" and heavy.get("status") != "unavailable":
            # Compare accuracy
            acc_improvement = heavy.get("avg_accuracy", 0) - direct.get("avg_accuracy", 0)
            lat_increase = heavy.get("avg_latency", 0) / max(direct.get("avg_latency", 1), 0.1)

            recommendations.append("### Kimi K2: Direct vs Make-it-heavy\n")

            if acc_improvement > 0.05:  # More than 5% improvement
                recommendations.append(f"- **Use make-it-heavy** for complex tasks requiring highest accuracy "
                                       f"(+{acc_improvement:.1%} accuracy gain)")
                recommendations.append(f"- Be aware of latency trade-off ({lat_increase:.1f}x slower)")
            elif acc_improvement < -0.05:  # Direct is better
                recommendations.append(f"- **Use direct mode** for better overall performance")
                recommendations.append(f"- Direct mode provides better accuracy and {1/lat_increase:.1f}x faster response")
            else:  # Similar accuracy
                recommendations.append(f"- **Use direct mode** for most tasks (similar accuracy, {1/lat_increase:.1f}x faster)")
                recommendations.append(f"- Consider make-it-heavy only for tasks requiring multiple perspectives")

    # Check Qwen availability
    if "qwen3_coder_30b" in aggregated_metrics:
        qwen = aggregated_metrics["qwen3_coder_30b"]
        if qwen.get("status") == "unavailable":
            recommendations.append("\n### Local Model Setup")
            recommendations.append("- **Qwen3-Coder:30B** was unavailable during testing")
            recommendations.append("- To enable: Install Ollama and run `ollama pull qwen3-coder:30b`")
            recommendations.append("- Local models can provide better latency and data privacy")

    # General recommendations
    recommendations.append("\n### General Recommendations")
    recommendations.append("- For **production use**: Choose based on latency requirements vs accuracy needs")
    recommendations.append("- For **development**: Direct mode offers best balance of speed and quality")
    recommendations.append("- For **complex reasoning**: Make-it-heavy may provide marginal improvements")

    return "\n".join(recommendations)


def generate_markdown_report(aggregated_metrics: Dict[str, Dict[str, Any]], output_path: str):
    """Generate and save markdown report"""
    content = generate_markdown_content(aggregated_metrics)

    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Write report
    with open(output_path, 'w') as f:
        f.write(content)

    print(f"Report saved to: {output_path}")


def save_json_backup(aggregated_metrics: Dict[str, Dict[str, Any]], output_path: str):
    """Save JSON backup of aggregated metrics"""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(aggregated_metrics, f, indent=2)

    print(f"JSON backup saved to: {output_path}")


if __name__ == "__main__":
    # Test report generation
    test_metrics = {
        "kimi_k2_direct": {
            "avg_accuracy": 0.85,
            "avg_latency": 2.5,
            "tokens_per_second": 45,
            "error_rate": 0.0,
            "status": "available"
        },
        "kimi_k2_via_make_it_heavy": {
            "avg_accuracy": 0.82,
            "avg_latency": 8.5,
            "tokens_per_second": 25,
            "error_rate": 0.1,
            "status": "available"
        }
    }

    generate_markdown_report(test_metrics, "results/analysis/test_report.md")
    save_json_backup(test_metrics, "results/analysis/test_metrics.json")