"""Model client functions for benchmark framework"""

import time
import json
import subprocess
import sys
import os
import requests
from typing import Dict, Any, Optional

# Add parent directory to import make-it-heavy modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


def call_openrouter_api(prompt: str, model: str, api_key: str, base_url: str) -> Dict[str, Any]:
    """Call OpenRouter API directly"""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(
        f"{base_url}/chat/completions",
        headers=headers,
        json=data,
        timeout=120
    )

    if response.status_code != 200:
        raise Exception(f"API error: {response.status_code} - {response.text}")

    return response.json()


def run_kimi_direct(prompt: str, timeout: int = 120, **kwargs) -> Dict[str, Any]:
    """Run Kimi K2 Thinking directly via OpenRouter"""
    try:
        start_time = time.time()

        # Load config to get API key
        import yaml
        with open("config/models.yaml", "r") as f:
            models_config = yaml.safe_load(f)

        kimi_config = models_config["models"]["kimi_k2_direct"]

        response = call_openrouter_api(
            prompt=prompt,
            model=kimi_config["model"],
            api_key=kimi_config["api_key"],
            base_url=kimi_config["base_url"]
        )

        latency = time.time() - start_time

        completion = response["choices"][0]["message"]["content"]

        # Extract reasoning if available (for Kimi K2 Thinking model)
        reasoning = None
        if "thinking" in response.get("choices", [{}])[0].get("message", {}):
            reasoning = response["choices"][0]["message"]["thinking"]

        return {
            "completion": completion,
            "reasoning": reasoning,
            "latency": latency,
            "meta": {
                "model": kimi_config["model"],
                "provider": "openrouter",
                "usage": response.get("usage", {})
            }
        }

    except TimeoutError:
        return {
            "error": "Request timeout",
            "completion": None,
            "latency": timeout,
            "meta": {}
        }
    except Exception as e:
        return {
            "error": str(e),
            "completion": None,
            "latency": time.time() - start_time if 'start_time' in locals() else 0,
            "meta": {}
        }


def run_kimi_via_make_it_heavy(prompt: str, **kwargs) -> Dict[str, Any]:
    """Run Kimi K2 via make-it-heavy orchestrator with 8 agents"""
    try:
        start_time = time.time()

        # Import orchestrator from make-it-heavy
        from orchestrator import TaskOrchestrator

        orchestrator = TaskOrchestrator(config_path="../config.yaml", silent=True)

        # Run orchestration
        result = orchestrator.orchestrate(prompt)

        latency = time.time() - start_time

        return {
            "completion": result,
            "reasoning": None,  # Multi-agent doesn't expose individual reasoning
            "latency": latency,
            "meta": {
                "model": "moonshotai/kimi-k2-thinking",
                "provider": "make_it_heavy",
                "agent_count": 8
            }
        }

    except Exception as e:
        return {
            "error": str(e),
            "completion": None,
            "latency": time.time() - start_time if 'start_time' in locals() else 0,
            "meta": {"agent_count": 8}
        }


def run_qwen_coder(prompt: str, **kwargs) -> Dict[str, Any]:
    """Run Qwen3-Coder:30B via Ollama"""
    try:
        start_time = time.time()

        # Check if Ollama is available
        try:
            check_result = subprocess.run(
                ["curl", "-s", "http://localhost:11434/api/tags"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if check_result.returncode != 0:
                raise Exception("Ollama not available")

        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            return {
                "error": "Model not available",
                "completion": None,
                "latency": 0,
                "meta": {"model": "qwen3-coder:30b"}
            }

        # Call Ollama API
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "qwen3-coder:30b",
                "prompt": prompt,
                "stream": False
            },
            timeout=180
        )

        if response.status_code != 200:
            raise Exception(f"Ollama error: {response.status_code}")

        result = response.json()
        latency = time.time() - start_time

        return {
            "completion": result.get("response", ""),
            "reasoning": None,
            "latency": latency,
            "meta": {
                "model": "qwen3-coder:30b",
                "provider": "ollama",
                "total_duration": result.get("total_duration"),
                "load_duration": result.get("load_duration"),
                "prompt_eval_count": result.get("prompt_eval_count"),
                "eval_count": result.get("eval_count")
            }
        }

    except Exception as e:
        return {
            "error": "Model not available",
            "completion": None,
            "latency": time.time() - start_time if 'start_time' in locals() else 0,
            "meta": {"model": "qwen3-coder:30b", "error_detail": str(e)}
        }