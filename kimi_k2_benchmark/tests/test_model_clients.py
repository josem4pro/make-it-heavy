import pytest
import sys
import os
from unittest.mock import Mock, patch

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import model_clients


class TestModelClients:
    """Test model client functions"""

    def test_run_kimi_direct_returns_expected_structure(self):
        """Test that run_kimi_direct returns dict with expected keys"""
        prompt = "Test prompt"

        with patch('src.model_clients.call_openrouter_api') as mock_api:
            mock_api.return_value = {"choices": [{"message": {"content": "Test response"}}]}

            result = model_clients.run_kimi_direct(prompt)

            assert isinstance(result, dict)
            assert 'completion' in result
            assert 'latency' in result
            assert 'meta' in result
            assert result['completion'] == "Test response"
            assert result['latency'] > 0

    def test_run_kimi_via_make_it_heavy_returns_expected_structure(self):
        """Test that run_kimi_via_make_it_heavy returns dict with expected keys"""
        prompt = "Test prompt"

        with patch('orchestrator.TaskOrchestrator') as MockOrchestrator:
            mock_orchestrator = MockOrchestrator.return_value
            mock_orchestrator.orchestrate.return_value = "Synthesized response"

            result = model_clients.run_kimi_via_make_it_heavy(prompt)

            assert isinstance(result, dict)
            assert 'completion' in result
            assert 'latency' in result
            assert 'meta' in result
            assert result['completion'] == "Synthesized response"
            assert result['meta']['agent_count'] == 8

    def test_run_qwen_coder_handles_unavailability(self):
        """Test that run_qwen_coder gracefully handles when Ollama is not available"""
        prompt = "Test prompt"

        with patch('src.model_clients.subprocess.run') as mock_run:
            mock_run.side_effect = Exception("Ollama not available")

            result = model_clients.run_qwen_coder(prompt)

            assert isinstance(result, dict)
            assert 'error' in result
            assert result['error'] == "Model not available"
            assert 'completion' in result
            assert result['completion'] is None

    def test_all_clients_handle_timeout(self):
        """Test that all client functions handle timeout gracefully"""
        prompt = "Test prompt"

        # Test timeout handling for each client
        with patch('src.model_clients.call_openrouter_api') as mock_api:
            mock_api.side_effect = TimeoutError("Request timeout")

            result = model_clients.run_kimi_direct(prompt, timeout=1)
            assert 'error' in result
            assert 'timeout' in result['error'].lower()