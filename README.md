# PR Creator Agent

Intelligent Python agent that automates pull request creation with Azure DevOps integration, work item linking, and Microsoft Teams bot support.

## 🤖 NEW: AI-Powered PR Agent

**Now with Microsoft AI Foundry integration!** The PR Creator Agent can now operate autonomously using LLM-powered decision making and function calling.

### What's New
- ✨ **Autonomous PR Creation** - AI agent handles the entire workflow
- 💬 **Natural Language Interface** - "Create a PR for work item 12345 from my feature branch"
- 🔧 **Function Calling** - AI uses Azure DevOps tools intelligently
- 🧠 **Context-Aware** - Understands work items and code changes
- 🎯 **Smart Descriptions** - AI-generated PR descriptions based on actual changes

### Quick Start with AI Agent

```python
from ai_pr_agent import AIPRAgent

agent = AIPRAgent(
    ado_org_url="https://dev.azure.com/your-org",
    ado_project="YourProject",
    ado_pat="your_pat",
    repo_id="your_repo_id",
    repo_path="C:\\path\\to\\repo"
)

# Let AI handle everything
result = agent.create_pr_autonomous(
    source_branch="feature/new-feature",
    target_branch="develop",
    work_item_id=12345
)
```

**📖 See [AI_AGENT_README.md](AI_AGENT_README.md) for complete AI agent documentation**

---

## 🚀 Features

- ✅ **Automatic PR Creation** - Create PRs with a single command (created as **drafts** by default)
- 📋 **Work Item Integration** - Fetch and link Azure DevOps work items automatically
- 🤖 **Teams Bot** - Create PRs directly from Microsoft Teams chat
- 📊 **Intelligent Summary Generation** - Analyze git diffs and generate comprehensive PR descriptions
- 🔍 **Change Categorization** - Automatically categorize changes (features, refactoring, tests, etc.)
- 🔗 **Automatic Linking** - Link work items to PRs automatically
- ✨ **Rich Formatting** - Generate markdown-formatted PR descriptions with emojis and sections

## 📋 Architecture

```
┌─────────────────┐
│  Teams Chat     │
│  "create pr"    │
└────────┬────────┘
         │
         v
┌─────────────────────────────────┐
│      Teams Bot Handler          │
│  - Parse commands               │
│  - Extract branch & work item   │
└────────┬────────────────────────┘
         │
         v
┌─────────────────────────────────┐
│       PR Agent (Orchestrator)   │
│  1. Verify branches exist       │
│  2. Fetch work item details     │
│  3. Analyze git changes         │
│  4. Generate PR summary         │
│  5. Create PR in Azure DevOps   │
└────────┬────────────────────────┘
         │
    ┌────┴────┐
    │         │
    v         v
┌─────────┐  ┌──────────────────┐
│ Azure   │  │ Git Repository   │
│ DevOps  │  │ (Local/Clone)    │
│ REST    │  │ - Diff analysis  │
│ API     │  │ - File changes   │
└─────────┘  └──────────────────┘
```

## 🛠️ How PR Summary Generation Works

### Step 1: Git Diff Analysis
```python
# Fetch commits between branches
base = repo.commit(target_branch)  # e.g., develop
head = repo.commit(source_branch)  # e.g., feature/my-branch

# Get diff between branches
diff_index = base.diff(head)

# For each changed file:
# - Detect status (Added, Modified, Deleted, Renamed)
# - Count additions/deletions
# - Categorize by file path and extension
```

### Step 2: File Categorization
Files are automatically categorized based on:
- **Path patterns**: `/services/`, `/controllers/`, `/models/`, `/tests/`
- **File extensions**: `.cs`, `.json`, `.md`, `.config`
- **Naming conventions**: `Service.cs`, `Controller.cs`, `Test.cs`

Categories:
- 🚀 **Features** - New services, controllers, models
- ♻️ **Refactoring** - Modified services/business logic
- 🐛 **Bug Fixes** - Detected by keywords or manual override
- 🧪 **Tests** - Test files and test projects
- ⚙️ **Configuration** - Config files, appsettings, etc.
- 📚 **Documentation** - README, markdown files

### Step 3: Work Item Context
```python
# Fetch work item from Azure DevOps
work_item = ado_client.get_work_item(work_item_id)

# Extract:
# - Title
# - Description
# - Acceptance Criteria
# - Type (User Story, Bug, Task)
# - State (Active, Resolved, Closed)
```

