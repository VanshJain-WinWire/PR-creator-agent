"""
Microsoft Teams Bot Handler
Handles incoming messages from Teams and orchestrates PR creation
"""
import os
import re
from typing import Optional, Tuple
from botbuilder.core import ActivityHandler, TurnContext, MessageFactory
from botbuilder.schema import ChannelAccount, Activity, ActivityTypes
from pr_agent import PRAgent


class TeamsPRBot(ActivityHandler):
    def __init__(self):
        """Initialize Teams bot with PR Agent"""
        self.pr_agent = PRAgent(
            ado_org_url=os.getenv("AZURE_DEVOPS_ORG_URL"),
            ado_project=os.getenv("AZURE_DEVOPS_PROJECT"),
            ado_pat=os.getenv("AZURE_DEVOPS_PAT"),
            repo_id=os.getenv("AZURE_DEVOPS_REPO_ID"),
            repo_path=os.getenv("GIT_REPO_PATH")
        )
    
    async def on_message_activity(self, turn_context: TurnContext):
        """Handle incoming message from Teams"""
        text = turn_context.activity.text.strip().lower()
        
        # Check for PR creation command
        if "create pr" in text or "create pull request" in text:
            await self._handle_create_pr_command(turn_context, turn_context.activity.text)
        elif "help" in text:
            await self._send_help_message(turn_context)
        else:
            await turn_context.send_activity(
                "I can help you create pull requests! Try:\n"
                "- `create pr` - Start PR creation wizard\n"
                "- `create pr from feature/branch-name for work item 12345` - Create PR directly\n"
                "- `help` - Show all commands"
            )
    
    async def _handle_create_pr_command(self, turn_context: TurnContext, text: str):
        """Handle PR creation command"""
        
        # Send initial acknowledgment
        await turn_context.send_activity("🚀 Starting PR creation process...")
        
        # Parse command for branch and work item
        branch, work_item_id, target_branch = self._parse_pr_command(text)
        
        # If missing information, ask for it
        if not branch:
            await turn_context.send_activity(
                "Which feature branch do you want to create a PR from?\n"
                "Example: `feature/my-branch`"
            )
            # Store state and wait for next message (simplified - use conversation state in production)
            return
        
        if not work_item_id:
            await turn_context.send_activity(
                "What is the work item ID for this PR?\n"
                "Example: `105550`"
            )
            return
        
        # Set default target branch if not provided
        if not target_branch:
            target_branch = os.getenv("DEFAULT_TARGET_BRANCH", "develop")
        
        try:
            # Create the PR using the agent
            await turn_context.send_activity(
                f"📋 Creating PR from `{branch}` to `{target_branch}`...\n"
                f"🔗 Fetching work item #{work_item_id}..."
            )
            
            result = self.pr_agent.create_pr(
                source_branch=branch,
                target_branch=target_branch,
                work_item_id=work_item_id
            )
            
            # Send success message with PR link
            success_card = self._create_pr_success_card(result)
            await turn_context.send_activity(success_card)
            
        except Exception as e:
            await turn_context.send_activity(
                f"❌ Failed to create PR: {str(e)}\n\n"
                "Please check:\n"
                "- Branch names are correct\n"
                "- Work item ID exists\n"
                "- You have permissions to create PRs"
            )
    
    def _parse_pr_command(self, text: str) -> Tuple[Optional[str], Optional[int], Optional[str]]:
        """Parse PR creation command to extract branch and work item"""
        
        # Pattern: "create pr from <branch> for work item <id> to <target>"
        pattern = r"from\s+(\S+).*?(?:work\s*item|wi|#)\s*(\d+).*?(?:to|into)\s+(\S+)"
        match = re.search(pattern, text, re.IGNORECASE)
        
        if match:
            return match.group(1), int(match.group(2)), match.group(3)
        
        # Pattern: "create pr from <branch> for work item <id>" (no target)
        pattern = r"from\s+(\S+).*?(?:work\s*item|wi|#)\s*(\d+)"
        match = re.search(pattern, text, re.IGNORECASE)
        
        if match:
            return match.group(1), int(match.group(2)), None
        
        # Pattern: just branch mentioned
        pattern = r"from\s+(\S+)"
        match = re.search(pattern, text, re.IGNORECASE)
        
        if match:
            return match.group(1), None, None
        
        return None, None, None
    
    def _create_pr_success_card(self, result: dict) -> Activity:
        """Create a rich adaptive card for PR success message"""
        
        pr = result["pull_request"]
        work_item = result["work_item"]
        changes = result["changes"]
        
        message = f"""✅ **Pull Request Created Successfully!**

**PR #{pr.pull_request_id}**: {pr.title}

📊 **Changes Summary:**
- {len(changes['added'])} files added
- {len(changes['modified'])} files modified
- {len(changes['deleted'])} files deleted

🔗 **Links:**
- [View Pull Request]({pr.web_url})
- [View Work Item](https://dev.azure.com/{os.getenv('AZURE_DEVOPS_ORG_URL').split('/')[-1]}/{os.getenv('AZURE_DEVOPS_PROJECT')}/_workitems/edit/{work_item.id})

📝 **Work Item:** AB#{work_item.id} - {work_item.title}

**Status:** {pr.status}
"""
        
        return MessageFactory.text(message)
    
    async def _send_help_message(self, turn_context: TurnContext):
        """Send help message with all available commands"""
        help_text = """🤖 **PR Creator Bot - Help**

**Commands:**

1️⃣ **Create PR with full details:**
`create pr from feature/my-branch for work item 12345 to develop`

2️⃣ **Create PR with default target branch:**
`create pr from feature/my-branch for work item 12345`

3️⃣ **Start PR creation wizard:**
`create pr`

4️⃣ **Get help:**
`help`

**Examples:**
- `create pr from feature/azure_blob_storage for work item 105550`
- `create pr from bugfix/login-issue for wi 12345 to main`

**Features:**
✓ Automatic work item linking
✓ Intelligent PR summary generation
✓ Branch validation
✓ Change analysis
"""
        await turn_context.send_activity(help_text)
    
    async def on_members_added_activity(
        self,
        members_added: list[ChannelAccount],
        turn_context: TurnContext
    ):
        """Handle when bot is added to a conversation"""
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                await turn_context.send_activity(
                    "👋 Hi! I'm the PR Creator Bot.\n\n"
                    "I can help you create pull requests with automatic work item linking!\n\n"
                    "Type `help` to see all available commands."
                )
