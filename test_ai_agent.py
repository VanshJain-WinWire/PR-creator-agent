#!/usr/bin/env python3
"""
Test AI PR Agent Setup
Verifies that AI Foundry and Azure DevOps connections are working
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"), override=True)


def check_environment_variables():
    """Check if all required environment variables are set"""
    print("=" * 60)
    print("1. Checking Environment Variables")
    print("=" * 60)
    
    required_vars = {
        "ADO_ORG_URL": "Azure DevOps Organization URL",
        "ADO_PROJECT": "Azure DevOps Project",
        "ADO_PAT": "Azure DevOps Personal Access Token",
        "REPO_ID": "Repository ID",
        "REPO_PATH": "Local Repository Path",
        "AIFOUNDRY_ENDPOINT": "AI Foundry Endpoint",
        "AIFOUNDRY_API_KEY": "AI Foundry API Key (or AZURE_OPENAI_API_KEY / OPENAI_API_KEY)"
    }
    
    missing = []
    for var, description in required_vars.items():
        if var == "AIFOUNDRY_API_KEY":
            value = os.getenv("AIFOUNDRY_API_KEY") or os.getenv("AZURE_OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
        else:
            value = os.getenv(var)
        if value:
            # Mask sensitive values
            if "KEY" in var or "PAT" in var:
                display_value = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
            else:
                display_value = value
            print(f"✅ {var}: {display_value}")
        else:
            print(f"❌ {var}: NOT SET")
            missing.append(f"{var} ({description})")
    
    print()
    
    if missing:
        print("❌ Missing environment variables:")
        for var in missing:
            print(f"   - {var}")
        return False
    
    print("✅ All environment variables are set")
    return True


def test_ai_foundry_connection():
    """Test connection to Microsoft AI Foundry"""
    print("=" * 60)
    print("2. Testing AI Foundry Connection")
    print("=" * 60)
    
    try:
        from ai_foundry_client import AIFoundryClient
        
        client = AIFoundryClient()
        
        # Test simple chat completion
        print("Sending test message to AI Foundry...")
        response = client.chat(
            messages=[
                {"role": "user", "content": "Say 'Hello from AI PR Agent!' and nothing else."}
            ],
            max_tokens=50,
            temperature=0
        )
        
        if 'choices' in response and len(response['choices']) > 0:
            message = response['choices'][0]['message']['content']
            print(f"✅ Response: {message}")
            print(f"✅ Tokens used: {response.get('usage', {}).get('total_tokens', 'N/A')}")
            return True
        else:
            print("❌ Unexpected response format")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def test_azure_devops_connection():
    """Test connection to Azure DevOps"""
    print()
    print("=" * 60)
    print("3. Testing Azure DevOps Connection")
    print("=" * 60)
    
    try:
        from azure_devops_client import AzureDevOpsClient
        
        client = AzureDevOpsClient(
            org_url=os.getenv("ADO_ORG_URL"),
            project=os.getenv("ADO_PROJECT"),
            pat=os.getenv("ADO_PAT")
        )
        
        # Test listing branches
        print("Fetching repository branches...")
        branches = client.list_branches(os.getenv("REPO_ID"))
        
        print(f"✅ Found {len(branches)} branches")
        if len(branches) > 0:
            print(f"   Sample branches:")
            for branch in branches[:5]:
                branch_name = branch['name'].replace('refs/heads/', '')
                print(f"   - {branch_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def test_local_repository():
    """Test local repository access"""
    print()
    print("=" * 60)
    print("4. Testing Local Repository Access")
    print("=" * 60)
    
    try:
        from git import Repo
        
        repo_path = os.getenv("REPO_PATH")
        print(f"Repository path: {repo_path}")
        
        repo = Repo(repo_path)
        
        # Get current branch
        current_branch = repo.active_branch.name
        print(f"✅ Current branch: {current_branch}")
        
        # List branches
        branches = [b.name for b in repo.branches]
        print(f"✅ Local branches: {len(branches)}")
        if len(branches) > 0:
            print(f"   - {', '.join(branches[:5])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def test_ai_tools_integration():
    """Test AI agent with Azure DevOps tools"""
    print()
    print("=" * 60)
    print("5. Testing AI Tools Integration")
    print("=" * 60)
    
    try:
        from azure_devops_tools import AzureDevOpsTools
        
        tools = AzureDevOpsTools(
            ado_org_url=os.getenv("ADO_ORG_URL"),
            ado_project=os.getenv("ADO_PROJECT"),
            ado_pat=os.getenv("ADO_PAT"),
            repo_id=os.getenv("REPO_ID"),
            repo_path=os.getenv("REPO_PATH")
        )
        
        print("Testing list_repository_branches tool...")
        result = tools.list_repository_branches()
        
        if result.get('success'):
            print(f"✅ Tool executed successfully")
            print(f"   Branches: {result.get('total_count', 0)}")
        else:
            print(f"❌ Tool execution failed: {result.get('error')}")
            return False
        
        # Get all tools
        all_tools = tools.get_all_tools()
        print(f"✅ Available tools: {len(all_tools)}")
        for tool_name in all_tools.keys():
            print(f"   - {tool_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def test_ai_agent():
    """Test complete AI PR Agent"""
    print()
    print("=" * 60)
    print("6. Testing AI PR Agent (Chat)")
    print("=" * 60)
    
    try:
        from ai_pr_agent import AIPRAgent
        
        agent = AIPRAgent(
            ado_org_url=os.getenv("ADO_ORG_URL"),
            ado_project=os.getenv("ADO_PROJECT"),
            ado_pat=os.getenv("ADO_PAT"),
            repo_id=os.getenv("REPO_ID"),
            repo_path=os.getenv("REPO_PATH")
        )
        
        print("Asking AI agent to list branches...")
        result = agent.chat_with_agent(
            "List all branches in the repository. Just give me the first 5."
        )
        
        print(f"✅ AI Response:")
        print(f"   {result['response']}")
        print(f"   Tokens used: {result.get('usage', {}).get('total_tokens', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("AI PR AGENT - SETUP VERIFICATION")
    print("=" * 60)
    print()
    
    tests = [
        ("Environment Variables", check_environment_variables),
        ("AI Foundry Connection", test_ai_foundry_connection),
        ("Azure DevOps Connection", test_azure_devops_connection),
        ("Local Repository", test_local_repository),
        ("AI Tools Integration", test_ai_tools_integration),
        ("AI Agent Chat", test_ai_agent)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except KeyboardInterrupt:
            print("\n\n⚠️  Tests interrupted by user")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ Unexpected error in {test_name}: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print()
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print()
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print()
        print("🎉 All tests passed! Your AI PR Agent is ready to use!")
        print()
        print("Next steps:")
        print("  1. Run example_ai_agent.py to see demonstrations")
        print("  2. Try creating a PR with the AI agent")
        print("  3. Read README.md for more information")
        return 0
    else:
        print()
        print("⚠️  Some tests failed. Please fix the issues above before using the agent.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
