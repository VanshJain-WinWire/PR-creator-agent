# Quick Start Guide

## Prerequisites

**Windows Users:** If you're on Windows, ensure you're using **Python 3.11 or 3.12** (not 3.14) for better package compatibility. Check your version:
```bash
python --version
```

If you have Python 3.14, consider installing Python 3.12 from [python.org](https://www.python.org/downloads/).

## 1. Setup (5 minutes)

```bash
# Install core dependencies (works without Teams bot)
pip install -r requirements.txt

# Copy environment template
copy .env.example .env  # Windows
# OR
cp .env.example .env    # Mac/Linux

# Edit .env with your Azure DevOps details
# - AZURE_DEVOPS_ORG_URL
# - AZURE_DEVOPS_PROJECT
# - AZURE_DEVOPS_PAT (get from https://dev.azure.com/winwire/_usersSettings/tokens)
# - AZURE_DEVOPS_REPO_ID
# - GIT_REPO_PATH (path to your local git repo)
```

**Note:** Teams bot is optional. You can use the agent via CLI or Python without installing Teams dependencies.

## 2. Test Connection

```bash
# Test Azure DevOps connection
python -c "from azure_devops_client import AzureDevOpsClient; import os; from dotenv import load_dotenv; load_dotenv(); client = AzureDevOpsClient(os.getenv('AZURE_DEVOPS_ORG_URL'), os.getenv('AZURE_DEVOPS_PROJECT'), os.getenv('AZURE_DEVOPS_PAT')); wi = client.get_work_item(105550); print(f'✓ Connected! Work Item: {wi.title}')"
```

## 3. Create Your First PR

### Option A: Command Line
```bash
python pr_agent.py feature/your-branch develop 105550
```

### Option B: Python Script
```python
from pr_agent import PRAgent
import os
from dotenv import load_dotenv

load_dotenv()

agent = PRAgent(
    ado_org_url=os.getenv("AZURE_DEVOPS_ORG_URL"),
    ado_project=os.getenv("AZURE_DEVOPS_PROJECT"),
    ado_pat=os.getenv("AZURE_DEVOPS_PAT"),
    repo_id=os.getenv("AZURE_DEVOPS_REPO_ID"),
    repo_path=os.getenv("GIT_REPO_PATH")
)

result = agent.create_pr(
    source_branch="feature/azure_blob_storage",
    target_branch="develop",
    work_item_id=105550
)

print(f"✅ PR Created: {result['pull_request'].web_url}")
```

## 4. Enable Teams Bot (Optional)

**Important:** Teams bot requires additional dependencies that may need C++ compiler on Windows.

### A. Install Teams Dependencies
```bash
# Install Teams bot dependencies
pip install -r requirements-teams.txt

# If you get build errors on Windows:
# 1. Install Visual C++ Build Tools from:
#    https://visualstudio.microsoft.com/visual-cpp-build-tools/
#    (Select "Desktop development with C++" during installation)
# 2. Or use Python 3.11/3.12 instead of 3.14
```

### B. Get Teams App Credentials
1. Go to Azure Portal → Bot Services
2. Create a new Bot Channels Registration
3. Note the App ID and Secret
4. Add Teams channel

### B. Configure
```bash
# Add to .env
TEAMS_APP_ID=your_app_id
TEAMS_APP_PASSWORD=your_app_secret
PORT=3978
```

### C. Run Bot Server
```bash
python app.py
```

### D. Expose with ngrok (for testing)
```bash
# In another terminal
ngrok http 3978

# Copy the https URL and set as bot messaging endpoint
# https://your-url.ngrok.io/api/messages
```

### E. Test in Teams
Message your bot:
```
create pr from feature/my-branch for work item 105550
```

## 5. Common Commands

```bash
# Preview changes without creating PR
python -c "from pr_agent import PRAgent; import os; from dotenv import load_dotenv; load_dotenv(); agent = PRAgent(os.getenv('AZURE_DEVOPS_ORG_URL'), os.getenv('AZURE_DEVOPS_PROJECT'), os.getenv('AZURE_DEVOPS_PAT'), os.getenv('AZURE_DEVOPS_REPO_ID'), os.getenv('GIT_REPO_PATH')); result = agent.preview_changes('feature/my-branch', 'develop'); print(f'Files changed: {len(result[\"file_changes\"])}')"

# Get work item details
python -c "from pr_agent import PRAgent; import os; from dotenv import load_dotenv; load_dotenv(); agent = PRAgent(os.getenv('AZURE_DEVOPS_ORG_URL'), os.getenv('AZURE_DEVOPS_PROJECT'), os.getenv('AZURE_DEVOPS_PAT'), os.getenv('AZURE_DEVOPS_REPO_ID'), os.getenv('GIT_REPO_PATH')); wi = agent.get_work_item_info(105550); print(f'{wi.id}: {wi.title}')"
```

## 6. Troubleshooting

**Problem:** Build errors for `aiohttp` or `pydantic-core` (missing Visual C++ or Rust)
**Solution:**
1. **Skip Teams bot for now** - The core PR agent works without Teams dependencies:
   ```bash
   pip install -r requirements.txt  # This works without compiler
   python pr_agent.py feature/test develop 12345
   ```
2. **Use Python 3.11 or 3.12** - Python 3.14 is very new and lacks pre-built wheels:
   - Download Python 3.12 from [python.org](https://www.python.org/downloads/)
   - Create new virtual environment: `python -m venv venv`
   - Activate: `venv\Scripts\activate`
   - Install: `pip install -r requirements-teams.txt`
3. **Install Visual C++ Build Tools** (if you must use Python 3.14):
   - Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
   - Select "Desktop development with C++" during installation
   - Restart terminal and try again

**Problem:** ImportError: No module named 'git'
**Solution:** `pip install GitPython`

**Problem:** 401 Unauthorized from Azure DevOps
**Solution:** 
1. Regenerate your PAT at https://dev.azure.com/winwire/_usersSettings/tokens
2. Ensure it has "Code (Read & Write)" and "Work Items (Read)" scopes
3. Update .env file

**Problem:** Branch not found
**Solution:**
1. Check branch name (case-sensitive)
2. Ensure branch is pushed to remote
3. Fetch latest: `git fetch --all` in your repo

**Problem:** "Both a source and target reference is required"
**Solution:** This usually means branch refs are malformed. The agent handles this automatically, but if you see this error, ensure you're using branch names without "refs/heads/" prefix.

## 7. Next Steps

- Customize PR templates in `pr_summary_generator.py`
- Add additional file categorization rules
- Integrate with CI/CD pipelines
- Deploy Teams bot to Azure App Service
- Add more commands to Teams bot

## 8. Getting PAT Token

1. Go to https://dev.azure.com/winwire
2. Click your profile icon (top right)
3. Select "Personal access tokens"
4. Click "New Token"
5. Give it a name: "PR Creator Agent"
6. Set expiration (90 days recommended)
7. Select scopes:
   - Code: Read & Write
   - Work Items: Read
8. Click "Create"
9. **Copy the token immediately** (you won't see it again!)
10. Paste it in your `.env` file

## 9. Repo ID

To get your repo ID:

```bash
# Using Azure CLI (if installed)
az repos show --repository aisdlc-api --project AI-SDLC --organization https://dev.azure.com/winwire

# Or use the REST API
curl -u :YOUR_PAT https://dev.azure.com/winwire/AI-SDLC/_apis/git/repositories/aisdlc-api?api-version=7.0
```

The `id` field in the response is your REPO_ID.

---

**Need Help?** Check the full [README.md](README.md) for detailed documentation!
