"""
Git and GitHub Automation Script
Handles repository initialization, commits, pushes, and remote management
"""

import subprocess
import os
import sys
import argparse
from pathlib import Path
from datetime import datetime

# Optional imports for GitHub functionality
try:
    from github import Github
    GITHUB_AVAILABLE = True
except ImportError:
    GITHUB_AVAILABLE = False
    print("Warning: PyGithub not installed. GitHub features will be limited.")

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional

class GitAutomation:
    """Automate Git and GitHub operations"""
    
    def __init__(self, repo_path='.'):
        self.repo_path = Path(repo_path).resolve()
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.github_username = os.getenv('GITHUB_USERNAME', '')
        self.github_repo_name = os.getenv('GITHUB_REPO', 'nj-cad-dv-analysis')
        
    def run_command(self, cmd, check=True):
        """Run a shell command"""
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            if check and result.returncode != 0:
                print(f"Error running command: {cmd}")
                print(result.stderr)
                return False
            return result
        except Exception as e:
            print(f"Exception running command: {e}")
            return False
    
    def is_git_repo(self):
        """Check if current directory is a git repository"""
        result = self.run_command('git rev-parse --git-dir', check=False)
        return result and result.returncode == 0
    
    def init_repo(self):
        """Initialize a new git repository"""
        if self.is_git_repo():
            print("Already a git repository")
            return True
        
        print("Initializing git repository...")
        if self.run_command('git init'):
            # Create .gitignore if it doesn't exist
            gitignore_path = self.repo_path / '.gitignore'
            if not gitignore_path.exists():
                self.create_gitignore()
            
            # Initial commit
            if self.run_command('git add .'):
                return self.run_command('git commit -m "Initial commit: Project setup"')
        
        return False
    
    def create_gitignore(self):
        """Create .gitignore file"""
        gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Jupyter Notebook
.ipynb_checkpoints
*.ipynb

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Environment
.env
.env.local

# Data files (add your specific patterns)
raw_data/**/*.xlsx
raw_data/**/*.csv
*.parquet

# Logs
logs/*.log
*.log

# Analysis outputs (can be large)
# analysis/ai_responses/**/*.json

