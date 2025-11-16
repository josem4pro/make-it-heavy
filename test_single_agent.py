#!/usr/bin/env python3

import sys
import os

# Add current directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent import OpenRouterAgent

def test_single_agent():
    """Test single agent with a simple query"""
    print("\n🔧 Testing Single Agent with Kimi K2 Thinking...")

    agent = OpenRouterAgent()

    query = "Resume en 3 líneas qué es Kimi K2 Thinking y para qué sirve."

    print(f"📝 Query: {query}")
    print("-" * 50)

    result = agent.run(query)

    if result:
        print("✅ Response received:")
        print(result)
        return True
    else:
        print("❌ Failed to get response")
        return False

if __name__ == "__main__":
    success = test_single_agent()
    sys.exit(0 if success else 1)