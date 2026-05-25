# AI PR Creator Agent

AI-powered autonomous agent for intelligent pull request creation in Azure DevOps using Microsoft AI Foundry and GPT-4o.

## 🌟 Overview

This project provides an AI agent that autonomously creates pull requests by:
- 🤖 Analyzing work items to understand context
- 🔍 Verifying branch existence and analyzing code changes
- 📝 Generating comprehensive, well-formatted PR descriptions
- 🔗 Linking work items and creating PRs in Azure DevOps
- 💬 Supporting natural language requests and interactive conversations

The agent uses **function calling** to intelligently orchestrate Azure DevOps operations, eliminating manual PR creation steps.

## 🚀 Features

### Core Capabilities

1. **Autonomous PR Creation**
   - AI analyzes work items, verifies branches, and creates PRs automatically
   - Generates structured PR descriptions with markdown formatting
   - Links work items and analyzes git diffs intelligently

2. **Natural Language Interface**
   - "Create a PR for work item 12345 from feature/login to develop"
   - No need to remember exact commands or formats
   - AI parses intent and executes appropriate actions

3. **Interactive Chat Mode**
   - Maintain conversation context across multiple queries
   - Ask questions about work items, branches, and changes
   - Iterative PR refinement before creation

4. **Intelligent Code Analysis**
   - Analyzes git diffs between branches
   - Categorizes changes: features, bug fixes, refactoring, tests, docs
   - Provides detailed file change summaries

5. **Azure DevOps Integration**
   - Work item retrieval and linking
   - Branch verification and commit history
   - Pull request creation with auto-reviewers
   - Repository exploration

## 📦 Installation

### Prerequisites
- Python 3.8+
- Azure DevOps account with PAT (Personal Access Token)
- Microsoft AI Foundry endpoint access
- Git repository cloned locally

### Setup Steps

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd pr-creator-agent
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment**
   
   Run the interactive setup wizard:
```bash
python setup_ai_agent.py
```

   Or manually create `.env` file:
```bash
copy .env.example .env
```

   Fill in required values:
```env
# Azure DevOps Configuration
ADO_ORG_URL=https://dev.azure.com/your-org
ADO_PROJECT=YourProjectName
ADO_PAT=your_personal_access_token
REPO_ID=your_repository_id
REPO_PATH=C:\Path\To\Your\Local\Repo

# AI Foundry Configuration
AIFOUNDRY_ENDPOINT=https://your-foundry-endpoint.services.ai.azure.com
AIFOUNDRY_API_KEY=your_ai_foundry_api_key

# Optional Settings
DEFAULT_TARGET_BRANCH=develop
```

4. **Verify setup**
```bash
python test_ai_agent.py
```

5. **Run demo**
```bash
python demo_ai_agent.py
```

## 💻 Usage

### Example 1: Basic Autonomous PR Creation

```python
from ai_pr_agent import AIPRAgent

agent = AIPRAgent(
    ado_org_url="https://dev.azure.com/your-org",
    ado_project="YourProject",
    ado_pat="your_pat",
    repo_id="your_repo_id",
    repo_path="C:\\path\\to\\repo"
)

# AI autonomously creates a complete PR
result = agent.create_pr_autonomous(
    source_branch="feature/user-authentication",
    target_branch="develop",
    work_item_id=12345
)

print(result['ai_response'])
```

### Example 2: Natural Language Request

```python
# Just describe what you want in plain English
result = agent.analyze_pr_request(
    "Create a PR for work item 12345 from feature/login to develop"
)
```

### Example 3: Custom Instructions

```python
result = agent.create_pr_autonomous(
    source_branch="bugfix/security-patch",
    target_branch="main",
    work_item_id=9876,
    user_instructions="""
    This is a critical security fix. Please emphasize:
    - Security implications and CVE references
    - Required security testing procedures
    - Need for expedited review
    """
)
```

### Example 4: Interactive Chat

