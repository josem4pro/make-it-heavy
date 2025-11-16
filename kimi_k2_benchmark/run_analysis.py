#!/usr/bin/env python3
"""
Run analysis on benchmark results
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src import comparator, reporter
from datetime import datetime


def main():
    print("\n" + "="*60)
    print(" BENCHMARK ANALYSIS")
    print("="*60)

    # Aggregate metrics
    print("\n📊 Aggregating Metrics...")
    aggregated = comparator.aggregate_metrics("results/raw")

    # Print comparison table
    print("\n" + comparator.create_comparison_table(aggregated))

    # Print summary statistics
    summary = comparator.generate_summary_statistics(aggregated)
    print("\n📈 Summary Statistics:")
    for key, value in summary.items():
        print(f"  • {key}: {value}")

    # Generate reports
    print("\n📝 Generating Reports...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Generate markdown report
    report_path = f"results/analysis/benchmark_report_{timestamp}.md"
    reporter.generate_markdown_report(aggregated, report_path)

    # Save JSON backup
    json_path = f"results/analysis/benchmark_data_{timestamp}.json"
    reporter.save_json_backup(aggregated, json_path)

    print(f"\n✅ Analysis complete!")
    print(f"  • Report: {report_path}")
    print(f"  • Data: {json_path}")

    return aggregated


if __name__ == "__main__":
    results = main()