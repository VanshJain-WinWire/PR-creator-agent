# PR Summary Generation Plan

## Overview

The PR Creator Agent uses a sophisticated multi-step process to generate intelligent, context-aware PR summaries that save developers time and improve code review quality.

## Process Flow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. USER INPUT                                               │
│   - Source Branch: feature/azure_blob_storage               │
│   - Target Branch: develop                                  │
│   - Work Item ID: 105550                                    │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. BRANCH VERIFICATION                                      │
│   ✓ Check if source branch exists in remote                │
│   ✓ Check if target branch exists in remote                │
│   ✗ Fail fast if branches don't exist                      │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. WORK ITEM FETCHING (Azure DevOps REST API)              │
│                                                             │
│   GET /wit/workitems/{id}                                   │
│                                                             │
│   Extract:                                                  │
│   • Title: "Allow input file upload in all phases"         │
│   • Description: HTML/plain text                            │
│   • Type: User Story / Bug / Task                           │
│   • State: Active / Resolved / Closed                       │
│   • Acceptance Criteria: Requirements list                  │
│   • Assigned To: Developer name                             │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. GIT DIFF ANALYSIS (Local Repository)                    │
│                                                             │
│   A. Get Commit Objects:                                    │
│      base_commit = repo.commit("develop")                   │
│      head_commit = repo.commit("feature/azure_blob_storage")│
│                                                             │
│   B. Calculate Diff:                                        │
│      diff_index = base_commit.diff(head_commit)             │
│                                                             │
│   C. For Each File Change:                                  │
│      - Path: AI-SDLC-API/Services/AzureBlobStorageService.cs│
│      - Status: A (Added) / M (Modified) / D (Deleted)       │
│      - Lines Added: +150                                    │
│      - Lines Removed: -20                                   │
│                                                             │
│   Output: List[FileChange]                                  │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. FILE CATEGORIZATION (Pattern Matching)                  │
│                                                             │
│   Rules:                                                    │
│   • Path contains "Service" → Category: service             │
│   • Path contains "Controller" → Category: controller       │
│   • Path contains "Test" → Category: test                   │
│   • Extension .md/.txt → Category: documentation            │
│   • Extension .json/.config → Category: configuration       │
│   • Path contains "Model" or "DB" → Category: model         │
│                                                             │
│   Example:                                                  │
│   Services/RequirementGeneratorService.cs → service (NEW)   │
│   Controllers/WinAIController.cs → controller (MODIFIED)    │
│   REFACTORING-SUMMARY.md → documentation (ADDED)            │
│   appsettings.json → configuration (MODIFIED)               │
│                                                             │
│   Output: Categorized FileChange objects                    │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. CHANGE SUMMARY AGGREGATION                               │
│                                                             │
│   Group by category:                                        │
│                                                             │
│   Features & Enhancements:                                  │
│   • ✨ Services/RequirementGeneratorService.cs (NEW)        │
│   • 🔧 Controllers/WinAIController.cs (MODIFIED)            │
│   • ✨ Services/OnCallSupportService.cs (NEW)               │
│                                                             │
│   Refactoring:                                              │
│   • 🔧 Services/ProjectService.cs (MODIFIED)                │
│                                                             │
│   Configuration:                                            │
│   • 🔧 appsettings.json (MODIFIED)                          │
│   • 🔧 Program.cs (MODIFIED - DI registration)              │
│                                                             │
│   Documentation:                                            │
│   • ✨ REFACTORING-SUMMARY.md (NEW)                         │
│                                                             │
│   Output: ChangeSummary object with categorized lists       │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│ 7. PR DESCRIPTION GENERATION (Markdown Assembly)           │
│                                                             │
│   Template Structure:                                       │
│   ┌───────────────────────────────────────────────┐        │
│   │ ## Summary                                    │        │
│   │ [Auto: Work item title + brief context]      │        │
│   │                                               │        │
│   │ ## Work Item Context                          │        │
│   │ **Work Item:** AB#105550 - [Title]            │        │
│   │ **Type:** User Story                          │        │
│   │ **State:** Active                             │        │
│   │ [Description from work item]                  │        │
│   │                                               │        │
│   │ ### Acceptance Criteria                       │        │
│   │ [From work item fields]                       │        │
│   │                                               │        │
│   │ ## Changes Made                               │        │
│   │                                               │        │
│   │ ### 🚀 Features & Enhancements                │        │
│   │ - ✨ **File**: Description                    │        │
│   │                                               │        │
│   │ ### ♻️ Refactoring                            │        │
│   │ - 🔧 **File**: Description                    │        │
│   │                                               │        │
│   │ [... other categories ...]                    │        │
│   │                                               │        │
│   │ ## Testing                                    │        │
│   │ - [ ] Unit tests added/updated                │        │
│   │ - [ ] Integration tests passed                │        │
│   │ - [ ] Manual testing completed                │        │
│   │                                               │        │
│   │ ## Related Work Items                         │        │
│   │ Fixes AB#105550                               │        │
│   └───────────────────────────────────────────────┘        │
│                                                             │
│   Output: Markdown string (PR description)                  │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│ 8. PR CREATION (Azure DevOps REST API)                     │
│                                                             │
│   POST /git/repositories/{repoId}/pullrequests              │
│                                                             │
│   Body:                                                     │
│   {                                                         │
│     "sourceRefName": "refs/heads/feature/azure_blob_storage"│
│     "targetRefName": "refs/heads/develop",                  │
│     "title": "[Work Item Title] (AB#105550)",               │
│     "description": "[Generated markdown from step 7]",      │
│     "workItemRefs": [{"id": "105550"}]                      │
│   }                                                         │
│                                                             │
│   Response:                                                 │
│   {                                                         │
│     "pullRequestId": 5870,                                  │
│     "status": "active",                                     │
│     "url": "https://dev.azure.com/.../pullRequests/5870"    │
│   }                                                         │
│                                                             │
│   Output: PullRequest object with web URL                   │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│ 9. RESULT RETURNED                                          │
│                                                             │
│   {                                                         │
│     "pull_request": {                                       │
│       "pull_request_id": 5870,                              │
│       "title": "...",                                       │
│       "web_url": "https://...",                             │
│       "status": "active"                                    │
│     },                                                      │
│     "work_item": { ... },                                   │
│     "changes": {                                            │
│       "total": 12,                                          │
│       "added": [FileChange, ...],                           │
│       "modified": [FileChange, ...],                        │
│       "deleted": []                                         │
│     },                                                      │
│     "summary": ChangeSummary { ... }                        │
│   }                                                         │
└─────────────────────────────────────────────────────────────┘
```

## Key Features

### 1. Intelligent File Categorization
```python
def _categorize_file(file_path: str) -> str:
    file_path_lower = file_path.lower()
    
    # Pattern matching
    if 'test' in file_path_lower:
        return 'test'
    if 'service' in file_path_lower:
        return 'service'
    if 'controller' in file_path_lower:
        return 'controller'
    # ... more patterns
