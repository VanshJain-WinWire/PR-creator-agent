"""
AI PR Agent - Autonomous PR Creation with Microsoft AI Foundry
Uses LLM with function calling to intelligently create and manage pull requests
"""
import os
import re
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

        # Initialize Azure DevOps tools with AI client for code analysis
        self.ado_tools = AzureDevOpsTools(
            ado_org_url=ado_org_url,
            ado_project=ado_project,
            ado_pat=ado_pat,
            repo_id=repo_id,
            repo_path=repo_path,
            ai_client=self.ai_client
        )
        
        self.org_url = ado_org_url
        self.project = ado_project
        self.repo_id = repo_id

    def _validate_pr_format(self, description: str) -> tuple[bool, list[str]]:
        """
        Validate if PR description follows the required format

        Returns:
            (is_valid, list of issues found)
        """
        issues = []

        # Required sections
        required_sections = [
            "### Summary",
            "### Changes",
            "### Documentation",
            "### Testing",
            "### Checklist"
        ]

        for section in required_sections:
            if section not in description:
                issues.append(f"Missing required section: {section}")

        # Check for separators
        separator_count = description.count("\n---\n")
        if separator_count < 4:
            issues.append(f"Missing section separators (---). Found {separator_count}, need 4")

        # Check for wrong patterns
        if "Linked Work Item:" in description:
            issues.append("Found 'Linked Work Item:' - should use AB#<id> in Summary instead")

        if "This PR implements the functionality outlined in work item #" in description:
            issues.append("Should use AB# format, not 'work item #'")

        # Check if analyze_code_changes was called
        if "AI analysis unavailable" in description or "Manual analysis not available" in description:
            issues.append("analyze_code_changes was not called or failed - PR description lacks detailed code analysis")

        # Check if Changes section has proper format
        if "### Changes" in description:
            changes_start = description.find("### Changes")
            next_section = description.find("###", changes_start + 1)
            changes_content = description[changes_start:next_section] if next_section > 0 else description[changes_start:]

            if "- **" not in changes_content:
                issues.append("Changes section should have bullets like '- **Filename**: Description'")

        is_valid = len(issues) == 0
        return is_valid, issues

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

**MANDATORY TOOL CALLING ORDER**:
1. FIRST: get_work_item() - Get work item details
2. SECOND: verify_branches() - Verify branches exist
3. THIRD: **analyze_code_changes() - YOU MUST CALL THIS!** This returns detailed_changes with what_changed/why_changed/impact for each file
4. FOURTH: create_pull_request() - Create PR with detailed description using data from step 3

**CRITICAL**: You CANNOT skip analyze_code_changes. If you try to create a PR without calling analyze_code_changes first, YOU WILL FAIL. The PR description requires the detailed_changes data from this tool.

When creating the PR description, follow this EXACT format. DO NOT deviate from this structure:

When you call create_pull_request, the description parameter MUST be formatted EXACTLY like this example:

---EXAMPLE START---
### Summary

This PR implements OAuth2 authentication for user login as described in AB#12345. The implementation adds support for Google and GitHub as identity providers, allowing users to authenticate using their existing accounts instead of creating new credentials.

---

### Changes

- **Controllers/AuthController.cs**: Added new OAuth2LoginAsync method that handles the OAuth2 callback flow, validates state tokens, exchanges authorization codes for access tokens, and creates user sessions
  - **Why**: To implement secure OAuth2 authentication flow following industry standards and best practices
  - **Impact**: New API endpoint at /api/auth/oauth/callback. Requires OAuth2Service dependency injection

- **Services/OAuth2Service.cs**: Created new service implementing OAuth2 provider integration with methods for generating authorization URLs, validating state tokens, exchanging codes for tokens, and fetching user profiles from Google/GitHub APIs
  - **Why**: To encapsulate OAuth2 provider communication logic in a dedicated, testable service layer
  - **Impact**: New dependencies: Microsoft.AspNetCore.Authentication.OAuth package. Requires OAuth client secrets in configuration

