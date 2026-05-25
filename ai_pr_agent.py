"""
AI PR Agent - Autonomous PR Creation with Microsoft AI Foundry
Uses LLM with function calling to intelligently create and manage pull requests
"""
import os
from typing import Dict, Any, Optional
from ai_foundry_client import AIFoundryClient
from azure_devops_tools import AzureDevOpsTools


class AIPRAgent:
    """
    AI-powered PR agent that uses Microsoft AI Foundry to autonomously
    create pull requests by analyzing work items and code changes
    """
    
    def __init__(
        self,
        ado_org_url: str,
        ado_project: str,
        ado_pat: str,
        repo_id: str,
        repo_path: str,
        ai_endpoint: str = None,
        ai_api_key: str = None
    ):
        """Initialize AI PR Agent with Azure DevOps and AI Foundry credentials"""
        
        # Initialize AI Foundry client
        self.ai_client = AIFoundryClient(
            endpoint=ai_endpoint or os.getenv("AIFOUNDRY_ENDPOINT", "https://af-sdlc-dev.services.ai.azure.com"),
            api_key=ai_api_key or os.getenv("AIFOUNDRY_API_KEY"),
            deployment="gpt-4o"
        )
        
        # Initialize Azure DevOps tools
        self.ado_tools = AzureDevOpsTools(
            ado_org_url=ado_org_url,
            ado_project=ado_project,
            ado_pat=ado_pat,
            repo_id=repo_id,
            repo_path=repo_path
        )
        
        self.org_url = ado_org_url
        self.project = ado_project
        self.repo_id = repo_id
    
    def create_pr_autonomous(
        self,
        source_branch: str,
        target_branch: str,
        work_item_id: int,
        user_instructions: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Autonomously create a PR using AI to analyze work items and code changes
        
        The AI agent will:
        1. Fetch work item details
        2. Verify branches exist
        3. Analyze code changes
        4. Generate a comprehensive PR description
        5. Create the pull request
        
        Args:
            source_branch: Feature branch with changes
            target_branch: Target branch (e.g., 'develop', 'main')
            work_item_id: Azure DevOps work item ID
            user_instructions: Optional additional instructions for the AI
        
        Returns:
            Dictionary with PR details and conversation history
        """
        
        print("🤖 AI PR Agent Starting...")
        print(f"📋 Work Item: #{work_item_id}")
        print(f"🌿 Branches: {source_branch} → {target_branch}")
        print()
        
        # Build system prompt
        system_prompt = """You are an expert DevOps AI agent specialized in creating high-quality pull requests.

Your task is to:
1. Fetch the work item details to understand what was implemented
2. Verify that both source and target branches exist
3. Analyze the code changes between the branches
4. Create a comprehensive, well-formatted PR description
5. Create the pull request linking it to the work item

When creating the PR description, follow this EXACT structure:

### Summary

Briefly describe the purpose of this change. What feature, bug fix or improvement does it address?

---

### Changes

- Describe major changes and their impact
- Mention any new dependencies, architectural decisions, or patterns used
- Include screenshots for UI updates (if applicable)

---

### Documentation

- What documentation was added or updated for this change?
- Link to updated files in `/documentation` when applicable
- If no documentation changes were needed, explain why

---

### Testing

What was tested and how?

- [ ] Unit tests written/updated
- [ ] Manual testing performed
- [ ] Code compiles successfully in local env
- [ ] Deploy to BLD from Feature branch

**IMPORTANT**: Only check boxes (use [x]) if you have CONFIRMED information about that item from your analysis. If you cannot determine whether something was done, leave it UNCHECKED (use [ ]).

---

### Checklist

- [ ] Follows .NET coding conventions (naming, formatting)
- [ ] Logic is clear and well-structured
- [ ] Input validation is included where needed
- [ ] Documentation has been added or updated, or a reason is provided above for why no documentation changes were needed
- [ ] No secrets or credentials in code
- [ ] Logging is meaningful and not overly verbose
- [ ] Code is commented where complex
- [ ] Relevant tests included and pass

**IMPORTANT**: Only check boxes (use [x]) if you can CONFIRM from your code analysis. If you cannot verify an item, leave it UNCHECKED (use [ ]).

Use markdown formatting and be thorough but concise. Always link the work item IDs properly.

You have access to Azure DevOps tools - use them to gather information and create the PR.
"""
        
        # Build user message
        user_message = f"""Please create a pull request for the following:

**Source Branch**: {source_branch}
**Target Branch**: {target_branch}
**Work Item ID**: {work_item_id}

"""
        
        if user_instructions:
            user_message += f"\n**Additional Instructions**: {user_instructions}\n"
        
        user_message += """
Please:
1. Get the work item details
2. Verify branches exist  
3. Analyze the code changes
4. Create a comprehensive PR with a well-formatted description
"""
        
        # Prepare messages
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        # Get all available tools
        tools = self.ado_tools.get_all_tools()
        
        # Run AI agent with function calling
        print("🧠 AI Agent analyzing and executing...")
        print()
        
        result = self.ai_client.chat_with_functions(
            messages=messages,
            functions=tools,
            max_iterations=10,
            temperature=0.3  # Lower temperature for more focused responses
        )
        
        print()
        print("✅ AI Agent Completed")
        print(f"🔄 Function calls made: {result['iterations']}")
        print()
        print("📝 AI Response:")
        print(result['response'])
        print()
        
        return {
            "success": True,
            "ai_response": result['response'],
            "function_calls": result['iterations'],
            "conversation_history": result['conversation_history'],
            "usage": result.get('usage', {})
        }
    
    def analyze_pr_request(
        self,
        user_request: str
    ) -> Dict[str, Any]:
        """
        Let the AI agent analyze a natural language PR request and execute it
        
        Example requests:
        - "Create a PR for work item 12345 from feature/login to develop"
        - "I need a PR for bug fix 9876, compare my-fix-branch with main"
        - "Draft a PR linking story 5432 from feature/dashboard to release"
        
        Args:
            user_request: Natural language description of the PR to create
        
        Returns:
            Dictionary with PR details and AI analysis
        """
        
        print("🤖 AI PR Agent - Natural Language Processing")
        print(f"📝 Request: {user_request}")
        print()
        
        system_prompt = """You are an expert DevOps AI agent that helps developers create pull requests.

You understand natural language requests and can:
- Extract branch names, work item IDs, and PR requirements from user requests
- Fetch work item details and verify branches
- Analyze code changes between branches
- Generate comprehensive PR descriptions following the specified format

When creating PR descriptions, follow this EXACT structure:

### Summary
Briefly describe the purpose of this change. What feature, bug fix or improvement does it address?

---

### Changes
- Describe major changes and their impact
- Mention any new dependencies, architectural decisions, or patterns used
- Include screenshots for UI updates (if applicable)

---

### Documentation
- What documentation was added or updated for this change?
- Link to updated files in `/documentation` when applicable
- If no documentation changes were needed, explain why

---

### Testing
What was tested and how?

- [ ] Unit tests written/updated
- [ ] Manual testing performed
- [ ] Code compiles successfully in local env
- [ ] Deploy to BLD from Feature branch

**IMPORTANT**: Only check boxes (use [x]) if you have CONFIRMED information. Leave UNCHECKED (use [ ]) if unknown.

---

### Checklist
- [ ] Follows .NET coding conventions (naming, formatting)
- [ ] Logic is clear and well-structured
- [ ] Input validation is included where needed
- [ ] Documentation has been added or updated, or a reason is provided above for why no documentation changes were needed
- [ ] No secrets or credentials in code
- [ ] Logging is meaningful and not overly verbose
- [ ] Code is commented where complex
- [ ] Relevant tests included and pass

**IMPORTANT**: Only check boxes (use [x]) if you can CONFIRM from your analysis. Leave UNCHECKED (use [ ]) if you cannot verify.

When given a request, parse the information and use the available tools to:
1. Get work item details
2. Verify branches exist
3. Analyze code changes
4. Create the pull request with properly formatted description

Always be helpful and thorough in your analysis."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_request}
        ]
        
        tools = self.ado_tools.get_all_tools()
        
        print("🧠 AI Agent processing request...")
        print()
        
        result = self.ai_client.chat_with_functions(
            messages=messages,
            functions=tools,
            max_iterations=10,
            temperature=0.4
        )
        
        print()
        print("✅ Request Completed")
        print(f"🔄 Actions taken: {result['iterations']}")
        print()
        print("📝 AI Response:")
        print(result['response'])
        print()
        
        return {
            "success": True,
            "ai_response": result['response'],
            "actions_taken": result['iterations'],
            "conversation_history": result['conversation_history'],
            "usage": result.get('usage', {})
        }
    
    def chat_with_agent(
        self,
        message: str,
        conversation_history: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Have an interactive conversation with the AI agent about PRs and work items
        
        Args:
            message: User message to send to the agent
            conversation_history: Previous conversation history (optional)
        
        Returns:
            Dictionary with AI response and updated conversation history
        """
        
        system_prompt = """You are a helpful DevOps AI assistant with access to Azure DevOps.

You can help users with:
- Creating and managing pull requests
- Analyzing work items and code changes
- Verifying branches and commits
- Providing insights about repository state

Use your tools to fetch real data from Azure DevOps when needed."""
        
        if conversation_history is None:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ]
        else:
            messages = conversation_history.copy()
            messages.append({"role": "user", "content": message})
        
        tools = self.ado_tools.get_all_tools()
        
        result = self.ai_client.chat_with_functions(
            messages=messages,
            functions=tools,
            max_iterations=5,
            temperature=0.7
        )
        
        return {
            "response": result['response'],
            "conversation_history": result['conversation_history'],
            "usage": result.get('usage', {})
        }


# Convenience function for quick PR creation
def create_ai_pr(
    work_item_id: int,
    source_branch: str,
    target_branch: str = "develop",
    user_instructions: Optional[str] = None
) -> Dict[str, Any]:
    """
    Quick helper function to create a PR using AI agent with environment variables
    
    Required environment variables:
    - ADO_ORG_URL: Azure DevOps organization URL
    - ADO_PROJECT: Project name
    - ADO_PAT: Personal Access Token
    - REPO_ID: Repository ID
    - REPO_PATH: Local repository path
    - AIFOUNDRY_ENDPOINT: AI Foundry endpoint (optional, defaults to af-sdlc-dev)
    - AIFOUNDRY_API_KEY: AI Foundry API key
    """
    
    agent = AIPRAgent(
        ado_org_url=os.getenv("ADO_ORG_URL"),
        ado_project=os.getenv("ADO_PROJECT"),
        ado_pat=os.getenv("ADO_PAT"),
        repo_id=os.getenv("REPO_ID"),
        repo_path=os.getenv("REPO_PATH")
    )
    
    return agent.create_pr_autonomous(
        source_branch=source_branch,
        target_branch=target_branch,
        work_item_id=work_item_id,
        user_instructions=user_instructions
    )