```

**Why?** Different file types require different descriptions. Services are "business logic", controllers are "API endpoints", tests are "test coverage".

### 2. Status Icons
```python
status_icon = {
    'A': '✨',  # Added - New file
    'M': '🔧',  # Modified - Changed file
    'D': '🗑️',  # Deleted - Removed file
    'R': '📝'   # Renamed - Moved/renamed
}
```

**Why?** Visual indicators make PR reviews faster and more intuitive.

### 3. Work Item Integration
- Pulls actual work item data from Azure DevOps
- Includes acceptance criteria in PR description
- Automatically links with "Fixes AB#105550" syntax
- Provides context for reviewers

**Why?** Reviewers need to understand *why* changes were made, not just *what* changed.

### 4. Automatic Categorization
Changes are grouped into meaningful sections:
- **Features** - New functionality
- **Refactoring** - Code improvements
- **Bug Fixes** - Issue resolutions
- **Tests** - Test additions/updates
- **Configuration** - Config changes
- **Documentation** - Docs updates

**Why?** Helps reviewers prioritize what to review first and understand the scope.

## Teams Bot Integration

```
User in Teams: "create pr from feature/my-branch for work item 12345"
                │
                ▼
         [Teams Bot Parser]
                │
         Extract: branch="feature/my-branch"
                  work_item_id=12345
                  target="develop" (default)
                │
                ▼
         [PR Agent.create_pr()]
                │
         Steps 1-9 above
                │
                ▼
         [Format Response Card]
                │
                ▼
User receives: "✅ PR #5870 created successfully!
                🔗 [View PR](https://...)"
```

## Performance

- **Branch Verification**: ~500ms (API call)
- **Work Item Fetch**: ~800ms (API call)
- **Git Diff Analysis**: ~2-5 seconds (local, depends on repo size)
- **PR Creation**: ~1-2 seconds (API call)

**Total**: ~5-10 seconds for complete PR creation

## Future Enhancements

1. **AI-Powered Summaries** - Use OpenAI GPT-4 to analyze diffs and generate human-like descriptions
2. **Smart Bug Detection** - Analyze commit messages and file changes to detect bug fixes automatically
3. **Test Coverage Analysis** - Calculate test coverage delta
4. **Code Quality Metrics** - Include complexity analysis
5. **Auto-Reviewer Assignment** - Suggest reviewers based on file ownership
6. **Multi-Repo Support** - Handle PRs across multiple repositories
7. **Draft PR Mode** - Create draft PRs for work in progress

## Error Handling

All stages include error handling:
- Branch not found → Clear error message
- Work item access denied → Permission error
- Git repo not accessible → Path error
- API rate limits → Retry with exponential backoff

## Security

- PAT tokens stored in environment variables (never in code)
- HTTPS for all API calls
- No sensitive data in logs
- Teams bot uses Microsoft authentication

---

**This plan ensures:**
✅ Comprehensive PR descriptions
✅ Fast execution (< 10 seconds)
✅ Human-readable output
✅ Context-aware summaries
✅ Automatic work item linking
✅ Easy integration (CLI, Python, Teams)
