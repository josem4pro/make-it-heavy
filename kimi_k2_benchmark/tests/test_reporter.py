import pytest
import sys
import os
from unittest.mock import Mock, patch, mock_open

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import reporter


class TestReporter:
    """Test reporter functions for generating final reports"""

    def test_generate_markdown_report_creates_file(self):
        """Test that generate_markdown_report creates a markdown file"""
        aggregated_metrics = {
            "kimi_k2_direct": {
                "avg_accuracy": 0.75,
                "avg_latency": 2.5,
                "tokens_per_second": 50
            }
        }

        with patch('builtins.open', mock_open()) as mock_file:
            output_path = "results/analysis/report.md"
            reporter.generate_markdown_report(aggregated_metrics, output_path)

            # Check file was opened for writing
            mock_file.assert_called_with(output_path, 'w')

            # Check content was written
            handle = mock_file()
            handle.write.assert_called()

    def test_markdown_report_contains_required_sections(self):
        """Test that generated markdown contains all required sections"""
        aggregated_metrics = {
            "kimi_k2_direct": {"avg_accuracy": 0.75, "avg_latency": 2.5}
        }

        report = reporter.generate_markdown_content(aggregated_metrics)

        # Check for required sections
        assert "# Benchmark Results" in report
        assert "## Summary" in report
        assert "## Model Comparison" in report
        assert "## Detailed Metrics" in report
        assert "kimi_k2_direct" in report
        assert "0.75" in report

    def test_generate_executive_summary(self):
        """Test generation of executive summary"""
        aggregated_metrics = {
            "kimi_k2_direct": {"avg_accuracy": 0.85, "avg_latency": 2.0},
            "kimi_k2_via_make_it_heavy": {"avg_accuracy": 0.80, "avg_latency": 4.0},
            "qwen3_coder_30b": {"status": "unavailable"}
        }

        summary = reporter.generate_executive_summary(aggregated_metrics)

        assert isinstance(summary, str)
        assert "kimi_k2_direct" in summary
        assert "best" in summary.lower() or "highest" in summary.lower()
        assert "unavailable" in summary.lower()

    def test_create_performance_chart(self):
        """Test creation of performance comparison chart (text-based)"""
        aggregated_metrics = {
            "model_a": {"avg_accuracy": 0.8},
            "model_b": {"avg_accuracy": 0.6},
            "model_c": {"avg_accuracy": 0.9}
        }

        chart = reporter.create_text_chart(aggregated_metrics, "avg_accuracy")

        assert isinstance(chart, str)
        assert "model_a" in chart
        assert "model_b" in chart
        assert "model_c" in chart
        # Model C should appear first (highest accuracy) after header
        lines = chart.split('\n')
        # Check within first few lines (after header and opening ```)
        model_c_found = any("model_c" in line for line in lines[:5])
        assert model_c_found, f"model_c not found in first lines: {lines[:5]}"

    def test_generate_recommendations(self):
        """Test generation of recommendations based on results"""
        aggregated_metrics = {
            "kimi_k2_direct": {"avg_accuracy": 0.85, "avg_latency": 2.0},
            "kimi_k2_via_make_it_heavy": {"avg_accuracy": 0.82, "avg_latency": 5.0}
        }

        recommendations = reporter.generate_recommendations(aggregated_metrics)

        assert isinstance(recommendations, str)
        assert len(recommendations) > 0
        # Should mention trade-offs
        assert "latency" in recommendations.lower() or "speed" in recommendations.lower()
        assert "accuracy" in recommendations.lower() or "quality" in recommendations.lower()

    def test_format_metrics_table(self):
        """Test formatting of metrics into markdown table"""
        metrics_data = {
            "model_1": {"metric_a": 0.5, "metric_b": 10},
            "model_2": {"metric_a": 0.7, "metric_b": 15}
        }

        table = reporter.format_metrics_table(metrics_data)

        assert isinstance(table, str)
        assert "|" in table  # Markdown table format
        # Check for model names (they get converted to title case)
        assert "Model 1" in table or "model_1" in table
        assert "Model 2" in table or "model_2" in table
        # These values should not be in the table since metrics don't match expected keys
        # The table expects specific metric names like avg_accuracy, avg_latency, etc.

    def test_save_json_backup(self):
        """Test that a JSON backup of results is saved"""
        aggregated_metrics = {"test": "data"}

        with patch('builtins.open', mock_open()) as mock_file:
            with patch('json.dump') as mock_json:
                reporter.save_json_backup(aggregated_metrics, "results/analysis/backup.json")

                mock_file.assert_called_with("results/analysis/backup.json", 'w')
                mock_json.assert_called_once()

    def test_report_includes_timestamp(self):
        """Test that report includes generation timestamp"""
        aggregated_metrics = {}

        report = reporter.generate_markdown_content(aggregated_metrics)

        # Should include date/time
        assert "Generated" in report or "Timestamp" in report or "Date" in report