# PR Creator Agent - Project Structure

```
pr-creator-agent/
│
├── 📄 README.md                      # Main documentation
├── 📄 QUICKSTART.md                  # Quick start guide
├── 📄 PR_GENERATION_PLAN.md          # Detailed plan for PR summary generation
├── 📄 requirements.txt               # Python dependencies
├── 📄 .env.example                   # Environment variables template
├── 📄 .gitignore                     # Git ignore rules
│
├── 🐍 azure_devops_client.py         # Azure DevOps REST API client
│   ├── AzureDevOpsClient             # Main client class
│   ├── get_work_item()               # Fetch work item details
│   ├── create_pull_request()         # Create PR
│   ├── list_repository_refs()        # List branches
│   └── verify_branch_exists()        # Validate branch
│
├── 🐍 pr_summary_generator.py        # PR summary generation logic
│   ├── PRSummaryGenerator            # Main generator class
│   ├── analyze_changes()             # Analyze git diffs
│   ├── _categorize_file()            # Categorize files by type
│   ├── _generate_change_summary()    # Group changes by category
│   └── generate_pr_description()     # Generate markdown PR body
│
├── 🐍 pr_agent.py                    # Main orchestrator
│   ├── PRAgent                       # Main agent class
│   ├── create_pr()                   # Create PR (full workflow)
│   ├── get_work_item_info()          # Get work item only
│   ├── preview_changes()             # Preview changes without creating PR
│   └── main()                        # CLI entry point
│
├── 🐍 teams_bot.py                   # Microsoft Teams bot handler
│   ├── TeamsPRBot                    # Bot handler class
│   ├── on_message_activity()         # Handle incoming messages
│   ├── _handle_create_pr_command()   # Process PR creation commands
│   ├── _parse_pr_command()           # Extract branch/work item from text
│   ├── _create_pr_success_card()     # Format success response
│   └── _send_help_message()          # Show bot help
│
└── 🐍 app.py                         # Teams bot web server
    ├── messages()                    # Bot endpoint handler
    ├── health()                      # Health check endpoint
    └── init_func()                   # App initialization
```

## File Descriptions

### Core Modules

#### `azure_devops_client.py`
**Purpose:** Interface with Azure DevOps REST API for work items, PRs, and repositories.

**Key Classes:**
- `WorkItem` - Data class for work item information
- `PullRequest` - Data class for PR details
- `AzureDevOpsClient` - Main API client

**Responsibilities:**
- Authenticate with PAT token
- Fetch work item details
- Create pull requests
- Verify branch existence
- Link work items to PRs

#### `pr_summary_generator.py`
**Purpose:** Analyze git changes and generate intelligent PR descriptions.

**Key Classes:**
- `FileChange` - Represents a single file change
- `ChangeSummary` - Categorized collection of changes
- `PRSummaryGenerator` - Main generator logic

**Responsibilities:**
- Compare git branches using GitPython
- Categorize files by type (service, controller, test, etc.)
- Group changes into meaningful categories
- Generate markdown-formatted PR descriptions
- Clean and format work item descriptions

#### `pr_agent.py`
**Purpose:** Orchestrate the entire PR creation workflow.

**Key Classes:**
- `PRAgent` - Main orchestrator

**Workflow:**
1. Verify branches exist
2. Fetch work item details
3. Analyze git changes
4. Generate PR description
5. Create PR in Azure DevOps
6. Return comprehensive result

**Can be used as:**
- Python module (import and call)
- CLI tool (run directly)

#### `teams_bot.py`
**Purpose:** Handle Microsoft Teams bot interactions.

**Key Classes:**
- `TeamsPRBot` - Bot activity handler

**Features:**
- Parse natural language commands
- Extract branch names and work item IDs
- Interactive command wizard
- Rich response formatting with links
- Help system

**Commands:**
- `create pr from <branch> for work item <id>`
- `create pr` - Start wizard
- `help` - Show all commands

#### `app.py`
**Purpose:** Web server for Teams bot.

**Endpoints:**
- `POST /api/messages` - Teams bot messaging endpoint
- `GET /health` - Health check

**Technology:**
- aiohttp web framework
- Bot Framework SDK
- Async/await for performance

## Data Flow

