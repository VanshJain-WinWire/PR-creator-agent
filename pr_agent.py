"""
PR Agent - Main Orchestrator
Coordinates work item fetching, change analysis, and PR creation
"""
import os
from typing import Dict, Any
from azure_devops_client import AzureDevOpsClient, WorkItem, PullRequest
from pr_summary_generator import PRSummaryGenerator


class PRAgent:
    def __init__(
        self,
        ado_org_url: str,
        ado_project: str,
        ado_pat: str,
        repo_id: str,
        repo_path: str
    ):
        """Initialize PR Agent with Azure DevOps and Git configuration"""
        self.ado_client = AzureDevOpsClient(ado_org_url, ado_project, ado_pat)
        self.repo_id = repo_id
        self.summary_generator = PRSummaryGenerator(repo_path)
        self.org_url = ado_org_url
        self.project = ado_project
    
    def create_pr(
        self,
        source_branch: str,
        target_branch: str,
        work_item_id: int
    ) -> Dict[str, Any]:
        """
        Create a pull request with automatic work item linking and summary generation
        
        Args:
            source_branch: Feature branch name (e.g., 'feature/my-branch')
            target_branch: Target branch name (e.g., 'develop' or 'main')
            work_item_id: Azure DevOps work item ID
        
        Returns:
            Dictionary containing PR details, work item info, and change summary
        """
        
        # Step 1: Verify branches exist
        print(f"🔍 Verifying branches...")
        if not self.ado_client.verify_branch_exists(self.repo_id, source_branch):
            raise ValueError(f"Source branch '{source_branch}' does not exist")
        
        if not self.ado_client.verify_branch_exists(self.repo_id, target_branch):
            raise ValueError(f"Target branch '{target_branch}' does not exist")
        
        # Step 2: Fetch work item details
        print(f"📋 Fetching work item #{work_item_id}...")
        work_item = self.ado_client.get_work_item(work_item_id)
        print(f"   ✓ Work Item: {work_item.title}")
        
        # Step 3: Analyze changes between branches
        print(f"📊 Analyzing changes between {source_branch} and {target_branch}...")
        file_changes, change_summary = self.summary_generator.analyze_changes(
            source_branch=source_branch,
            target_branch=target_branch
        )
        print(f"   ✓ Found {len(file_changes)} changed files")
        
        # Step 4: Generate PR description
        print(f"✍️ Generating PR description...")
        pr_description = self.summary_generator.generate_pr_description(
            source_branch=source_branch,
            target_branch=target_branch,
            work_item=work_item,
            change_summary=change_summary
        )
        
        # Step 5: Create PR title
        pr_title = f"{work_item.title} (AB#{work_item_id})"
        
        # Step 6: Create the pull request
        print(f"🚀 Creating pull request...")
        pull_request = self.ado_client.create_pull_request(
            repo_id=self.repo_id,
            source_branch=source_branch,
            target_branch=target_branch,
            title=pr_title,
            description=pr_description,
            work_item_ids=[work_item_id]
        )
        
        print(f"   ✓ PR #{pull_request.pull_request_id} created successfully!")
        print(f"   🔗 {pull_request.web_url}")
        
        # Return comprehensive result
        return {
            "pull_request": pull_request,
            "work_item": work_item,
            "changes": {
                "total": len(file_changes),
                "added": [f for f in file_changes if f.status == 'A'],
                "modified": [f for f in file_changes if f.status == 'M'],
                "deleted": [f for f in file_changes if f.status == 'D']
            },
            "summary": change_summary
        }
    
    def get_work_item_info(self, work_item_id: int) -> WorkItem:
        """Fetch work item details without creating PR"""
        return self.ado_client.get_work_item(work_item_id)
    
    def preview_changes(self, source_branch: str, target_branch: str) -> Dict[str, Any]:
        """Preview changes without creating PR"""
        file_changes, change_summary = self.summary_generator.analyze_changes(
            source_branch=source_branch,
            target_branch=target_branch
        )
        
        return {
            "file_changes": file_changes,
            "summary": change_summary
        }


def main():
    """CLI entry point for testing"""
    import sys
    from dotenv import load_dotenv
    
    load_dotenv()
    
    # Initialize agent
    agent = PRAgent(
        ado_org_url=os.getenv("AZURE_DEVOPS_ORG_URL"),
        ado_project=os.getenv("AZURE_DEVOPS_PROJECT"),
        ado_pat=os.getenv("AZURE_DEVOPS_PAT"),
        repo_id=os.getenv("AZURE_DEVOPS_REPO_ID"),
        repo_path=os.getenv("GIT_REPO_PATH")
    )
    
    # Parse command line arguments
    if len(sys.argv) < 4:
        print("Usage: python pr_agent.py <source_branch> <target_branch> <work_item_id>")
        print("Example: python pr_agent.py feature/my-branch develop 105550")
        sys.exit(1)
    
    source_branch = sys.argv[1]
    target_branch = sys.argv[2]
    work_item_id = int(sys.argv[3])
    
    try:
        # Create PR
        result = agent.create_pr(
            source_branch=source_branch,
            target_branch=target_branch,
            work_item_id=work_item_id
        )
        
        print("\n" + "="*60)
        print("✅ SUCCESS!")
        print("="*60)
        print(f"PR URL: {result['pull_request'].web_url}")
        print(f"PR ID: {result['pull_request'].pull_request_id}")
        print(f"Title: {result['pull_request'].title}")
        print(f"Status: {result['pull_request'].status}")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
