import pytest
import sys
import os
import json
from unittest.mock import Mock, patch, mock_open

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import comparator


class TestComparator:
    """Test comparator functions for aggregating metrics"""

    def test_aggregate_metrics_calculates_averages(self):
        """Test that aggregate_metrics correctly calculates averages per model"""
        raw_results = [
            {"model_id": "kimi_k2_direct", "accuracy": 1.0, "latency": 2.0},
            {"model_id": "kimi_k2_direct", "accuracy": 0.5, "latency": 3.0},
            {"model_id": "kimi_k2_via_make_it_heavy", "accuracy": 0.8, "latency": 5.0},
            {"model_id": "kimi_k2_via_make_it_heavy", "accuracy": 0.6, "latency": 4.0}
        ]

        with patch('src.comparator.load_raw_results') as mock_load:
            mock_load.return_value = raw_results

            aggregated = comparator.aggregate_metrics("results/raw")

            assert "kimi_k2_direct" in aggregated
            assert "kimi_k2_via_make_it_heavy" in aggregated

            # Check averages
            assert aggregated["kimi_k2_direct"]["avg_accuracy"] == 0.75
            assert aggregated["kimi_k2_direct"]["avg_latency"] == 2.5
            assert aggregated["kimi_k2_via_make_it_heavy"]["avg_accuracy"] == 0.7
            assert aggregated["kimi_k2_via_make_it_heavy"]["avg_latency"] == 4.5

    def test_calculate_tokens_per_second(self):
        """Test tokens/second calculation"""
        raw_results = [
            {
                "model_id": "kimi_k2_direct",
                "latency": 2.0,
                "output_tokens": 100
            }
        ]

        with patch('src.comparator.load_raw_results') as mock_load:
            mock_load.return_value = raw_results

            aggregated = comparator.aggregate_metrics("results/raw")

            assert "tokens_per_second" in aggregated["kimi_k2_direct"]
            assert aggregated["kimi_k2_direct"]["tokens_per_second"] == 50.0

    def test_handle_missing_model_results(self):
        """Test handling of models with no results (e.g., unavailable)"""
        raw_results = [
            {"model_id": "kimi_k2_direct", "accuracy": 1.0, "latency": 2.0},
            {"model_id": "qwen3_coder_30b", "error": "Model not available"}
        ]

        with patch('src.comparator.load_raw_results') as mock_load:
            mock_load.return_value = raw_results

            aggregated = comparator.aggregate_metrics("results/raw")

            assert "kimi_k2_direct" in aggregated
            assert "qwen3_coder_30b" in aggregated
            assert aggregated["qwen3_coder_30b"]["status"] == "unavailable"
            assert aggregated["qwen3_coder_30b"]["avg_accuracy"] == 0.0

    def test_create_comparison_table(self):
        """Test creation of comparison table"""
        aggregated = {
            "kimi_k2_direct": {
                "avg_accuracy": 0.75,
                "avg_latency": 2.5,
                "tokens_per_second": 50
            },
            "kimi_k2_via_make_it_heavy": {
                "avg_accuracy": 0.7,
                "avg_latency": 4.5,
                "tokens_per_second": 30
            }
        }

        table = comparator.create_comparison_table(aggregated)

        assert isinstance(table, str)
        assert "kimi_k2_direct" in table
        assert "kimi_k2_via_make_it_heavy" in table
        assert "0.75" in table
        assert "0.7" in table

    def test_calculate_statistics(self):
        """Test calculation of additional statistics (std dev, min, max)"""
        raw_results = [
            {"model_id": "kimi_k2_direct", "latency": 1.0},
            {"model_id": "kimi_k2_direct", "latency": 3.0},
            {"model_id": "kimi_k2_direct", "latency": 2.0}
        ]

        with patch('src.comparator.load_raw_results') as mock_load:
            mock_load.return_value = raw_results

            aggregated = comparator.aggregate_metrics("results/raw")

            assert "min_latency" in aggregated["kimi_k2_direct"]
            assert "max_latency" in aggregated["kimi_k2_direct"]
            assert aggregated["kimi_k2_direct"]["min_latency"] == 1.0
            assert aggregated["kimi_k2_direct"]["max_latency"] == 3.0

    def test_identify_best_performer(self):
        """Test identification of best performing model"""
        aggregated = {
            "model_a": {"avg_accuracy": 0.8, "avg_latency": 2.0},
            "model_b": {"avg_accuracy": 0.9, "avg_latency": 3.0},
            "model_c": {"avg_accuracy": 0.7, "avg_latency": 1.5}
        }

        best_accuracy = comparator.get_best_performer(aggregated, "avg_accuracy")
        best_latency = comparator.get_best_performer(aggregated, "avg_latency", minimize=True)

        assert best_accuracy == "model_b"
        assert best_latency == "model_c"