# AI PR Agent - Microsoft AI Foundry Integration

## 🤖 Overview

The AI PR Agent uses Microsoft AI Foundry to create an autonomous agent that intelligently manages pull requests in Azure DevOps. The agent uses function calling to interact with Azure DevOps APIs and can understand natural language requests.

## 🌟 Features

### Autonomous PR Creation
The AI agent can:
- **Fetch work item details** automatically from Azure DevOps
- **Verify branch existence** before creating PRs
- **Analyze code changes** between branches
- **Generate comprehensive PR descriptions** based on work items and code analysis
- **Create pull requests** with automatic work item linking
- **Handle natural language requests** like "Create a PR for work item 12345 from my feature branch to develop"

### Azure DevOps Tools
The agent has access to these tools:
- `get_work_item` - Retrieve work item details
- `verify_branches` - Check if branches exist
- `analyze_code_changes` - Analyze diffs between branches
- `create_pull_request` - Create PRs with descriptions
- `list_repository_branches` - List all branches
- `get_commit_details` - Get recent commits from a branch

## 📋 Prerequisites

1. **Microsoft AI Foundry Access**
   - Endpoint URL (e.g., `https://af-sdlc-dev.services.ai.azure.com`)
   - API Key with appropriate permissions
   - Deployed GPT-4 model

2. **Azure DevOps Access**
   - Organization URL
   - Project name
   - Personal Access Token (PAT) with:
     - Code (Read & Write)
     - Work Items (Read)
     - Pull Request Threads (Read & Write)

3. **Local Repository**
   - Cloned git repository for diff analysis

## 🚀 Quick Start

### 1. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in your credentials:

```bash
# Azure DevOps Configuration
ADO_ORG_URL=https://dev.azure.com/your-org
ADO_PROJECT=YourProject
ADO_PAT=your_pat_token_here
REPO_ID=your_repo_id

# Local Repository Path
REPO_PATH=C:\Path\To\Your\Local\Repo

# Microsoft AI Foundry
AIFOUNDRY_ENDPOINT=https://af-sdlc-dev.services.ai.azure.com
AIFOUNDRY_API_KEY=your_api_key_here
```

### 3. Basic Usage

```python
from ai_pr_agent import AIPRAgent

# Initialize agent
agent = AIPRAgent(
    ado_org_url="https://dev.azure.com/your-org",
    ado_project="YourProject",
    ado_pat="your_pat",
    repo_id="your_repo_id",
    repo_path="C:\\path\\to\\repo"
)

# Create PR autonomously
result = agent.create_pr_autonomous(
    source_branch="feature/my-feature",
    target_branch="develop",
    work_item_id=12345
)

print(result['ai_response'])
```

## 📚 Usage Examples

### Example 1: Autonomous PR Creation

The AI agent handles everything automatically:

```python
agent = AIPRAgent(...)

result = agent.create_pr_autonomous(
    source_branch="feature/user-authentication",
    target_branch="develop",
    work_item_id=12345
)

# AI will:
# 1. Fetch work item #12345
# 2. Verify both branches exist
# 3. Analyze code changes
# 4. Generate comprehensive PR description
# 5. Create the pull request
```

### Example 2: With Custom Instructions

Provide additional context to the AI:

```python
result = agent.create_pr_autonomous(
    source_branch="bugfix/security-patch",
    target_branch="main",
    work_item_id=9876,
    user_instructions="""
    This is a critical security fix. Please emphasize:
    - Security implications
    - Testing requirements
    - Need for immediate review
    """
)
```

### Example 3: Natural Language Requests

Let the AI parse your request:

```python
result = agent.analyze_pr_request(
    "Create a PR for work item 54321 comparing feature/dashboard with develop"
)
```

### Example 4: Interactive Chat

Have a conversation with the agent:

```python
# Ask about a work item
result1 = agent.chat_with_agent(
    "Tell me about work item 12345"
)

# Continue the conversation
result2 = agent.chat_with_agent(
    "Now create a PR from feature/api to develop for this work item",
    conversation_history=result1['conversation_history']
)
```

### Example 5: Quick Helper

One-liner PR creation using environment variables:

```python
from ai_pr_agent import create_ai_pr

result = create_ai_pr(
    work_item_id=12345,
    source_branch="feature/payment",
    target_branch="develop"
)
```

## 🔧 Architecture

### Components

1. **AIFoundryClient** (`ai_foundry_client.py`)
   - Handles communication with Microsoft AI Foundry
   - Supports function calling / tool use
   - Manages multi-turn conversations