- **Models/OAuthProvider.cs**: Added new enum and provider configuration model defining supported OAuth2 providers (Google, GitHub) with their respective client IDs and authorization endpoints
  - **Why**: To maintain provider configurations in a type-safe, maintainable structure
  - **Impact**: Configuration changes required in appsettings.json for OAuth client credentials

---

### Documentation

- No documentation files were modified in this change

---

### Testing

What was tested and how?

- [ ] Unit tests written/updated
- [ ] Manual testing performed
- [ ] Code compiles successfully in local env
- [ ] Deploy to BLD from Feature branch

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
---EXAMPLE END---

**FORMAT RULES YOU MUST FOLLOW**:
1. Start with EXACTLY "### Summary" (3 hashes, space, capital S)
2. After Summary paragraph, use EXACTLY "---" (3 dashes) on its own line
3. Then EXACTLY "### Changes" (3 hashes, space, capital C)
4. For each file, use EXACTLY: "- **Filename**: Description"
5. Add sub-bullets with EXACTLY "  - **Why**: " and "  - **Impact**: "
6. After Changes section, EXACTLY "---" on its own line
7. Then EXACTLY "### Documentation"
8. Then EXACTLY "---" on its own line
9. Then EXACTLY "### Testing"
10. Then EXACTLY "---" on its own line
11. Then EXACTLY "### Checklist"
12. Use ONLY these 5 sections: Summary, Changes, Documentation, Testing, Checklist
13. DO NOT use bullet points in Summary
14. DO NOT skip sections
15. DO NOT add extra sections
16. DO NOT use different headers like "Linked Work Item" or "Description"

**WHEN YOU CALL create_pull_request**:
- The description parameter MUST follow the exact format above
- Use detailed_changes fields (what_changed, why_changed, impact) from analyze_code_changes
- If you generate anything other than this exact format, YOU HAVE FAILED

**EXAMPLES OF WRONG FORMATS (DO NOT USE THESE)**:

❌ WRONG - Simple bullet list:
"This PR implements the functionality outlined in work item #107295:
- Added export endpoints
- PDF generation using QuestPDF
- Excel generation using EPPlus
Linked Work Item: #107295"

❌ WRONG - Missing section headers:
"Description: This PR adds export functionality.
Changes: Updated InsightsController.
Linked: #107295"

✅ CORRECT - Use the exact format from the example above with ### headers and --- separators.

You have access to Azure DevOps tools - use them to gather information and create the PR.
"""
        
        # Build user message
        user_message = f"""Please create a pull request for the following:

**Source Branch**: {source_branch}
**Target Branch**: {target_branch}
**Work Item ID**: {work_item_id}

**CRITICAL STEPS YOU MUST FOLLOW IN THIS EXACT ORDER**:

1. FIRST: Call get_work_item({work_item_id}) to understand what was implemented
2. SECOND: Call verify_branches("{source_branch}", "{target_branch}") to confirm branches exist
3. THIRD: **MANDATORY** - Call analyze_code_changes("{source_branch}", "{target_branch}") to get detailed_changes with what_changed/why_changed/impact for each file
4. FOURTH: Create PR using create_pull_request with the EXACT format from the example above, using the detailed_changes data

**YOU MUST CALL analyze_code_changes BEFORE create_pull_request. DO NOT SKIP THIS STEP.**