```
┌─────────────┐
│  User Input │
│  (CLI/Teams)│
└──────┬──────┘
       │
       v
┌──────────────────┐
│    PR Agent      │ ◄─── Orchestrator
└──────┬───────────┘
       │
       ├─────────────────────┐
       │                     │
       v                     v
┌──────────────┐      ┌──────────────────┐
│ Azure DevOps │      │ Git Repository   │
│   Client     │      │  (PR Summary     │
│              │      │   Generator)     │
│ - Work Items │      │ - Diff Analysis  │
│ - PRs        │      │ - Categorization │
│ - Branches   │      │ - Summary        │
└──────────────┘      └──────────────────┘
       │                     │
       └─────────┬───────────┘
                 │
                 v
          ┌────────────┐
          │   Result   │
          │ - PR URL   │
          │ - Summary  │
          │ - Changes  │
          └────────────┘
```

## Usage Patterns

### Pattern 1: Direct CLI
```bash
python pr_agent.py feature/my-branch develop 12345
```

### Pattern 2: Python Script
```python
from pr_agent import PRAgent
agent = PRAgent(...)
result = agent.create_pr(...)
```

### Pattern 3: Teams Bot
```
User: "create pr from feature/my-branch for work item 12345"
Bot: [Creates PR and returns link]
```

## Environment Variables

| Variable | Used By | Purpose |
|----------|---------|---------|
| `AZURE_DEVOPS_ORG_URL` | All modules | Organization URL |
| `AZURE_DEVOPS_PROJECT` | All modules | Project name |
| `AZURE_DEVOPS_PAT` | azure_devops_client | Authentication |
| `AZURE_DEVOPS_REPO_ID` | pr_agent | Repository ID |
| `GIT_REPO_PATH` | pr_summary_generator | Local repo path |
| `DEFAULT_TARGET_BRANCH` | pr_agent, teams_bot | Default target |
| `TEAMS_APP_ID` | teams_bot, app | Bot app ID |
| `TEAMS_APP_PASSWORD` | teams_bot, app | Bot secret |
| `PORT` | app | Server port |

## Dependencies

### Core
- `azure-devops` - Azure DevOps SDK
- `GitPython` - Git operations
- `requests` - HTTP client
- `python-dotenv` - Environment management

### Teams Bot
- `botbuilder-core` - Bot Framework
- `botbuilder-schema` - Bot schemas
- `aiohttp` - Async web server

### Optional
- `openai` - AI-powered summaries (future)
- `pydantic` - Data validation

## Testing Strategy

### Unit Tests (to be added)
- `test_azure_devops_client.py` - API client tests
- `test_pr_summary_generator.py` - Summary generation tests
- `test_pr_agent.py` - Agent orchestration tests
- `test_teams_bot.py` - Bot handler tests

### Integration Tests (to be added)
- `test_end_to_end.py` - Full workflow test
- `test_teams_integration.py` - Teams bot integration

### Manual Testing
```bash
# Test connection
python -c "from azure_devops_client import AzureDevOpsClient; ..."

# Test PR creation
python pr_agent.py feature/test-branch develop 12345

# Test bot locally
python app.py
# Then use Bot Framework Emulator
```

## Deployment

### Local Development
```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env
python pr_agent.py <branch> <target> <work_item>
```

### Teams Bot (Local Testing)
```bash
python app.py
ngrok http 3978
# Set bot endpoint to ngrok URL
```

### Production (Azure App Service)
1. Create Azure App Service (Python 3.8+)
2. Configure environment variables in App Service settings
3. Deploy code (Git, Azure DevOps, or VS Code)
4. Set bot messaging endpoint to App Service URL

## Extension Points

### Custom Categorization
Edit `pr_summary_generator.py::_categorize_file()` to add new file categories.

### Custom Templates
Edit `pr_summary_generator.py::generate_pr_description()` to modify PR format.

### Additional Commands
Edit `teams_bot.py::on_message_activity()` to add new bot commands.

### AI Integration
Add OpenAI integration in `pr_summary_generator.py` for smarter summaries.

## Security Considerations

- ✅ PAT tokens in environment variables only
- ✅ HTTPS for all API calls
- ✅ No credentials in logs
- ✅ Bot uses Microsoft authentication
- ✅ .gitignore excludes .env files
- ⚠️ Secure PAT storage recommended for production

## Performance

- Branch verification: ~500ms
- Work item fetch: ~800ms
- Git diff analysis: ~2-5s (depends on repo size)
- PR creation: ~1-2s
- **Total: ~5-10 seconds**

## Future Roadmap

1. ✅ Basic PR creation (Done)
2. ✅ Teams bot integration (Done)
3. ⏳ Unit test coverage
4. ⏳ AI-powered summaries (OpenAI)
5. ⏳ Auto-reviewer assignment
6. ⏳ Multi-repo support
7. ⏳ Draft PR mode
8. ⏳ Code quality metrics