# Processed data
processed_data/*
!processed_data/.gitkeep
"""
        gitignore_path = self.repo_path / '.gitignore'
        with open(gitignore_path, 'w') as f:
            f.write(gitignore_content)
        print(".gitignore created")
    
    def create_github_repo(self, description=None):
        """Create a new GitHub repository"""
        if not GITHUB_AVAILABLE:
            print("ERROR: PyGithub not installed. Install with: pip install PyGithub")
            return False
        
        if not self.github_token:
            print("ERROR: GITHUB_TOKEN not found in environment variables")
            print("Please set it in .env file or environment")
            return False
        
        try:
            g = Github(self.github_token)
            user = g.get_user()
            
            # Check if repo already exists
            try:
                existing_repo = user.get_repo(self.github_repo_name)
                print(f"Repository already exists: {existing_repo.html_url}")
                return True
            except:
                pass
            
            # Create new repo
            description = description or "NJ CAD/RMS and Domestic Violence Data Analysis"
            repo = user.create_repo(
                self.github_repo_name,
                description=description,
                private=False,
                auto_init=False
            )
            print(f"Repository created: {repo.html_url}")
            
            # Add remote if not exists
            self.add_remote(repo.clone_url)
            
            return True
            
        except Exception as e:
            print(f"Error creating GitHub repository: {e}")
            return False
    
    def add_remote(self, url=None):
        """Add or update git remote"""
        if not url:
            if not self.github_token:
                print("ERROR: Need GitHub URL or GITHUB_TOKEN")
                return False
            url = f"https://github.com/{self.github_username}/{self.github_repo_name}.git"
        
        # Check if remote exists
        result = self.run_command('git remote get-url origin', check=False)
        if result and result.returncode == 0:
            # Update existing remote
            print("Remote 'origin' already exists, updating...")
            self.run_command(f'git remote set-url origin {url}')
        else:
            # Add new remote
            print("Adding remote 'origin'...")
            self.run_command(f'git remote add origin {url}')
        
        print(f"Remote configured: {url}")
        return True
    
    def commit_and_push(self, message, auto_push=True):
        """Commit changes and optionally push to remote"""
        # Check for changes
        status_result = self.run_command('git status --porcelain', check=False)
        if not status_result or not status_result.stdout.strip():
            print("No changes to commit")
            return True
        
        # Add all changes
        if not self.run_command('git add .'):
            return False
        
        # Commit
        commit_msg = message or f"Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        if not self.run_command(f'git commit -m "{commit_msg}"'):
            return False
        
        print("Changes committed successfully")
        
        # Push if requested
        if auto_push:
            return self.push()
        
        return True
    
    def push(self, branch='main'):
        """Push to remote repository"""
        print(f"Pushing to origin/{branch}...")
        
        # Get current branch
        result = self.run_command('git branch --show-current', check=False)
        current_branch = result.stdout.strip() if result else branch
        
        # Push
        if self.run_command(f'git push -u origin {current_branch}', check=False):
            print("Successfully pushed to GitHub")
            return True
        else:
            # Try pushing to existing branch
            if self.run_command(f'git push origin {current_branch}', check=False):
                print("Successfully pushed to GitHub")
                return True
            else:
                print("Push failed. You may need to configure remote or check credentials")
                return False
    
    def create_tag_release(self, tag_name, message=None):
        """Create a git tag and optional GitHub release"""
        tag_msg = message or f"Release {tag_name}"
        
        # Create tag
        if not self.run_command(f'git tag -a {tag_name} -m "{tag_msg}"'):
            return False
        
        # Push tag
        if not self.run_command(f'git push origin {tag_name}'):
            return False
        
        print(f"Tag {tag_name} created and pushed")
        
        # Create GitHub release if token available
        if self.github_token and GITHUB_AVAILABLE:
            try:
                g = Github(self.github_token)
                user = g.get_user()
                repo = user.get_repo(self.github_repo_name)
                
                release = repo.create_git_release(
                    tag=tag_name,
                    name=tag_name,
                    message=tag_msg,
                    draft=False,
                    prerelease=False
                )
                print(f"GitHub release created: {release.html_url}")
            except Exception as e:
                print(f"Note: Could not create GitHub release: {e}")
        
        return True
    
    def get_status(self):
        """Get repository status"""
        print("=== Git Repository Status ===\n")
        
        # Branch info
        result = self.run_command('git branch --show-current', check=False)
        if result:
            print(f"Current branch: {result.stdout.strip()}")
        
        # Remote info
        result = self.run_command('git remote -v', check=False)
        if result and result.stdout.strip():
            print(f"\nRemotes:\n{result.stdout}")
        else:
            print("\nNo remotes configured")
        
        # Status
        result = self.run_command('git status', check=False)
        if result:
            print(f"\n{result.stdout}")
    
    def sync_with_remote(self):
        """Pull latest changes from remote and push local changes"""
        print("Syncing with remote...")
        
        # Fetch first
        self.run_command('git fetch origin', check=False)
        
        # Pull
        result = self.run_command('git pull origin main', check=False)
        if not result:
            # Try master branch
            result = self.run_command('git pull origin master', check=False)
        
        # Push
        self.push()
        
        print("Sync complete")


def main():
    parser = argparse.ArgumentParser(description='Git and GitHub Automation')
    parser.add_argument('--init', action='store_true', help='Initialize git repository')
    parser.add_argument('--create-repo', action='store_true', help='Create GitHub repository')
    parser.add_argument('--commit-push', type=str, metavar='MESSAGE', help='Commit and push changes')
    parser.add_argument('--push', action='store_true', help='Push to remote')
    parser.add_argument('--tag-release', type=str, metavar='TAG', help='Create a tag and release')
    parser.add_argument('--tag-message', type=str, help='Message for tag/release')
    parser.add_argument('--status', action='store_true', help='Show repository status')
    parser.add_argument('--sync', action='store_true', help='Sync with remote')
    parser.add_argument('--repo-name', type=str, help='GitHub repository name')
    parser.add_argument('--repo-path', type=str, default='.', help='Path to repository')
    
    args = parser.parse_args()
    
    automation = GitAutomation(repo_path=args.repo_path)
    
    if args.repo_name:
        automation.github_repo_name = args.repo_name
    
    # Handle commands
    if args.init:
        automation.init_repo()
    elif args.create_repo:
        automation.create_github_repo()
    elif args.commit_push:
        automation.commit_and_push(args.commit_push)
    elif args.push:
        automation.push()
    elif args.tag_release:
        automation.create_tag_release(args.tag_release, args.tag_message)
    elif args.status:
        automation.get_status()
    elif args.sync:
        automation.sync_with_remote()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

