import pytest
import sys
import os
import json
from unittest.mock import Mock, patch, mock_open

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import evaluator


class TestEvaluator:
    """Test evaluator functions"""

    def test_load_configs_returns_valid_data(self):
        """Test that load_configs properly loads YAML files"""
        models, benchmarks, metrics = evaluator.load_configs()

        assert 'models' in models
        assert 'benchmarks' in benchmarks
        assert 'metrics' in metrics

        assert len(models['models']) >= 3
        assert len(benchmarks['benchmarks']) == 5
        assert len(metrics['metrics']) >= 4

    def test_run_single_benchmark_case_creates_result_file(self):
        """Test that run_single_benchmark_case creates a result file in raw directory"""
        model_id = "kimi_k2_direct"
        task_spec = {
            "id": "test_task",
            "prompt": "Test prompt",
            "has_ground_truth": True,
            "ground_truth": 42
        }

        with patch('src.evaluator.model_clients') as mock_clients:
            mock_clients.run_kimi_direct.return_value = {
                "completion": "42",
                "latency": 2.5,
                "meta": {}
            }

            with patch('builtins.open', mock_open()) as mock_file:
                result = evaluator.run_single_benchmark_case(model_id, task_spec)

                assert isinstance(result, dict)
                assert 'accuracy' in result
                assert 'latency' in result
                assert 'task_id' in result
                assert 'model_id' in result
                assert result['accuracy'] == 1.0  # Correct answer
                assert result['latency'] == 2.5

                # Check file was written
                mock_file.assert_called()
                assert 'results/raw' in str(mock_file.call_args)

    def test_run_all_benchmarks_executes_all_combinations(self):
        """Test that run_all_benchmarks runs all model-task combinations"""
        with patch('src.evaluator.load_configs') as mock_load:
            mock_load.return_value = (
                {"models": {"kimi_k2_direct": {}, "kimi_k2_via_make_it_heavy": {}}},
                {"benchmarks": [{"id": "task1"}, {"id": "task2"}]},
                {"metrics": []}
            )

            with patch('src.evaluator.run_single_benchmark_case') as mock_run:
                mock_run.return_value = {"accuracy": 1.0, "latency": 1.0}

                results = evaluator.run_all_benchmarks()

                # 2 models × 2 tasks = 4 combinations
                assert mock_run.call_count == 4
                assert len(results) == 4

    def test_calculate_accuracy_for_ground_truth_tasks(self):
        """Test accuracy calculation for tasks with ground truth"""
        # Numerical ground truth
        result = evaluator.calculate_accuracy("42", 42)
        assert result == 1.0

        result = evaluator.calculate_accuracy("43", 42)
        assert result == 0.0

        # String ground truth (case-insensitive)
        result = evaluator.calculate_accuracy("HELLO world", "hello world")
        assert result == 1.0

    def test_evaluate_qualitative_task(self):
        """Test evaluation of tasks without ground truth using criteria"""
        task_spec = {
            "evaluation_criteria": [
                "Uses hash set",
                "O(n) time complexity",
                "Clear explanation"
            ]
        }

        response = "I use a hash set for O(n) time complexity. Here's my clear explanation..."

        score = evaluator.evaluate_qualitative_task(response, task_spec)
        assert score >= 0.66  # At least 2 out of 3 criteria met

    def test_handle_model_error_gracefully(self):
        """Test that evaluator handles model errors gracefully"""
        model_id = "qwen3_coder_30b"
        task_spec = {"id": "test", "prompt": "Test"}

        with patch('src.evaluator.model_clients.run_qwen_coder') as mock_run:
            mock_run.return_value = {"error": "Model not available", "completion": None}

            result = evaluator.run_single_benchmark_case(model_id, task_spec)

            assert result['error'] == "Model not available"
            assert result['accuracy'] == 0.0
            assert 'latency' in result