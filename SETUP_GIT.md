# Git and GitHub Setup Guide

## Quick Start

Your project is already initialized with Git! Follow these steps to push to GitHub:

## Option 1: Create Repository on GitHub Website (Recommended for First Time)

1. Go to https://github.com/new
2. Create a new repository:
   - Repository name: `nj-cad-dv-analysis`
   - Description: "NJ CAD/RMS and Domestic Violence Data Analysis"
   - Choose Public or Private
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
3. Click "Create repository"

4. Add the remote:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/nj-cad-dv-analysis.git
   ```

5. Push your code:
   ```bash
   git push -u origin main
   ```

## Option 2: Use Automation Script (Requires GitHub Token)

### Step 1: Get GitHub Personal Access Token

1. Go to: https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Name it: "CAD-DV-Analysis"
4. Select these permissions:
   - ✅ `repo` (all permissions)
5. Click "Generate token"
6. Copy the token (you won't see it again!)

### Step 2: Configure Local Environment

1. Copy the example env file:
   ```bash
   copy .env.example .env
   ```

2. Edit `.env` and add your credentials:
   ```
   GITHUB_TOKEN=your_token_here
   GITHUB_USERNAME=your_github_username
   GITHUB_REPO=nj-cad-dv-analysis
   ```

### Step 3: Install Dependencies (for GitHub automation)

```bash
pip install PyGithub python-dotenv
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

### Step 4: Create Repository Automatically

```bash
python git_automation.py --create-repo
```

This will:
- Create the GitHub repository
- Add it as remote
- Configure everything automatically

### Step 5: Push Your Code

```bash
python git_automation.py --commit-push "Initial commit: Project setup"
```

## Ongoing Workflow

### After Making Changes

```bash
# Commit and push in one command
python git_automation.py --commit-push "Your descriptive commit message"

# Or manually
git add .
git commit -m "Your message"
git push
```

### Other Useful Commands

```bash
# Check repository status
python git_automation.py --status

# Create a tagged release
python git_automation.py --tag-release v1.0.0 "First release"

# Sync with remote
python git_automation.py --sync

# Just push existing commits
python git_automation.py --push
```

## Troubleshooting

### "Repository already exists"
This is fine! It means the GitHub repo is already created. Just push your code:
```bash
git push -u origin main
```

### "Permission denied"
Make sure you're using HTTPS with a token, not SSH:
```bash
git remote set-url origin https://github.com/USERNAME/nj-cad-dv-analysis.git
```

### "Remote origin already exists"
Remove and re-add it:
```bash
git remote remove origin
git remote add origin https://github.com/USERNAME/nj-cad-dv-analysis.git
```

### Push Failed
If you see "Push failed", you may need to pull first:
```bash
git pull origin main --allow-unrelated-histories
git push origin main
```

## What's Already Committed

✅ All project structure and code files
✅ AI data analyzer script
✅ ETL pipeline framework
✅ README and documentation
✅ .gitignore configured properly

## Important Notes

- **Large data files are excluded** by .gitignore
- **Sensitive data** should NOT be committed
- **Logs and processed data** are excluded
- Only **code and configuration** are tracked

## Next Steps After GitHub Setup

1. Add your raw data files to `raw_data/` directories
2. Run `python ai_data_analyzer.py` to analyze data
3. Review AI responses in `analysis/ai_responses/`
4. Build ETL pipelines as needed
5. Commit your work regularly!

