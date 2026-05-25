"""
AI PR Agent - Example Usage
Demonstrates how to use the AI-powered PR creation with Microsoft AI Foundry
"""
import os
from dotenv import load_dotenv
from ai_pr_agent import AIPRAgent, create_ai_pr

# Load environment variables
load_dotenv()


def example_1_basic_pr_creation():
    """Example 1: Basic autonomous PR creation"""
    print("=" * 60)
    print("Example 1: Basic Autonomous PR Creation")
    print("=" * 60)
    print()
    
    # Initialize AI PR Agent
    agent = AIPRAgent(
        ado_org_url=os.getenv("ADO_ORG_URL"),
        ado_project=os.getenv("ADO_PROJECT"),
        ado_pat=os.getenv("ADO_PAT"),
        repo_id=os.getenv("REPO_ID"),
        repo_path=os.getenv("REPO_PATH")
    )
    
    # Let AI agent autonomously create a PR
    result = agent.create_pr_autonomous(
        source_branch="feature/user-authentication",
        target_branch="develop",
        work_item_id=12345
    )
    
    print("Result:", result)


def example_2_with_instructions():
    """Example 2: PR creation with custom instructions"""
    print("=" * 60)
    print("Example 2: PR with Custom Instructions")
    print("=" * 60)
    print()
    
    agent = AIPRAgent(
        ado_org_url=os.getenv("ADO_ORG_URL"),
        ado_project=os.getenv("ADO_PROJECT"),
        ado_pat=os.getenv("ADO_PAT"),
        repo_id=os.getenv("REPO_ID"),
        repo_path=os.getenv("REPO_PATH")
    )
    
    # Provide additional context for the AI
    result = agent.create_pr_autonomous(
        source_branch="bugfix/login-timeout",
        target_branch="main",
        work_item_id=9876,
        user_instructions="""
        This is a critical security fix. Please emphasize:
        - Security implications in the PR description
        - Testing requirements for security scenarios
        - Need for immediate review
        """
    )
    
    print("Result:", result)


def example_3_natural_language():
    """Example 3: Natural language PR request"""
    print("=" * 60)
    print("Example 3: Natural Language PR Request")
    print("=" * 60)
    print()
    
    agent = AIPRAgent(
        ado_org_url=os.getenv("ADO_ORG_URL"),
        ado_project=os.getenv("ADO_PROJECT"),
        ado_pat=os.getenv("ADO_PAT"),
        repo_id=os.getenv("REPO_ID"),
        repo_path=os.getenv("REPO_PATH")
    )
    
    # Let AI parse and execute the request
    result = agent.analyze_pr_request(
        "Create a PR for work item 54321 comparing feature/dashboard-redesign with develop branch"
    )
    
    print("Result:", result)


def example_4_interactive_chat():
    """Example 4: Interactive conversation with AI agent"""
    print("=" * 60)
    print("Example 4: Interactive Chat with AI Agent")
    print("=" * 60)
    print()
    
    agent = AIPRAgent(
        ado_org_url=os.getenv("ADO_ORG_URL"),
        ado_project=os.getenv("ADO_PROJECT"),
        ado_pat=os.getenv("ADO_PAT"),
        repo_id=os.getenv("REPO_ID"),
        repo_path=os.getenv("REPO_PATH")
    )
    
    # Start a conversation
    conversation = None
    
    # First message
    result1 = agent.chat_with_agent(
        "Can you tell me about work item 107295?",
        conversation_history=conversation
    )
    print("AI:", result1['response'])
    print()
    
    # Continue conversation
    result2 = agent.chat_with_agent(
        "What branches exist in the repository?",
        conversation_history=result1['conversation_history']
    )
    print("AI:", result2['response'])
    print()
    
    # Create PR in the conversation
    result3 = agent.chat_with_agent(
        "Create a PR from feature/multi-format-export-insights to develop for this work item",
        conversation_history=result2['conversation_history']
    )
    print("AI:", result3['response'])


def example_5_quick_helper():
    """Example 5: Using the convenience helper function"""
    print("=" * 60)
    print("Example 5: Quick Helper Function")
    print("=" * 60)
    print()
    
    # Quick one-liner PR creation
    result = create_ai_pr(
        work_item_id=12345,
        source_branch="feature/multi-format-export-insights",
        target_branch="develop"
    )
    
    print("Result:", result)


def example_6_check_branches():
    """Example 6: Check branches before creating PR"""
    print("=" * 60)
    print("Example 6: Branch Verification")
    print("=" * 60)
    print()
    
    agent = AIPRAgent(
        ado_org_url=os.getenv("ADO_ORG_URL"),
        ado_project=os.getenv("ADO_PROJECT"),
        ado_pat=os.getenv("ADO_PAT"),
        repo_id=os.getenv("REPO_ID"),
        repo_path=os.getenv("REPO_PATH")
    )
    
    # Ask AI to check branches first
    result = agent.chat_with_agent(
        "Can you list all branches in the repository and check if 'feature/login' exists?"
    )
    
    print("AI:", result['response'])


if __name__ == "__main__":
    import sys
    
    print("\n🤖 AI PR Agent - Example Demonstrations\n")
    
    # Check if environment variables are set
    required_vars = ["ADO_ORG_URL", "ADO_PROJECT", "ADO_PAT", "REPO_ID", "REPO_PATH", "AIFOUNDRY_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("❌ Error: Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these in your .env file")
        sys.exit(1)
    
    print("✅ All environment variables configured\n")
    
    # Run examples (comment/uncomment as needed)
    
    # Uncomment the example you want to run:
    
    # example_1_basic_pr_creation()
    # example_2_with_instructions()
    # example_3_natural_language()
    example_4_interactive_chat()
    # example_5_quick_helper()
    # example_6_check_branches()
    
    print("\n✅ Example completed successfully!")
