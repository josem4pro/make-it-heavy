#!/usr/bin/env python3
"""
Main script to run complete benchmark suite for Kimi K2 Thinking models
"""

import sys
import os
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src import evaluator, comparator, reporter


def main():
    """Main execution function"""
    print("\n" + "="*60)
    print(" KIMI K2 THINKING BENCHMARK SUITE")
    print("="*60)
    print(f"\n📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Phase 1: Run all benchmarks
    print("🚀 PHASE 1: Running Benchmarks...")
    print("-" * 40)

    try:
        results = evaluator.run_all_benchmarks()
        print(f"\n✅ Completed {len(results)} benchmark runs")
    except Exception as e:
        print(f"\n❌ Error during benchmark execution: {e}")
        return 1

    # Phase 2: Aggregate metrics
    print("\n📊 PHASE 2: Aggregating Metrics...")
    print("-" * 40)

    try:
        aggregated = comparator.aggregate_metrics("results/raw")

        # Print comparison table
        print("\n" + comparator.create_comparison_table(aggregated))

        # Print summary statistics
        summary = comparator.generate_summary_statistics(aggregated)
        print("\n📈 Summary Statistics:")
        for key, value in summary.items():
            print(f"  • {key}: {value}")

    except Exception as e:
        print(f"\n❌ Error during aggregation: {e}")
        return 1

    # Phase 3: Generate reports
    print("\n📝 PHASE 3: Generating Reports...")
    print("-" * 40)

    try:
        # Create timestamp for unique report names
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Generate markdown report
        report_path = f"results/analysis/benchmark_report_{timestamp}.md"
        reporter.generate_markdown_report(aggregated, report_path)

        # Save JSON backup
        json_path = f"results/analysis/benchmark_data_{timestamp}.json"
        reporter.save_json_backup(aggregated, json_path)

        # Also create a "latest" symlink for easy access
        latest_report = "results/analysis/latest_report.md"
        latest_json = "results/analysis/latest_data.json"

        # Create symlinks (overwrite if exists)
        if os.path.exists(latest_report):
            os.remove(latest_report)
        os.symlink(os.path.basename(report_path), latest_report)

        if os.path.exists(latest_json):
            os.remove(latest_json)
        os.symlink(os.path.basename(json_path), latest_json)

        print(f"\n✅ Reports generated successfully!")
        print(f"  • Markdown: {report_path}")
        print(f"  • JSON: {json_path}")
        print(f"  • Latest symlinks created")

    except Exception as e:
        print(f"\n❌ Error during report generation: {e}")
        return 1

    print("\n" + "="*60)
    print(" BENCHMARK COMPLETE!")
    print("="*60)
    print(f"\n📅 Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())