If you skip analyze_code_changes, you will not have the data needed to create a proper PR description.
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

        max_retries = 2
        for attempt in range(max_retries):
            result = self.ai_client.chat_with_functions(
                messages=messages,
                functions=tools,
                max_iterations=10,
                temperature=0.1  # Very low temperature for strict format adherence
            )

            print()
            print(f"✅ AI Agent Completed (Attempt {attempt + 1}/{max_retries})")
            print(f"🔄 Function calls made: {result['iterations']}")
            print()

            # Check if analyze_code_changes was called
            conversation = result.get('conversation_history', [])
            analyze_called = any(
                'analyze_code_changes' in str(msg.get('tool_calls', ''))
                for msg in conversation
                if msg.get('role') == 'assistant'
            )

            if not analyze_called:
                print("⚠️  WARNING: analyze_code_changes was NOT called!")
                if attempt < max_retries - 1:
                    print(f"🔄 Retrying with explicit instructions... (Attempt {attempt + 2}/{max_retries})")
                    messages.append({"role": "assistant", "content": result['response']})
                    messages.append({
                        "role": "user",
                        "content": "ERROR: You did not call analyze_code_changes! You MUST call analyze_code_changes(source_branch, target_branch) BEFORE creating the PR. This tool provides the detailed_changes with what_changed/why_changed/impact that you need for the PR description. Please call it now."
                    })
                    continue
                else:
                    print("❌ Failed after maximum retries - analyze_code_changes was never called")

            # Validate PR format if a PR was created
            pr_description = ""
            for msg in conversation:
                if msg.get('role') == 'assistant' and msg.get('tool_calls'):
                    for tool_call in msg.get('tool_calls', []):
                        if tool_call.get('function', {}).get('name') == 'create_pull_request':
                            import json
                            args = json.loads(tool_call.get('function', {}).get('arguments', '{}'))
                            pr_description = args.get('description', '')
                            break

            if pr_description:
                is_valid, issues = self._validate_pr_format(pr_description)

                if not is_valid:
                    print(f"⚠️  WARNING: PR format validation failed! Issues found:")
                    for issue in issues:
                        print(f"   - {issue}")

                    if attempt < max_retries - 1:
                        print(f"🔄 Retrying with format correction... (Attempt {attempt + 2}/{max_retries})")
                        issues_str = "\n".join(f"- {issue}" for issue in issues)
                        messages = result['conversation_history'].copy()
                        messages.append({
                            "role": "user",
                            "content": f"""ERROR: The PR description format is INCORRECT. Issues found:

{issues_str}

You MUST fix the PR description to follow the EXACT format from the example. Remember:
- Use "### Summary", "### Changes", "### Documentation", "### Testing", "### Checklist"
- Use "---" between sections
- In Changes section, use detailed_changes data with what_changed/why_changed/impact
- DO NOT use "Linked Work Item:" or bullet lists
- Follow the example exactly!

Please call create_pull_request again with the CORRECTED description."""
                        })
                        continue
                    else:
                        print("❌ Failed after maximum retries - PR format still incorrect")
                else:
                    print("✅ PR format validation passed!")

            # Success - break retry loop
            break

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
- Analyze code changes between branches (AI analyzes diffs)
- Generate comprehensive PR descriptions in the EXACT required format

**CRITICAL FORMAT REQUIREMENT**: When you call create_pull_request, the description MUST follow this EXACT format:

### Summary

