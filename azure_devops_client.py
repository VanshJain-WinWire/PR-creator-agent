"""
Azure DevOps API Client
Handles work items, pull requests, and repository operations
"""
import os
import base64
import requests
from typing import Dict, Any, Optional, List
from dataclasses import dataclass


@dataclass
class WorkItem:
    id: int
    title: str
    description: str
    work_item_type: str
    state: str
    assigned_to: Optional[str] = None
    acceptance_criteria: Optional[str] = None


@dataclass
class PullRequest:
    pull_request_id: int
    title: str
    description: str
    source_ref: str
    target_ref: str
    status: str
    url: str
    web_url: str


class AzureDevOpsClient:
    def __init__(self, org_url: str, project: str, pat: str):
        """Initialize Azure DevOps client with organization details"""
        self.org_url = org_url.rstrip('/')
        self.project = project
        self.pat = pat
        self.base_url = f"{self.org_url}/{self.project}/_apis"
        
        # Create authorization header
        auth_string = f":{self.pat}"
        self.auth_header = base64.b64encode(auth_string.encode()).decode()
        self.headers = {
            "Authorization": f"Basic {self.auth_header}",
            "Content-Type": "application/json; charset=utf-8"
        }
    
    def get_work_item(self, work_item_id: int) -> WorkItem:
        """Fetch work item details from Azure DevOps"""
        url = f"{self.org_url}/_apis/wit/workitems/{work_item_id}?api-version=7.0"
        
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        
        data = response.json()
        fields = data.get("fields", {})
        
        return WorkItem(
            id=work_item_id,
            title=fields.get("System.Title", ""),
            description=fields.get("System.Description", ""),
            work_item_type=fields.get("System.WorkItemType", ""),
            state=fields.get("System.State", ""),
            assigned_to=fields.get("System.AssignedTo", {}).get("displayName"),
            acceptance_criteria=fields.get("Microsoft.VSTS.Common.AcceptanceCriteria", "")
        )
    
    def create_pull_request(
        self,
        repo_id: str,
        source_branch: str,
        target_branch: str,
        title: str,
        description: str,
        work_item_ids: Optional[List[int]] = None
    ) -> PullRequest:
        """Create a pull request in Azure DevOps"""
        url = f"{self.base_url}/git/repositories/{repo_id}/pullrequests?api-version=7.0"
        
        # Ensure branches have refs/heads/ prefix
        if not source_branch.startswith("refs/heads/"):
            source_branch = f"refs/heads/{source_branch}"
        if not target_branch.startswith("refs/heads/"):
            target_branch = f"refs/heads/{target_branch}"
        
        # Build request body
        body = {
            "sourceRefName": source_branch,
            "targetRefName": target_branch,
            "title": title,
            "description": description,
            "isDraft": True
        }
        
        # Add work item references if provided
        if work_item_ids:
            body["workItemRefs"] = [{"id": str(wid)} for wid in work_item_ids]
        
        response = requests.post(url, headers=self.headers, json=body)
        response.raise_for_status()
        
        data = response.json()
        
        # Build web URL
        pr_id = data.get("pullRequestId")
        web_url = f"{self.org_url}/{self.project}/_git/{data.get('repository', {}).get('name', 'repo')}/pullrequest/{pr_id}"
        
        return PullRequest(
            pull_request_id=pr_id,
            title=data.get("title", ""),
            description=data.get("description", ""),
            source_ref=data.get("sourceRefName", ""),
            target_ref=data.get("targetRefName", ""),
            status=data.get("status", ""),
            url=data.get("url", ""),
            web_url=web_url
        )
    
    def list_repository_refs(self, repo_id: str) -> List[Dict[str, Any]]:
        """List all branches in the repository"""
        url = f"{self.base_url}/git/repositories/{repo_id}/refs?api-version=7.0"
        
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        
        return response.json().get("value", [])
    
    def verify_branch_exists(self, repo_id: str, branch_name: str) -> bool:
        """Check if a branch exists in the repository"""
        refs = self.list_repository_refs(repo_id)
        
        # Normalize branch name
        if not branch_name.startswith("refs/heads/"):
            branch_name = f"refs/heads/{branch_name}"
        
        return any(ref.get("name") == branch_name for ref in refs)
    
    def list_branches(self, repo_id: str) -> List[Dict[str, Any]]:
        """List all branches in the repository"""
        url = f"{self.base_url}/git/repositories/{repo_id}/refs?filter=heads/&api-version=7.0"
        
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        
        return response.json().get("value", [])
    
    def get_commits(self, repo_id: str, branch: str, top: int = 10) -> List[Dict[str, Any]]:
        """Get recent commits from a branch"""
        # Normalize branch name
        if not branch.startswith("refs/heads/"):
            branch = f"refs/heads/{branch}"
        
        url = f"{self.base_url}/git/repositories/{repo_id}/commits?searchCriteria.itemVersion.version={branch}&$top={top}&api-version=7.0"
        
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        
        commits = response.json().get("value", [])
        
        # Simplify commit info
        return [{
            "commitId": c.get("commitId"),
            "comment": c.get("comment"),
            "author": c.get("author", {}).get("name"),
            "date": c.get("author", {}).get("date")
        } for c in commits]