```python
# Start a conversation with the AI agent
conversation = None

# Ask about a work item
result = agent.chat_with_agent(
    "Tell me about work item 12345",
    conversation_history=conversation
)
print("AI:", result['response'])

# Continue the conversation
result = agent.chat_with_agent(
    "What branches are available?",
    conversation_history=result['conversation_history']
)
print("AI:", result['response'])

# Create PR in context
result = agent.chat_with_agent(
    "Create a PR from feature/new-api to develop for this work item",
    conversation_history=result['conversation_history']
)
print("AI:", result['response'])
```

### Example 5: PR Summary Only (No Creation)

```python
# Get AI-generated PR summary without creating the PR
result = agent.chat_with_agent("""
I need a PR summary but don't create the actual PR yet.

Please:
1. Get work item #12345 details
2. Verify branches exist: feature/my-feature → develop
3. Analyze code changes between these branches
4. Generate a complete PR description

Show me the PR title and description you would use, but STOP before calling create_pull_request.
""")

print("AI-Generated Summary:")
print(result['response'])
```

### Example 6: Quick Helper Function

```python
from ai_pr_agent import create_ai_pr

# One-liner PR creation using environment variables
result = create_ai_pr(
    work_item_id=12345,
    source_branch="feature/payment-integration",
    target_branch="develop"
)
```

## 🛠️ Available AI Tools

The AI agent has access to these Azure DevOps tools:

| Tool | Description |
|------|-------------|
| `get_work_item` | Retrieve work item details (title, description, acceptance criteria) |
| `verify_branches` | Check if source and target branches exist |
| `analyze_code_changes` | Analyze git diff and categorize changes |
| `create_pull_request` | Create PR with title, description, and work item links |
| `list_repository_branches` | List all branches in the repository |
| `get_commit_details` | Get recent commit history for a branch |

The AI autonomously decides which tools to use and in what order based on the user's request.

## 📁 Project Structure

```
pr-creator-agent/
├── ai_pr_agent.py              # Main AI agent interface and workflows
├── ai_foundry_client.py        # AI Foundry client with function calling
├── azure_devops_tools.py       # Tool schemas and callable functions
├── azure_devops_client.py      # Azure DevOps API integration
├── pr_summary_generator.py     # Git diff analysis and summary generation
├── setup_ai_agent.py           # Interactive environment setup wizard
├── test_ai_agent.py            # Setup verification and connectivity test
├── demo_ai_agent.py            # Quick demonstration script
├── example_ai_agent.py         # Comprehensive usage examples
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variable template
└── README.md                   # This file
```

## 🔧 Core Components

### AI Foundry Client (`ai_foundry_client.py`)
- Microsoft AI Foundry integration with GPT-4o
- Function calling loop with tool execution
- API version compatibility (2024-08-01-preview, 2024-02-01-preview, 2023-12-01-preview)
- Automatic retry logic with version fallback

### Azure DevOps Tools (`azure_devops_tools.py`)
- Decorated tool schemas using `@tool_schema`
- Callable functions exposed to AI agent
- Error handling and structured responses
- Work item, branch, commit, and PR operations

### PR Summary Generator (`pr_summary_generator.py`)
- Local git repository analysis
- Intelligent change categorization
- File diff parsing and summarization
- Markdown-formatted output generation

### AI PR Agent (`ai_pr_agent.py`)
- High-level agent interface
- Three interaction modes:
  - `create_pr_autonomous()` - Structured PR creation
  - `analyze_pr_request()` - Natural language processing
  - `chat_with_agent()` - Interactive conversation

## 🎯 How It Works

1. **User Request**: Provide work item ID and branches (or natural language request)

2. **AI Analysis**: Agent receives request and system prompt explaining available tools

3. **Function Calling Loop**:
   - AI decides which tools to call (e.g., `get_work_item`)
   - Tool executes and returns results
   - AI analyzes results and decides next action
   - Repeats until task complete (max 10 iterations)

4. **PR Creation**: AI synthesizes information and creates structured PR description

5. **Response**: Agent returns success status and AI-generated summary

## 🔍 Example AI Workflow

For request: "Create PR for work item 12345 from feature/login to develop"

