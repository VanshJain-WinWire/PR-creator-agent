"""
PR Summary Generator
Analyzes git diffs and generates comprehensive PR summaries
"""
import os
import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from git import Repo
from azure_devops_client import WorkItem


@dataclass
class FileChange:
    path: str
    status: str  # M=Modified, A=Added, D=Deleted, R=Renamed
    additions: int = 0
    deletions: int = 0
    category: Optional[str] = None


@dataclass
class ChangeSummary:
    features: List[str] = field(default_factory=list)
    bug_fixes: List[str] = field(default_factory=list)
    refactoring: List[str] = field(default_factory=list)
    tests: List[str] = field(default_factory=list)
    documentation: List[str] = field(default_factory=list)
    configuration: List[str] = field(default_factory=list)
    other: List[str] = field(default_factory=list)


class PRSummaryGenerator:
    def __init__(self, repo_path: str):
        """Initialize with local git repository path"""
        self.repo = Repo(repo_path)
    
    def analyze_changes(
        self,
        source_branch: str,
        target_branch: str
    ) -> Tuple[List[FileChange], ChangeSummary]:
        """Analyze all changes between source and target branches"""
        
        # Get the diff between branches
        base = self.repo.commit(target_branch)
        head = self.repo.commit(source_branch)
        
        # Get diff stats
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
            
            file_change = FileChange(
                path=file_path,
                status=status,
                category=self._categorize_file(file_path)
            )
            
            file_changes.append(file_change)
        
        # Categorize changes into summary
        change_summary = self._generate_change_summary(file_changes)
        
        return file_changes, change_summary
    
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
    
    def generate_pr_description(
        self,
        source_branch: str,
        target_branch: str,
        work_item: WorkItem,
        change_summary: ChangeSummary
    ) -> str:
        """Generate complete PR description in markdown format"""
        
        pr_body = f"""## Summary
This PR addresses work item AB#{work_item.id} - {work_item.title}.

## Work Item Context
**Work Item:** AB#{work_item.id} - {work_item.title}
**Type:** {work_item.work_item_type}
**State:** {work_item.state}

{self._format_description(work_item.description)}

"""
        
        if work_item.acceptance_criteria:
            pr_body += f"""### Acceptance Criteria
{self._format_description(work_item.acceptance_criteria)}

"""
        
        pr_body += """## Changes Made

"""
        
        # Add each category if it has changes
        if change_summary.features:
            pr_body += "### 🚀 Features & Enhancements\n"
            for item in change_summary.features:
                pr_body += f"- {item}\n"
            pr_body += "\n"
        
        if change_summary.refactoring:
            pr_body += "### ♻️ Refactoring\n"
            for item in change_summary.refactoring:
                pr_body += f"- {item}\n"
            pr_body += "\n"
        
        if change_summary.bug_fixes:
            pr_body += "### 🐛 Bug Fixes\n"
            for item in change_summary.bug_fixes:
                pr_body += f"- {item}\n"
            pr_body += "\n"
        
        if change_summary.tests:
            pr_body += "### 🧪 Tests\n"
            for item in change_summary.tests:
                pr_body += f"- {item}\n"
            pr_body += "\n"
        
        if change_summary.configuration:
            pr_body += "### ⚙️ Configuration\n"
            for item in change_summary.configuration:
                pr_body += f"- {item}\n"
            pr_body += "\n"
        
        if change_summary.documentation:
            pr_body += "### 📚 Documentation\n"
            for item in change_summary.documentation:
                pr_body += f"- {item}\n"
            pr_body += "\n"
        
        pr_body += f"""## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests passed
- [ ] Manual testing completed

## Related Work Items
Fixes AB#{work_item.id}
"""
        
        return pr_body
    
    def _format_description(self, text: Optional[str]) -> str:
        """Clean and format HTML description text"""
        if not text:
            return ""
        
        # Remove HTML tags (basic cleanup)
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'&nbsp;', ' ', text)
        text = re.sub(r'&amp;', '&', text)
        text = text.strip()
        
        return text if text else "No description provided."