2. **AzureDevOpsTools** (`azure_devops_tools.py`)
   - Wraps Azure DevOps APIs as callable functions
   - Provides tool schemas for the AI agent
   - Handles error responses

3. **AIPRAgent** (`ai_pr_agent.py`)
   - Main orchestrator for AI-powered PR creation
   - Manages conversation flow
   - Coordinates between AI and Azure DevOps

### How It Works

```
User Request
    ↓
AI PR Agent (orchestrator)
    ↓
AI Foundry LLM (GPT-4)
    ↓
Function Calls → Azure DevOps Tools
    ↓
Azure DevOps API
    ↓
Results back to LLM
    ↓
AI Response to User
```

The AI agent uses OpenAI's function calling feature to:
1. Decide which tools to use
2. Call tools with appropriate parameters
3. Interpret tool results
4. Make follow-up decisions
5. Provide comprehensive responses

## 🎯 Best Practices

### 1. Work Item Quality
- Ensure work items have clear descriptions
- Include acceptance criteria
- Link related items

### 2. Branch Naming
- Use consistent branch naming conventions
- Include work item IDs when possible
- Use descriptive names (e.g., `feature/user-auth`, `bugfix/login-timeout`)

### 3. AI Instructions
- Be specific in custom instructions
- Mention critical requirements
- Specify review priorities

### 4. Error Handling
```python
result = agent.create_pr_autonomous(...)

if result.get('success'):
    print(f"✅ PR created: {result['ai_response']}")
else:
    print(f"❌ Error: {result.get('error')}")
```

## 🔐 Security Considerations

1. **Credentials**
   - Store API keys in environment variables
   - Never commit `.env` files
   - Use `.gitignore` to exclude sensitive files
   - Rotate keys regularly

2. **API Key Permissions**
   - Use minimum required permissions
   - AI Foundry: Chat completions only
   - Azure DevOps: Scope PAT to specific projects

3. **Draft PRs**
   - PRs are created as drafts by default
   - Review AI-generated descriptions before publishing
   - Verify linked work items

## 📊 Token Usage

The AI agent optimizes token usage:
- Uses temperature 0.3 for focused PR creation
- Limits function call iterations (max 10)
- Returns token usage in responses

Example token tracking:
```python
result = agent.create_pr_autonomous(...)
print(f"Tokens used: {result['usage']['total_tokens']}")
```

## 🐛 Troubleshooting

### Issue: "API key is required"
**Solution**: Set `AIFOUNDRY_API_KEY` in your `.env` file

### Issue: "Branch does not exist"
**Solution**: 
- Check branch names (no `refs/heads/` prefix needed)
- Verify branches exist in Azure DevOps
- Use `list_repository_branches` tool to see available branches

### Issue: "Work item not found"
**Solution**: 
- Verify work item ID is correct
- Check PAT has work item read permissions
- Ensure work item is in the correct project

### Issue: "Max iterations reached"
**Solution**: 
- Increase `max_iterations` parameter
- Check if tools are returning errors
- Verify Azure DevOps connectivity

## 🔄 Comparison with Original Agent

| Feature | Original PR Agent | AI PR Agent |
|---------|------------------|-------------|
| Work item fetching | ✅ Manual | ✅ Autonomous |
| Branch verification | ✅ Manual | ✅ Autonomous |
| Change analysis | ✅ Manual | ✅ Autonomous |
| PR description | 📝 Template | 🤖 AI-generated |
| Error handling | Basic | Intelligent retry |
| Natural language | ❌ No | ✅ Yes |
| Interactive chat | ❌ No | ✅ Yes |

## 📈 Future Enhancements

Potential improvements:
- [ ] Multi-PR creation for related work items
- [ ] Automatic reviewer assignment based on code ownership
- [ ] PR status monitoring and updates
- [ ] Integration with CI/CD pipelines
- [ ] Code review comment generation
- [ ] Work item transition automation

## 🤝 Contributing

To add new Azure DevOps tools:

1. Add method to `AzureDevOpsTools` class
2. Decorate with `@tool_schema`
3. Add to `get_all_tools()` dictionary
4. Test with example usage

Example:
```python
@tool_schema({
    "name": "get_reviewers",
    "description": "Get suggested reviewers for a PR",
    "parameters": {
        "type": "object",
        "properties": {
            "file_paths": {
                "type": "array",
                "items": {"type": "string"}
            }
        }
    }
})
def get_reviewers(self, file_paths: List[str]) -> Dict[str, Any]:
    # Implementation
    pass
```

## 📝 License

Same as parent project.

## 🙏 Acknowledgments

- Microsoft AI Foundry for LLM capabilities
- Azure DevOps API for repository management
- OpenAI for function calling specification
