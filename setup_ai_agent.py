#!/usr/bin/env python3
"""
Quick Setup Script for AI PR Agent
Helps users configure their environment interactively
"""
import os
import sys
from pathlib import Path


def print_banner():
    """Print welcome banner"""
    print("\n" + "=" * 60)
    print("  AI PR AGENT - QUICK SETUP")
    print("=" * 60)
    print("\nThis script will help you set up your .env file")
    print("for the AI PR Agent with Microsoft AI Foundry.\n")


def get_input(prompt, default=None, required=True):
    """Get user input with optional default"""
    if default:
        full_prompt = f"{prompt} [{default}]: "
    else:
        full_prompt = f"{prompt}: "
    
    while True:
        value = input(full_prompt).strip()
        
        if value:
            return value
        elif default:
            return default
        elif not required:
            return ""
        else:
            print("❌ This field is required. Please enter a value.")


def main():
    """Run interactive setup"""
    print_banner()
    
    # Check if .env already exists
    env_file = Path(".env")
    if env_file.exists():
        overwrite = input("⚠️  .env file already exists. Overwrite? (y/N): ").strip().lower()
        if overwrite != 'y':
            print("Setup cancelled.")
            return
    
    print("Please provide the following information:\n")
    
    # Azure DevOps Configuration
    print("📋 Azure DevOps Configuration")
    print("-" * 60)
    ado_org_url = get_input("Azure DevOps Organization URL", "https://dev.azure.com/your-org")
    ado_project = get_input("Project Name")
    ado_pat = get_input("Personal Access Token (PAT)")
    repo_id = get_input("Repository ID")
    print()
    
    # Local Repository
    print("📁 Local Repository")
    print("-" * 60)
    repo_path = get_input("Local Repository Path", os.getcwd())
    print()
    
    # AI Foundry Configuration
    print("🤖 Microsoft AI Foundry Configuration")
    print("-" * 60)
    aifoundry_endpoint = get_input(
        "AI Foundry Endpoint",
        "https://af-sdlc-dev.services.ai.azure.com"
    )
    aifoundry_api_key = get_input("AI Foundry API Key")
    print()
    
    # Default branch
    print("🌿 Default Configuration")
    print("-" * 60)
    default_branch = get_input("Default Target Branch", "develop")
    print()
    
    # Create .env content
    env_content = f"""# Azure DevOps Configuration
ADO_ORG_URL={ado_org_url}
ADO_PROJECT={ado_project}
ADO_PAT={ado_pat}
REPO_ID={repo_id}

# Local Repository Path
REPO_PATH={repo_path}

# Microsoft AI Foundry Configuration (for AI Agent)
AIFOUNDRY_ENDPOINT={aifoundry_endpoint}
AIFOUNDRY_API_KEY={aifoundry_api_key}

# Default Branch Configuration
DEFAULT_TARGET_BRANCH={default_branch}
"""
    
    # Write .env file
    print("=" * 60)
    print("Writing configuration to .env file...")
    
    with open(".env", "w") as f:
        f.write(env_content)
    
    print("✅ .env file created successfully!")
    print()
    
    # Summary
    print("=" * 60)
    print("SETUP COMPLETE!")
    print("=" * 60)
    print()
    print("Next steps:")
    print()
    print("1. Install dependencies:")
    print("   pip install -r requirements.txt")
    print()
    print("2. Test your setup:")
    print("   python test_ai_agent.py")
    print()
    print("3. Try the examples:")
    print("   python example_ai_agent.py")
    print()
    print("4. Read the documentation:")
    print("   - README.md - AI agent overview and usage")
    print()
    print("📚 For more information, see the documentation files.")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)