### Step 4: Summary Assembly
```markdown
## Summary
[High-level overview based on work item title]

## Work Item Context
**Work Item:** AB#105550 - Allow input file upload in all phases
[Work item description]

### Acceptance Criteria
[Acceptance criteria from work item]

## Changes Made

### 🚀 Features & Enhancements
- ✨ **Services/RequirementGeneratorService.cs**: New service added
- 🔧 **Controllers/WinAIController.cs**: API endpoint updated

### ♻️ Refactoring
- 🔧 **Services/OnCallSupportService.cs**: Service refactored

### 🧪 Tests
- ✨ **Tests/ServiceTests.cs**: New tests added

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests passed
- [ ] Manual testing completed

## Related Work Items
Fixes AB#105550
```

## 📦 Installation

### Prerequisites
- Python 3.11+ (Python 3.11 or 3.12 recommended for Windows users)
- Git installed and configured
- Azure DevOps account with PAT (Personal Access Token)
- Local clone of your repository
- (Optional) Microsoft Teams app registration for bot

### Setup

1. **Clone the project:**
```bash
cd c:\Users\Vanshjain\Project\pr-creator-agent
```

2. **Install core dependencies:**
```bash
pip install -r requirements.txt
```

**Note:** This installs everything you need for CLI and Python usage. Teams bot is optional (see section below).

3. **Configure environment:**
```bash
copy .env.example .env  # Windows
# OR
cp .env.example .env    # Mac/Linux
```

Edit `.env` and add your configuration:
```env
AZURE_DEVOPS_ORG_URL=https://dev.azure.com/winwire
AZURE_DEVOPS_PROJECT=AI-SDLC
AZURE_DEVOPS_PAT=your_pat_token_here
AZURE_DEVOPS_REPO_ID=dea47add-b82d-45e2-942a-ac97c4b17a31
GIT_REPO_PATH=c:\Users\Vanshjain\Project\aisdlc-api
DEFAULT_TARGET_BRANCH=develop
```

4. **Test your setup:**
```bash
python test_setup.py
```

### Teams Bot Setup (Optional)

The Teams bot requires additional dependencies that need C++ compiler on Windows.

**Option 1: Use Python 3.11/3.12 (Recommended for Windows)**
```bash
pip install -r requirements-teams.txt
```

**Option 2: Install Visual C++ Build Tools (if using Python 3.14)**
1. Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Select "Desktop development with C++" during installation
3. Run: `pip install -r requirements-teams.txt`

Then configure Teams bot settings in `.env` (see Teams Bot Setup section below).

## 🎯 Usage

### Option 1: Command Line (Easiest)

```bash
python pr_agent.py feature/azure_blob_storage develop 105550
```

### Option 2: Python Script

```python
from pr_agent import PRAgent
import os

agent = PRAgent(
    ado_org_url=os.getenv("AZURE_DEVOPS_ORG_URL"),
    ado_project=os.getenv("AZURE_DEVOPS_PROJECT"),
    ado_pat=os.getenv("AZURE_DEVOPS_PAT"),
    repo_id=os.getenv("AZURE_DEVOPS_REPO_ID"),
    repo_path=os.getenv("GIT_REPO_PATH")
)

result = agent.create_pr(
    source_branch="feature/my-branch",
    target_branch="develop",
    work_item_id=105550
)

print(f"PR Created: {result['pull_request'].web_url}")
```

### Option 3: Microsoft Teams Bot (Requires Additional Setup)

**Note:** Teams bot requires installing `requirements-teams.txt` (see Teams Bot Setup section above).

1. **Start the bot server:**
```bash
python app.py
```

2. **In Teams, message the bot:**
```
create pr from feature/azure_blob_storage for work item 105550
```

Or use the wizard:
```
create pr
```

The bot will guide you through the process!

## 🤖 Teams Bot Setup

### 1. Register Teams App

