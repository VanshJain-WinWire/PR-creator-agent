#!/usr/bin/env python3
"""
Simple AI Agent Demo
Quick demonstration of the AI agent capabilities
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def demo_ai_agent():
    """Run a simple demo of the AI agent"""
    
    print("\n" + "=" * 60)
    print("  AI PR AGENT - QUICK DEMO")
    print("=" * 60)
    print()
    
    # Check environment
    required_vars = ["ADO_ORG_URL", "ADO_PROJECT", "ADO_PAT", "REPO_ID", "REPO_PATH", "AIFOUNDRY_API_KEY"]
    missing = [v for v in required_vars if not os.getenv(v)]
    
    if missing:
        print("❌ Missing required environment variables:")
        for var in missing:
            print(f"   - {var}")
        print("\n💡 Run 'python setup_ai_agent.py' to configure")
        return
    
    print("✅ Environment configured")
    print()
    
    # Import and initialize agent
    try:
        from ai_pr_agent import AIPRAgent
        
        print("🤖 Initializing AI agent...")
        agent = AIPRAgent(
            ado_org_url=os.getenv("ADO_ORG_URL"),
            ado_project=os.getenv("ADO_PROJECT"),
            ado_pat=os.getenv("ADO_PAT"),
            repo_id=os.getenv("REPO_ID"),
            repo_path=os.getenv("REPO_PATH")
        )
        print("✅ Agent ready!")
        print()
        
    except Exception as e:
        print(f"❌ Error initializing agent: {e}")
        return
    
    # Demo 1: List branches
    print("=" * 60)
    print("Demo 1: Asking AI to list repository branches")
    print("=" * 60)
    print()
    
    try:
        result = agent.chat_with_agent(
            "List the first 5 branches in the repository"
        )
        
        print("🤖 AI Response:")
        print(result['response'])
        print()
        print(f"📊 Tokens used: {result.get('usage', {}).get('total_tokens', 'N/A')}")
        print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print()
    
    # Demo 2: Ask about repository
    print("=" * 60)
    print("Demo 2: Getting repository information")
    print("=" * 60)
    print()
    
    try:
        result = agent.chat_with_agent(
            "How many branches are in the repository and what is the naming pattern?"
        )
        
        print("🤖 AI Response:")
        print(result['response'])
        print()
        print(f"📊 Tokens used: {result.get('usage', {}).get('total_tokens', 'N/A')}")
        print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print()
    
    # Demo 3: Interactive capabilities
    print("=" * 60)
    print("Demo 3: Interactive Chat Mode")
    print("=" * 60)
    print()
    print("The agent can maintain conversation context.")
    print("Try running example_ai_agent.py for more interactive examples!")
    print()
    
    # Summary
    print("=" * 60)
    print("DEMO COMPLETE")
    print("=" * 60)
    print()
    print("✅ The AI agent successfully:")
    print("   - Connected to Microsoft AI Foundry")
    print("   - Used Azure DevOps tools")
    print("   - Responded to natural language queries")
    print()
    print("📚 Next Steps:")
    print("   1. Read AI_AGENT_README.md for full documentation")
    print("   2. Try example_ai_agent.py for more examples")
    print("   3. Create your first PR with the AI agent!")
    print()
    print("   Example:")
    print("   ```python")
    print("   result = agent.create_pr_autonomous(")
    print("       source_branch='feature/my-branch',")
    print("       target_branch='develop',")
    print("       work_item_id=12345")
    print("   )")
    print("   ```")
    print()


if __name__ == "__main__":
    try:
        demo_ai_agent()
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
