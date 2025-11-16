#!/usr/bin/env python3

import sys
import os

# Add current directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from orchestrator import TaskOrchestrator

def test_multi_agent():
    """Test multi-agent orchestration with a more complex query"""
    print("\n🚀 Testing Multi-Agent Orchestration with Kimi K2 Thinking...")

    orchestrator = TaskOrchestrator()

    query = "Compara Kimi K2 Thinking con qwen3-coder:30b para tareas de codificación compleja."

    print(f"📝 Query: {query}")
    print("-" * 50)

    result = orchestrator.orchestrate(query)

    if result:
        print("\n✅ Synthesized Response received:")
        print(result)
        return True
    else:
        print("❌ Failed to get response")
        return False

if __name__ == "__main__":
    success = test_multi_agent()
    sys.exit(0 if success else 1)