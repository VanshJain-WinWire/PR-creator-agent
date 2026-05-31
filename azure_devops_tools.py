"""
Azure DevOps Tools for AI Agent
Provides callable functions that the AI agent can use to interact with Azure DevOps
"""
import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from git import Repo
from azure_devops_client import AzureDevOpsClient, WorkItem
from ai_foundry_client import tool_schema, AIFoundryClient


@dataclass
class FileChange:
    path: str
    status: str  # M=Modified, A=Added, D=Deleted, R=Renamed
    category: Optional[str] = None
    what_changed: Optional[str] = None
    why_changed: Optional[str] = None
    impact: Optional[str] = None


@dataclass
class ChangeSummary:
    features: List[str] = field(default_factory=list)
    bug_fixes: List[str] = field(default_factory=list)
    refactoring: List[str] = field(default_factory=list)
    tests: List[str] = field(default_factory=list)
    documentation: List[str] = field(default_factory=list)
    configuration: List[str] = field(default_factory=list)
    other: List[str] = field(default_factory=list)


class AzureDevOpsTools:
    """Collection of Azure DevOps tools for AI agents"""

    def __init__(
        self,
        ado_org_url: str,
        ado_project: str,
        ado_pat: str,
        repo_id: str,
        repo_path: str,
        ai_client: Optional[AIFoundryClient] = None
    ):
        """Initialize Azure DevOps tools with credentials and repository info"""
        self.ado_client = AzureDevOpsClient(ado_org_url, ado_project, ado_pat)
        self.repo_id = repo_id
        self.repo_path = repo_path
        self.repo = Repo(repo_path)
        self.ai_client = ai_client
        self.org_url = ado_org_url
        self.project = ado_project
    
    @tool_schema({
        "name": "get_work_item",
        "description": "Retrieve details about an Azure DevOps work item (user story, bug, task, etc.) by its ID",
        "parameters": {
            "type": "object",
            "properties": {
                "work_item_id": {
                    "type": "integer",
                    "description": "The ID number of the work item to retrieve"
                }
            },
            "required": ["work_item_id"]
        }
    })
    def get_work_item(self, work_item_id: int) -> Dict[str, Any]:
        """Get work item details from Azure DevOps"""
        try:
            work_item = self.ado_client.get_work_item(work_item_id)
            return {
                "success": True,
                "work_item": {
                    "id": work_item.id,
                    "title": work_item.title,
                    "description": work_item.description,
                    "type": work_item.work_item_type,
                    "state": work_item.state,
                    "assigned_to": work_item.assigned_to,
                    "acceptance_criteria": work_item.acceptance_criteria
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    @tool_schema({
        "name": "verify_branches",
        "description": "Check if source and target branches exist in the repository",
        "parameters": {
            "type": "object",
            "properties": {
                "source_branch": {
                    "type": "string",
                    "description": "The source branch name (e.g., 'feature/my-feature')"
                },
                "target_branch": {
                    "type": "string",
                    "description": "The target branch name (e.g., 'develop' or 'main')"
                }
            },
            "required": ["source_branch", "target_branch"]
        }
    })
    def verify_branches(self, source_branch: str, target_branch: str) -> Dict[str, Any]:
        """Verify that both source and target branches exist"""
        try:
            source_exists = self.ado_client.verify_branch_exists(self.repo_id, source_branch)
            target_exists = self.ado_client.verify_branch_exists(self.repo_id, target_branch)
            
            return {
                "success": True,
                "source_branch": {
                    "name": source_branch,
                    "exists": source_exists
                },
                "target_branch": {
                    "name": target_branch,
                    "exists": target_exists
                },
                "both_exist": source_exists and target_exists
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    @tool_schema({
        "name": "analyze_code_changes",
        "description": "Analyze the code changes between two branches and get a detailed summary of what was modified",
        "parameters": {
            "type": "object",
            "properties": {
                "source_branch": {
                    "type": "string",
                    "description": "The source branch with new changes"
                },
                "target_branch": {
                    "type": "string",
                    "description": "The target branch to compare against"
                }
            },
            "required": ["source_branch", "target_branch"]
        }
    })
    def analyze_code_changes(self, source_branch: str, target_branch: str) -> Dict[str, Any]:
        """Analyze changes between branches using AI"""
        try:
            # Get the diff between branches
            base = self.repo.commit(target_branch)
            head = self.repo.commit(source_branch)
            diff_index = base.diff(head)

            file_changes = []

            for diff in diff_index:
                # Determine status
                if diff.new_file:
                    status = 'A'
                elif diff.deleted_file:
                    status = 'D'
                elif diff.renamed_file:
                    status = 'R'
                else:
                    status = 'M'

                file_path = diff.b_path if diff.b_path else diff.a_path

                # Get actual diff content
                try:
                    # diff.diff can be None, bytes, or string depending on GitPython version
                    if diff.diff:
                        if isinstance(diff.diff, bytes):
                            diff_content = diff.diff.decode('utf-8')
                        elif isinstance(diff.diff, str):
                            diff_content = diff.diff
                        else:
                            diff_content = ""
                    else:
                        # Fallback: use git command directly
                        diff_content = self.repo.git.diff(target_branch, source_branch, '--', file_path)
                except Exception as e:
                    print(f"   ⚠️  Error getting diff for {file_path}: {e}")
                    diff_content = ""

                print(f"   📄 File: {file_path}, Diff size: {len(diff_content)} bytes")

                # Use AI to analyze the diff if AI client is available
                if self.ai_client and diff_content:
                    analysis = self._analyze_diff_with_ai(file_path, diff_content, status)
                else:
                    analysis = {
                        "what_changed": "File modified" if status == 'M' else "File added" if status == 'A' else "File deleted",
                        "why_changed": "Manual analysis not available",
                        "impact": "Unknown"
                    }

                file_change = FileChange(
                    path=file_path,
                    status=status,
                    category=self._categorize_file(file_path),
                    what_changed=analysis.get("what_changed"),
                    why_changed=analysis.get("why_changed"),
                    impact=analysis.get("impact")
                )

                file_changes.append(file_change)

            # Categorize changes into summary
            change_summary = self._generate_change_summary(file_changes)

            # Build detailed file changes with AI-powered analysis
            detailed_changes = []
            for fc in file_changes:
                change_detail = {
                    "file": fc.path,
                    "status": fc.status,
                    "category": fc.category,
                    "what_changed": fc.what_changed,
                    "why_changed": fc.why_changed,
                    "impact": fc.impact
                }
                detailed_changes.append(change_detail)

            result = {
                "success": True,
                "total_files_changed": len(file_changes),
                "changes": {
                    "added_files": [f.path for f in file_changes if f.status == 'A'],
                    "modified_files": [f.path for f in file_changes if f.status == 'M'],
                    "deleted_files": [f.path for f in file_changes if f.status == 'D']
                },
                "detailed_changes": detailed_changes,
                "summary": {
                    "features": change_summary.features,
                    "bug_fixes": change_summary.bug_fixes,
                    "refactoring": change_summary.refactoring,
                    "tests": change_summary.tests,
                    "documentation": change_summary.documentation,
                    "configuration": change_summary.configuration
                }
            }

            print(f"\n✅ Analysis complete: {len(file_changes)} files analyzed\n")

            return result
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    @tool_schema({
        "name": "create_pull_request",
        "description": "Create a new pull request in Azure DevOps linking a work item with code changes",
        "parameters": {
            "type": "object",
            "properties": {
                "source_branch": {
                    "type": "string",
                    "description": "The source branch containing changes"
                },
                "target_branch": {
                    "type": "string",
                    "description": "The target branch to merge into"
                },
                "title": {
                    "type": "string",
                    "description": "The pull request title"
                },
                "description": {
                    "type": "string",
                    "description": "The pull request description in markdown format"
                },
                "work_item_ids": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "List of work item IDs to link to this PR"
                }
            },
            "required": ["source_branch", "target_branch", "title", "description"]
        }
    })
    def create_pull_request(
        self,
        source_branch: str,
        target_branch: str,
        title: str,
        description: str,
        work_item_ids: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """Create a pull request"""
        try:
            # pr = self.ado_client.create_pull_request(
            #     repo_id=self.repo_id,
            #     source_branch=source_branch,
            #     target_branch=target_branch,
            #     title=title,
            #     description=description,
            #     work_item_ids=work_item_ids
            # )
            
            return {
                "success": True,
                "pull_request": {
                    "id": pull_request_id,
                    "title": title,
                    "url": pr.web_url,
                    "status": pr.status,
                    "source_branch": source_branch,
                    "target_branch": target_branch,
                    "description": description
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    @tool_schema({
        "name": "list_repository_branches",
        "description": "List all branches in the repository",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    })
    def list_repository_branches(self) -> Dict[str, Any]:
        """List all branches in the repository"""
        try:
            branches = self.ado_client.list_branches(self.repo_id)
            return {
                "success": True,
                "branches": [b['name'].replace('refs/heads/', '') for b in branches],
                "total_count": len(branches)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    @tool_schema({
        "name": "get_commit_details",
        "description": "Get details about recent commits in a branch",
        "parameters": {
            "type": "object",
            "properties": {
                "branch": {
                    "type": "string",
                    "description": "The branch name to get commits from"
                },
                "top": {
                    "type": "integer",
                    "description": "Number of recent commits to retrieve (default: 10)"
                }
            },
            "required": ["branch"]
        }
    })
    def get_commit_details(self, branch: str, top: int = 10) -> Dict[str, Any]:
        """Get recent commit details from a branch"""
        try:
            commits = self.ado_client.get_commits(self.repo_id, branch, top)
            return {
                "success": True,
                "commits": commits,
                "count": len(commits)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _analyze_diff_with_ai(self, file_path: str, diff_content: str, status: str) -> Dict[str, str]:
        """Use AI to analyze what changed and why in the code"""
        # Truncate very large diffs to avoid token limits
        max_diff_length = 4000
        if len(diff_content) > max_diff_length:
            diff_content = diff_content[:max_diff_length] + "\n... (diff truncated)"

        analysis_prompt = f"""Analyze this code change and provide a concise summary.

**File**: {file_path}
**Change Type**: {'Added' if status == 'A' else 'Modified' if status == 'M' else 'Deleted' if status == 'D' else 'Renamed'}

**Diff**:
```diff
{diff_content}
```

Provide your analysis in this exact JSON format:
{{
  "what_changed": "Brief description of what code was added/modified (e.g., 'Added ExportToPdf method with PDF generation logic using iTextSharp')",
  "why_changed": "Why this change was made based on the code context (e.g., 'To provide PDF export functionality for project insights reports')",
  "impact": "Impact of this change (e.g., 'New API endpoint for PDF export, requires iTextSharp dependency')"
}}

Keep each field to 1-2 sentences maximum. Focus on the most significant changes.
"""

        try:
            response = self.ai_client.chat(
                messages=[{"role": "user", "content": analysis_prompt}],
                temperature=0.3,
                max_tokens=500
            )

            # Extract JSON from response
            content = response['choices'][0]['message']['content']

            # Try to parse JSON from response
            # First, try to parse the entire content as JSON
            try:
                analysis = json.loads(content)
                if isinstance(analysis, dict) and 'what_changed' in analysis:
                    return analysis
            except json.JSONDecodeError:
                pass

            # If that fails, look for JSON block in markdown code blocks
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
            if json_match:
                analysis = json.loads(json_match.group(1))
                return analysis

            # Look for JSON object (handle nested braces properly)
            json_match = re.search(r'\{[\s\S]*"what_changed"[\s\S]*"why_changed"[\s\S]*"impact"[\s\S]*\}', content, re.DOTALL)
            if json_match:
                analysis = json.loads(json_match.group())
                return analysis

            # If all parsing fails, use the content directly
            return {
                "what_changed": content[:200] if content else "Code modified",
                "why_changed": "Analysis parsing failed",
                "impact": "Unknown"
            }

        except Exception as e:
            return {
                "what_changed": f"File {'added' if status == 'A' else 'modified' if status == 'M' else 'deleted'}",
                "why_changed": "AI analysis failed",
                "impact": "Unknown"
            }

    def _categorize_file(self, file_path: str) -> str:
        """Categorize file based on path and extension"""
        file_path_lower = file_path.lower()

        # Test files
        if 'test' in file_path_lower or file_path_lower.endswith('.test.cs'):
            return 'test'

        # Documentation
        if file_path_lower.endswith(('.md', '.txt', '.rst')) or 'readme' in file_path_lower:
            return 'documentation'

        # Configuration
        if file_path_lower.endswith(('.json', '.xml', '.yaml', '.yml', '.config', '.ini')):
            return 'configuration'

        # Services (business logic)
        if 'service' in file_path_lower or '/services/' in file_path_lower:
            return 'service'

        # Controllers (API endpoints)
        if 'controller' in file_path_lower or '/controllers/' in file_path_lower:
            return 'controller'

        # Models/Entities
        if 'model' in file_path_lower or '/models/' in file_path_lower or '/db/' in file_path_lower:
            return 'model'

        return 'other'

    def _generate_change_summary(self, file_changes: List[FileChange]) -> ChangeSummary:
        """Generate categorized summary from file changes"""
        summary = ChangeSummary()

        for change in file_changes:
            status_icon = {
                'A': '✨',
                'M': '🔧',
                'D': '🗑️',
                'R': '📝'
            }.get(change.status, '•')

            change_desc = f"{status_icon} **{change.path}**"

            if change.category == 'test':
                summary.tests.append(change_desc)
            elif change.category == 'documentation':
                summary.documentation.append(change_desc)
            elif change.category == 'configuration':
                summary.configuration.append(change_desc)
            elif change.category == 'service':
                if change.status == 'A':
                    summary.features.append(f"{change_desc}: New service added")
                else:
                    summary.refactoring.append(f"{change_desc}: Service refactored")
            elif change.category == 'controller':
                summary.features.append(f"{change_desc}: API endpoint updated")
            elif change.category == 'model':
                summary.features.append(f"{change_desc}: Data model changed")
            else:
                summary.other.append(change_desc)

        return summary

    def get_all_tools(self) -> Dict[str, Any]:
        """Return dictionary of all available tools for the AI agent"""
        return {
            "get_work_item": self.get_work_item,
            "verify_branches": self.verify_branches,
            "analyze_code_changes": self.analyze_code_changes,
            "create_pull_request": self.create_pull_request,
            "list_repository_branches": self.list_repository_branches,
            "get_commit_details": self.get_commit_details
        }
