"""
Azure DevOps Tools for AI Agent
Provides callable functions that the AI agent can use to interact with Azure DevOps
"""
import json
from typing import Dict, Any, List, Optional
from azure_devops_client import AzureDevOpsClient, WorkItem
from pr_summary_generator import PRSummaryGenerator
from ai_foundry_client import tool_schema


class AzureDevOpsTools:
    """Collection of Azure DevOps tools for AI agents"""
    
    def __init__(
        self,
        ado_org_url: str,
        ado_project: str,
        ado_pat: str,
        repo_id: str,
        repo_path: str
    ):
        """Initialize Azure DevOps tools with credentials and repository info"""
        self.ado_client = AzureDevOpsClient(ado_org_url, ado_project, ado_pat)
        self.repo_id = repo_id
        self.repo_path = repo_path
        self.summary_generator = PRSummaryGenerator(repo_path)
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
        """Analyze changes between branches"""
        try:
            file_changes, change_summary = self.summary_generator.analyze_changes(
                source_branch=source_branch,
                target_branch=target_branch
            )
            
            return {
                "success": True,
                "total_files_changed": len(file_changes),
                "changes": {
                    "added_files": [f.path for f in file_changes if f.status == 'A'],
                    "modified_files": [f.path for f in file_changes if f.status == 'M'],
                    "deleted_files": [f.path for f in file_changes if f.status == 'D']
                },
                "summary": {
                    "features": change_summary.features,
                    "bug_fixes": change_summary.bug_fixes,
                    "refactoring": change_summary.refactoring,
                    "tests": change_summary.tests,
                    "documentation": change_summary.documentation,
                    "configuration": change_summary.configuration
                }
            }
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
            pr = self.ado_client.create_pull_request(
                repo_id=self.repo_id,
                source_branch=source_branch,
                target_branch=target_branch,
                title=title,
                description=description,
                work_item_ids=work_item_ids
            )
            
            return {
                "success": True,
                "pull_request": {
                    "id": pr.pull_request_id,
                    "title": pr.title,
                    "url": pr.web_url,
                    "status": pr.status,
                    "source_branch": pr.source_ref,
                    "target_branch": pr.target_ref
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