```
1. AI calls: get_work_item(12345)
   → Understands: "Implement user login with OAuth2"

2. AI calls: verify_branches("feature/login", "develop")
   → Confirms: Both branches exist

3. AI calls: analyze_code_changes("feature/login", "develop")
   → Finds: 5 files changed (auth.py, login.py, tests, config, docs)

4. AI calls: create_pull_request(
      title="Implement User Login with OAuth2",
      description="## Summary\n[AI-generated description]...",
      work_item_ids=[12345]
   )
   → PR created successfully

5. AI responds: "✅ Created PR #234 linking work item #12345"
```

## 🧪 Testing

### Verify Setup
```bash
python test_ai_agent.py
```
Tests: Environment variables, API connectivity, Azure DevOps access

### Run Demo
```bash
python demo_ai_agent.py
```
Demonstrates: Branch listing, repository queries, interactive chat

### Test PR Summary Only
```bash
python test_pr_summary_only.py
```
Tests: AI analysis without creating actual PR

### Run Examples
```bash
python example_ai_agent.py
```
Comprehensive examples of all agent capabilities

## ⚙️ Configuration

### API Version Compatibility

The client uses these Azure OpenAI API versions (in order):
1. `2024-08-01-preview` (default - latest features)
2. `2024-02-01-preview` (stable function calling)
3. `2023-12-01-preview` (fallback)

**Note**: Versions before 2023-12-01 don't support function calling properly.

### Model Configuration

Default model: `gpt-4o`

You can override the model:
```python
from ai_foundry_client import AIFoundryClient

client = AIFoundryClient(
    endpoint="https://your-endpoint.com",
    api_key="your-key",
    deployment="gpt-4o",  # or "gpt-4", "gpt-35-turbo"
    api_version="2024-08-01-preview"
)
```

### Temperature Settings

- `create_pr_autonomous()`: 0.3 (focused, deterministic)
- `analyze_pr_request()`: 0.4 (balanced)
- `chat_with_agent()`: 0.7 (creative, conversational)

## 🐛 Troubleshooting

### 400 Bad Request Error
**Cause**: Using old API version (e.g., 2023-05-15) that doesn't support function calling

**Fix**: Updated in latest version to use 2024-08-01-preview. Pull latest changes:
```bash
git pull origin main
```

### 401 Authentication Error
**Cause**: Invalid API key or endpoint mismatch

**Fix**: 
- Verify `AIFOUNDRY_API_KEY` in `.env`
- Confirm `AIFOUNDRY_ENDPOINT` matches your AI Foundry resource
- Check key hasn't expired

### Branch Not Found
**Cause**: Branch name mismatch or doesn't exist in Azure DevOps

**Fix**: Use full branch name without `refs/heads/` prefix
```python
# Correct
source_branch="feature/my-feature"

# Incorrect
source_branch="refs/heads/feature/my-feature"
```

### Max Iterations Reached
**Cause**: AI couldn't complete task in 10 function calls

**Fix**: 
- Simplify the request
- Provide more specific instructions
- Check if branches/work items exist

### Git Repository Not Found
**Cause**: `REPO_PATH` doesn't point to valid git repository

**Fix**: Ensure path points to repository root (contains `.git` folder)

## 📊 Best Practices

1. **Clear Work Items**: Ensure work items have detailed descriptions and acceptance criteria
2. **Branch Naming**: Use consistent naming conventions (feature/, bugfix/, hotfix/)
3. **Specific Instructions**: Provide context for complex or critical PRs
4. **Verify Before Creating**: Use `chat_with_agent` to preview PR content first
5. **Iterative Refinement**: Use chat mode to refine PR details before creation

## 🔐 Security Notes

- Store `.env` file securely and never commit it
- Use Azure DevOps PAT with minimum required permissions:
  - Code: Read & Write
  - Work Items: Read
- Rotate API keys regularly
- Use separate PATs for different environments

## 🚀 Roadmap

- [ ] Support for GitHub and GitLab
- [ ] Multi-work-item PR creation
- [ ] Auto-reviewer assignment based on file changes
- [ ] PR template customization
- [ ] Slack/Teams notifications
- [ ] CI/CD pipeline integration
- [ ] PR quality scoring and suggestions

## 📝 License

[Specify your license here]

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request with clear description

## 📧 Support

For issues or questions:
- Open an issue on GitHub
- Contact: [your-email@example.com]

---

**Built with ❤️ using Microsoft AI Foundry and Azure DevOps**
