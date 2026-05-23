# Windows Installation Guide

## Issue

You encountered build errors when installing Python packages:
- `aiohttp` requires Visual C++ compiler
- `pydantic-core` requires Rust compiler

These errors occur because:
1. You're using **Python 3.14** (very new, limited pre-built wheels)
2. Teams bot dependencies (`aiohttp`, `pydantic`) need compilation on Windows

## ✅ Solution (Already Applied)

I've restructured the project so you can use it **without Teams bot**:

### What Changed:
1. **`requirements.txt`** - Now contains only core dependencies (✅ already installed successfully!)
2. **`requirements-teams.txt`** - NEW file for optional Teams bot dependencies
3. **`test_setup.py`** - NEW script to verify your setup works
4. **Updated documentation** - Clearer instructions for Windows users

## 🚀 Quick Start (Core Features)

You can now use the PR Creator Agent via CLI or Python!

### 1. Configure Environment

```bash
# Already done: pip install -r requirements.txt ✓

# Copy and edit .env
copy .env.example .env
```

Edit `.env` with your values:
```env
AZURE_DEVOPS_ORG_URL=https://dev.azure.com/winwire
AZURE_DEVOPS_PROJECT=AI-SDLC
AZURE_DEVOPS_PAT=<your_token_here>
AZURE_DEVOPS_REPO_ID=dea47add-b82d-45e2-942a-ac97c4b17a31
GIT_REPO_PATH=c:\Users\Vanshjain\Project\aisdlc-api
DEFAULT_TARGET_BRANCH=develop
```

### 2. Test Setup

```bash
python test_setup.py
```

This will verify:
- ✓ Environment variables are set
- ✓ Python modules load correctly
- ✓ Azure DevOps connection works

### 3. Create Your First PR

```bash
python pr_agent.py feature/azure_blob_storage develop 105550
```

## 🤖 Teams Bot (Optional)

If you want the Teams bot feature, you have **3 options**:

### Option A: Use Python 3.11 or 3.12 (Recommended)

1. Install Python 3.12 from [python.org](https://www.python.org/downloads/)
2. Create new virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
3. Install all dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-teams.txt
   ```

### Option B: Install Visual C++ Build Tools

1. Download: https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. During installation, select **"Desktop development with C++"**
3. Restart terminal
4. Install Teams dependencies:
   ```bash
   pip install -r requirements-teams.txt
   ```

### Option C: Skip Teams Bot

Just use CLI or Python! The Teams bot is optional. You get all the core functionality without it:
- ✅ Create PRs from command line
- ✅ Work item integration
- ✅ Intelligent summary generation
- ✅ Automatic linking
- ❌ Teams chat interface (optional)

## 📊 What You Can Do Now

### Without Teams Bot (Works Now!)

```bash
# Create PR via CLI
python pr_agent.py <source_branch> <target_branch> <work_item_id>

# Or use Python script
python
>>> from pr_agent import PRAgent
>>> agent = PRAgent(...)
>>> result = agent.create_pr("feature/my-branch", "develop", 12345)
>>> print(result['pull_request'].web_url)
```

### With Teams Bot (Requires Setup Above)

```
[In Teams]
User: create pr from feature/my-branch for work item 12345
Bot: ✅ PR #5870 created! 🔗 [View PR](https://...)
```

## 🧪 Testing Checklist

- [ ] Edit `.env` with your Azure DevOps details
- [ ] Run `python test_setup.py` (should show ✅ SUCCESS!)
- [ ] Test PR creation: `python pr_agent.py feature/test develop 105550`
- [ ] (Optional) Install Teams dependencies and test `python app.py`

## 📝 Next Steps

1. **Configure .env** (see step 1 above)
2. **Run test_setup.py** to verify everything works
3. **Create your first PR** using the CLI
4. **Read QUICKSTART.md** for more examples
5. **(Optional) Set up Teams bot** when you need it

## 💡 Key Points

- ✅ **Core functionality works now** (CLI + Python)
- ✅ **No compiler needed** for core features
- ⚠️ **Teams bot is optional** (requires additional setup on Windows)
- 📚 **Full documentation** in README.md and QUICKSTART.md
- 🧪 **Test script** (test_setup.py) to verify everything works

## 🆘 Still Having Issues?

1. Check you're in the right directory: `cd c:\Users\Vanshjain\Project\pr-creator-agent`
2. Verify Python version: `python --version` (should be 3.11-3.14)
3. Check `.env` file has correct values
4. Run test script: `python test_setup.py`
5. See QUICKSTART.md section 6 for detailed troubleshooting

---

**You're all set!** The core PR Creator Agent is ready to use. Teams bot is just an extra feature you can add later if needed.
