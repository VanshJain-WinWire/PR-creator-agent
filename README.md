# PR Creator Agent

AI-first Python agent for autonomous pull request creation in Azure DevOps.

## Overview

This repository contains only the active AI implementation.

Core capabilities:
- Autonomous PR creation with tool-calling
- Natural-language PR requests
- Work item lookup and branch verification
- Git diff analysis and structured PR descriptions

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Create environment file:

```bash
copy .env.example .env
```

3. Fill required values in `.env`:

```env
ADO_ORG_URL=https://dev.azure.com/your-org
ADO_PROJECT=YourProject
ADO_PAT=your_personal_access_token
REPO_ID=your_repository_id
REPO_PATH=C:\Path\To\Your\Local\Repo
AIFOUNDRY_ENDPOINT=https://af-sdlc-dev.services.ai.azure.com
AIFOUNDRY_API_KEY=your_ai_foundry_api_key
DEFAULT_TARGET_BRANCH=develop
```

4. Verify setup:

```bash
python test_ai_agent.py
```

## Quick Usage

```python
from ai_pr_agent import AIPRAgent

agent = AIPRAgent(
    ado_org_url="https://dev.azure.com/your-org",
    ado_project="YourProject",
    ado_pat="your_pat",
    repo_id="your_repo_id",
    repo_path="C:\\path\\to\\repo"
)

result = agent.create_pr_autonomous(
    source_branch="feature/new-feature",
    target_branch="develop",
    work_item_id=12345
)
```

Natural-language request:

```python
response = agent.analyze_pr_request(
    "Create a PR for work item 12345 from feature/new-feature to develop"
)
```

## Main Files

- `ai_pr_agent.py`: AI agent interface and workflows
- `ai_foundry_client.py`: AI Foundry client and tool-call loop
- `azure_devops_tools.py`: tool schemas and callable actions
- `azure_devops_client.py`: Azure DevOps API integration
- `pr_summary_generator.py`: local diff analysis and summary building
- `setup_ai_agent.py`: interactive environment setup
- `test_ai_agent.py`: setup and connectivity verification
- `demo_ai_agent.py` and `example_ai_agent.py`: runnable examples