1. Go to [Azure Portal](https://portal.azure.com)
2. Create a new **Bot Channels Registration**
3. Note the **App ID** and generate an **App Secret**
4. Add Microsoft Teams channel

### 2. Configure Bot

Add to `.env`:
```env
TEAMS_APP_ID=your_app_id
TEAMS_APP_PASSWORD=your_app_secret
PORT=3978
```

### 3. Deploy

**Local testing (with ngrok):**
```bash
ngrok http 3978
```

Copy the ngrok URL and set it as your bot's messaging endpoint:
```
https://your-ngrok-url.ngrok.io/api/messages
```

**Production:**
Deploy to Azure App Service, AWS, or your preferred cloud platform.

### 4. Install in Teams

1. Create Teams app manifest
2. Add bot configuration
3. Upload to Teams or publish to Teams Store

## 📝 Example Output

```
🔍 Verifying branches...
📋 Fetching work item #105550...
   ✓ Work Item: Allow input file upload in all phases
📊 Analyzing changes between feature/azure_blob_storage and develop...
   ✓ Found 12 changed files
✍️ Generating PR description...
🚀 Creating pull request...
   ✓ PR #5870 created successfully!
   🔗 https://dev.azure.com/winwire/AI-SDLC/_git/aisdlc-api/pullrequest/5870

============================================================
✅ SUCCESS!
============================================================
PR URL: https://dev.azure.com/winwire/AI-SDLC/_git/aisdlc-api/pullrequest/5870
PR ID: 5870
Title: Allow input file upload in all phases (AB#105550)
Status: active
============================================================
```

## 🔧 Configuration Options

| Variable | Description | Required |
|----------|-------------|----------|
| `AZURE_DEVOPS_ORG_URL` | Azure DevOps organization URL | Yes |
| `AZURE_DEVOPS_PROJECT` | Project name | Yes |
| `AZURE_DEVOPS_PAT` | Personal Access Token | Yes |
| `AZURE_DEVOPS_REPO_ID` | Repository GUID | Yes |
| `GIT_REPO_PATH` | Local repo path for diff analysis | Yes |
| `DEFAULT_TARGET_BRANCH` | Default target branch (e.g., develop) | No |
| `TEAMS_APP_ID` | Teams bot app ID | Teams only |
| `TEAMS_APP_PASSWORD` | Teams bot app secret | Teams only |
| `PORT` | Server port | No (default: 3978) |

## 🎨 Customization

### Custom Summary Templates

Edit `pr_summary_generator.py` to customize the PR description format:

```python
def generate_pr_description(self, ...):
    pr_body = f"""## Summary
    {your_custom_template}
    """
```

### Additional Change Categories

Add new categorization rules in `_categorize_file()`:

```python
if 'infrastructure' in file_path_lower:
    return 'infrastructure'
```

## 🧪 Testing

```bash
# Test Azure DevOps connection
python -c "from azure_devops_client import AzureDevOpsClient; import os; from dotenv import load_dotenv; load_dotenv(); client = AzureDevOpsClient(os.getenv('AZURE_DEVOPS_ORG_URL'), os.getenv('AZURE_DEVOPS_PROJECT'), os.getenv('AZURE_DEVOPS_PAT')); print(client.get_work_item(105550))"

# Preview changes without creating PR
python -c "from pr_agent import PRAgent; import os; from dotenv import load_dotenv; load_dotenv(); agent = PRAgent(os.getenv('AZURE_DEVOPS_ORG_URL'), os.getenv('AZURE_DEVOPS_PROJECT'), os.getenv('AZURE_DEVOPS_PAT'), os.getenv('AZURE_DEVOPS_REPO_ID'), os.getenv('GIT_REPO_PATH')); print(agent.preview_changes('feature/my-branch', 'develop'))"
```

## 📚 API Reference

### PRAgent

```python
agent.create_pr(source_branch, target_branch, work_item_id) -> dict
agent.get_work_item_info(work_item_id) -> WorkItem
agent.preview_changes(source_branch, target_branch) -> dict
```

### AzureDevOpsClient

```python
client.get_work_item(work_item_id) -> WorkItem
client.create_pull_request(...) -> PullRequest
client.verify_branch_exists(repo_id, branch_name) -> bool
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - feel free to use this in your projects!

## 🆘 Troubleshooting

**Error: Branch not found**
- Ensure branch exists in remote repository
- Check branch name spelling (case-sensitive)
- Verify you have permissions to access the branch

**Error: Work item not found**
- Verify work item ID is correct
- Check PAT has Work Items Read permissions
- Ensure work item is in the specified project

**Error: 401 Unauthorized**
- Regenerate your PAT token
- Ensure PAT has Code (Read & Write) permissions
- Check PAT expiration date

**Teams bot not responding**
- Verify bot endpoint is accessible
- Check TEAMS_APP_ID and TEAMS_APP_PASSWORD
- Review bot logs for errors

## 📞 Support

For issues or questions, please open an issue on GitHub or contact the development team.
