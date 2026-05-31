"""
AI PR Agent - Example Usage
Demonstrates how to use the AI-powered PR creation with Microsoft AI Foundry
"""
import os
from dotenv import load_dotenv
from ai_pr_agent import AIPRAgent

# Load environment variables
load_dotenv()


def example_1_create_pr():
    """Example 1: Create a PR with AI analysis"""
    print("=" * 60)
    print("Example 1: Create PR with AI Analysis")
    print("=" * 60)
    print()

    agent = AIPRAgent(
        ado_org_url=os.getenv("ADO_ORG_URL"),
        ado_project=os.getenv("ADO_PROJECT"),
        ado_pat=os.getenv("ADO_PAT"),
        repo_id=os.getenv("REPO_ID"),
        repo_path=os.getenv("REPO_PATH")
    )

    # AI will:
    # 1. Get work item details
    # 2. Verify branches exist
    # 3. Analyze code changes with AI
    # 4. Generate PR description in company format
    # 5. Create the PR
    result = agent.create_pr_autonomous(
        source_branch="feature/multi-format-export-insights",
        target_branch="develop",
        work_item_id=107295
    )

    print("Result:", result)


def example_2_generate_summary_only():
    """Example 2: Generate PR summary WITHOUT creating the PR"""
    print("=" * 60)
    print("Example 2: Generate PR Summary Only (No PR Creation)")
    print("=" * 60)
    print()

    agent = AIPRAgent(
        ado_org_url=os.getenv("ADO_ORG_URL"),
        ado_project=os.getenv("ADO_PROJECT"),
        ado_pat=os.getenv("ADO_PAT"),
        repo_id=os.getenv("REPO_ID"),
        repo_path=os.getenv("REPO_PATH")
    )

    # Generate summary only - no PR created
    # Useful for reviewing before creating
    result = agent.generate_pr_summary(
        source_branch="feature/multi-format-export-insights",
        target_branch="develop",
        work_item_id=107295
    )

    print("\n📋 Summary Generated!")
    print("You can now:")
    print("  1. Review the summary above")
    print("  2. Make manual adjustments if needed")
    print("  3. Use example_1_create_pr() to create the actual PR")


def example_3_interactive_chat():
    """Example 3: Interactive chat to explore and create PR"""
    print("=" * 60)
    print("Example 3: Interactive Chat")
    print("=" * 60)
    print()

    agent = AIPRAgent(
        ado_org_url=os.getenv("ADO_ORG_URL"),
        ado_project=os.getenv("ADO_PROJECT"),
        ado_pat=os.getenv("ADO_PAT"),
        repo_id=os.getenv("REPO_ID"),
        repo_path=os.getenv("REPO_PATH")
    )

    # Chat 1: Ask about work item
    result1 = agent.chat_with_agent(
        "Tell me about work item 105550"
    )
    print("AI:", result1['response'])
    print()

    # Chat 2: List branches
    result2 = agent.chat_with_agent(
        "What branches exist in the repository?",
        conversation_history=result1['conversation_history']
    )
    print("AI:", result2['response'])
    print()

    # Chat 3: Create PR
    result3 = agent.chat_with_agent(
        "Create a PR from feature/multi-format-export-insights to develop for work item 105550. Make sure to analyze the code changes first.",
        conversation_history=result2['conversation_history']
    )
    print("AI:", result3['response'])


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

    # Run examples (uncomment the one you want to run)

    # example_1_create_pr()
    # example_2_generate_summary_only()
    example_3_interactive_chat()

    print("\n✅ Example completed successfully!")
