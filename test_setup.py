# Test PR Agent Setup
# Quick script to verify your installation works

import os
from dotenv import load_dotenv

print("🔍 Testing PR Agent Setup...\n")

# Load environment
load_dotenv()

# Check environment variables
required_vars = [
    "AZURE_DEVOPS_ORG_URL",
    "AZURE_DEVOPS_PROJECT",
    "AZURE_DEVOPS_PAT",
    "AZURE_DEVOPS_REPO_ID",
    "GIT_REPO_PATH"
]

print("📋 Checking environment variables...")
missing = []
for var in required_vars:
    value = os.getenv(var)
    if value and value != f"your_{var.lower()}":
        print(f"  ✓ {var}: {'*' * 10} (set)")
    else:
        print(f"  ✗ {var}: NOT SET")
        missing.append(var)

if missing:
    print(f"\n❌ Missing {len(missing)} required environment variable(s).")
    print("\n📝 Edit your .env file and set:")
    for var in missing:
        print(f"   - {var}")
    print("\n💡 See QUICKSTART.md section 8-9 for how to get these values.")
    exit(1)

print("\n✓ All environment variables are set!\n")

# Test imports
print("📦 Testing Python imports...")
try:
    from azure_devops_client import AzureDevOpsClient
    print("  ✓ azure_devops_client")
except ImportError as e:
    print(f"  ✗ azure_devops_client: {e}")
    exit(1)

try:
    from pr_summary_generator import PRSummaryGenerator
    print("  ✓ pr_summary_generator")
except ImportError as e:
    print(f"  ✗ pr_summary_generator: {e}")
    exit(1)

try:
    from pr_agent import PRAgent
    print("  ✓ pr_agent")
except ImportError as e:
    print(f"  ✗ pr_agent: {e}")
    exit(1)

print("\n✓ All imports successful!\n")

# Test Azure DevOps connection
print("🔗 Testing Azure DevOps connection...")
try:
    client = AzureDevOpsClient(
        os.getenv("AZURE_DEVOPS_ORG_URL"),
        os.getenv("AZURE_DEVOPS_PROJECT"),
        os.getenv("AZURE_DEVOPS_PAT")
    )
    
    # Try to get a work item (use a test work item ID)
    test_work_item_id = 105550
    print(f"  Fetching work item #{test_work_item_id}...")
    
    wi = client.get_work_item(test_work_item_id)
    print(f"  ✓ Connected! Work Item: {wi.title}")
    
except Exception as e:
    print(f"  ✗ Connection failed: {e}")
    print("\n💡 Check:")
    print("   - Is your PAT token valid?")
    print("   - Does it have 'Code (Read & Write)' and 'Work Items (Read)' permissions?")
    print("   - Is work item #105550 accessible in your project?")
    exit(1)

print("\n" + "="*60)
print("✅ SUCCESS! Your PR Creator Agent is ready to use!")
print("="*60)
print("\n📚 Next steps:")
print("  1. Create your first PR:")
print("     python pr_agent.py feature/your-branch develop 105550")
print("\n  2. Or import in Python:")
print("     from pr_agent import PRAgent")
print("\n  3. Need Teams bot? See QUICKSTART.md section 4")
print("\n🎉 Happy automating!")