[2-3 sentences describing purpose. Reference work item as AB#<id>]

---

### Changes

- **[Filename]**: [Use what_changed from detailed_changes]
  - **Why**: [Use why_changed from detailed_changes]
  - **Impact**: [Use impact from detailed_changes if significant]

---

### Documentation

- [List documentation changes OR state "No documentation files were modified in this change"]

---

### Testing

What was tested and how?

- [ ] Unit tests written/updated
- [ ] Manual testing performed
- [ ] Code compiles successfully in local env
- [ ] Deploy to BLD from Feature branch

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

**MANDATORY RULES**:
1. Use EXACTLY "### Summary", "### Changes", "### Documentation", "### Testing", "### Checklist"
2. Use EXACTLY "---" between sections
3. NO bullet points in Summary section
4. NO extra sections like "Linked Work Item" or "Description"
5. Use what_changed, why_changed, impact from detailed_changes in Changes section

When given a request:
1. Get work item details
2. Verify branches exist
3. Analyze code changes
4. Create PR with description in EXACT format above

Always be helpful and thorough."""
        
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
            temperature=0.1  # Very low temperature for strict format adherence
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

**CRITICAL: When creating pull requests, you MUST follow this EXACT format:**

### Summary

[2-3 sentences describing purpose. Reference work item as AB#<id>]

---

### Changes

- **[Filename]**: [Use what_changed from detailed_changes]
  - **Why**: [Use why_changed from detailed_changes]
  - **Impact**: [Use impact from detailed_changes if significant]

---

### Documentation

[Documentation info or "No documentation files were modified"]

---

### Testing

What was tested and how?

- [ ] Unit tests written/updated
- [ ] Manual testing performed
- [ ] Code compiles successfully in local env
- [ ] Deploy to BLD from Feature branch

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

**MANDATORY WHEN CREATING PR**:
1. ALWAYS call analyze_code_changes() before create_pull_request()
2. Use ONLY these section headers: Summary, Changes, Documentation, Testing, Checklist
3. Use "---" as separators between sections
4. DO NOT use: "Linked Work Item", "Features", "Notes", or any other sections

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
            temperature=0.1  # Low temperature for strict format when creating PRs
        )
        
        return {
            "response": result['response'],
            "conversation_history": result['conversation_history'],
            "usage": result.get('usage', {})
        }

    def generate_pr_summary(
        self,
        source_branch: str,
        target_branch: str,
        work_item_id: int
    ) -> Dict[str, Any]:
        """
        Generate PR summary WITHOUT creating the actual PR

        Use this when you want to:
        - Preview the PR description before creating it
        - Get AI analysis for review
        - Generate documentation without PR creation

        Args:
            source_branch: Feature branch with changes
            target_branch: Target branch (e.g., 'develop', 'main')
            work_item_id: Azure DevOps work item ID

        Returns:
            Dictionary with generated PR summary
        """

        print("🤖 AI PR Agent - Generating Summary (No PR Creation)")
        print(f"📋 Work Item: #{work_item_id}")
        print(f"🌿 Branches: {source_branch} → {target_branch}")
        print()

        system_prompt = """You are an expert DevOps AI agent specialized in analyzing code changes and generating PR descriptions.

**MANDATORY TOOL CALLING ORDER**:
1. FIRST: get_work_item() - Get work item details
2. SECOND: verify_branches() - Verify branches exist
3. THIRD: **analyze_code_changes() - YOU MUST CALL THIS!** Returns detailed_changes with what_changed/why_changed/impact
4. FOURTH: Generate PR description and show it to user

**CRITICAL**: DO NOT call create_pull_request. Your task is to GENERATE the PR description only, not create the actual PR.

Generate the PR description following this EXACT format:

### Summary

[2-3 sentences describing purpose. Reference work item as AB#<id>]

---

### Changes

- **[Filename]**: [Use what_changed from detailed_changes]
  - **Why**: [Use why_changed from detailed_changes]
  - **Impact**: [Use impact from detailed_changes if significant]

---

### Documentation

[Documentation info or "No documentation files were modified"]

---

### Testing

What was tested and how?

- [ ] Unit tests written/updated
- [ ] Manual testing performed
- [ ] Code compiles successfully in local env
- [ ] Deploy to BLD from Feature branch

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

After generating the description, DO NOT call create_pull_request. Just show the description to the user."""

        user_message = f"""Please generate a PR description (summary only - do not create the actual PR):

**Source Branch**: {source_branch}
**Target Branch**: {target_branch}
**Work Item ID**: {work_item_id}

**CRITICAL STEPS**:
1. Call get_work_item({work_item_id})
2. Call verify_branches("{source_branch}", "{target_branch}")
3. **MANDATORY** - Call analyze_code_changes("{source_branch}", "{target_branch}")
4. Generate the complete PR description following the format above

**DO NOT call create_pull_request - just show me the PR description.**"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]

        tools = self.ado_tools.get_all_tools()

        print("🧠 AI Agent analyzing and generating summary...")
        print()

        result = self.ai_client.chat_with_functions(
            messages=messages,
            functions=tools,
            max_iterations=10,
            temperature=0.1
        )

        print()
        print("✅ Summary Generated")
        print("=" * 80)
        print(result['response'])
        print("=" * 80)
        print()

        return {
            "success": True,
            "pr_summary": result['response'],
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
