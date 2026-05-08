# GitHub Setup Guide
## The Red Hand & The Eternal Throne: A Bard's Chronicle Website

This guide walks you through setting up a GitHub repository for your book website and collaborating with others.

## Prerequisites

Before starting, ensure you have:

- [ ] A GitHub account (sign up at [github.com](https://github.com))
- [ ] Git installed on your computer
- [ ] Your book website files ready
- [ ] Basic understanding of version control concepts

## Step 1: Create Your GitHub Account

If you don't have a GitHub account:

1. Go to [github.com](https://github.com)
2. Click "Sign up"
3. Choose a username (consider using your author name or book title)
4. Use a professional email address
5. Create a strong password
6. Verify your email address

## Step 2: Install Git

### Windows
1. Download Git from [git-scm.com](https://git-scm.com)
2. Run the installer with default settings
3. Open Command Prompt or PowerShell
4. Verify installation: `git --version`

### macOS
1. Install using Homebrew: `brew install git`
2. Or download from [git-scm.com](https://git-scm.com)
3. Verify installation: `git --version`

### Linux
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install git

# CentOS/RHEL
sudo yum install git

# Verify installation
git --version
```

## Step 3: Configure Git

Set up your identity for commits:

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
git config --global init.defaultBranch main
```

## Step 4: Create Repository

### Option A: GitHub Web Interface

1. Log into GitHub
2. Click the "+" icon in the top right
3. Select "New repository"
4. Repository details:
   - **Name**: `red-hand-chronicle-website` (or your preferred name)
   - **Description**: "Official website for The Red Hand & The Eternal Throne: A Bard's Chronicle"
   - **Visibility**: Public (required for free GitHub Pages)
   - **Initialize**: Check "Add a README file"
   - **License**: Choose MIT or another appropriate license
5. Click "Create repository"

### Option B: Command Line

```bash
# Create and navigate to your project directory
mkdir red-hand-chronicle-website
cd red-hand-chronicle-website

# Initialize Git repository
git init

# Create initial README
echo "# The Red Hand & The Eternal Throne: A Bard's Chronicle Website" > README.md

# Add and commit initial files
git add README.md
git commit -m "Initial commit"

# Connect to GitHub (replace USERNAME and REPOSITORY)
git remote add origin https://github.com/USERNAME/REPOSITORY.git
git push -u origin main
```

## Step 5: Upload Your Website Files

### Method 1: Web Interface (Easiest)

1. Navigate to your repository on GitHub
2. Click "uploading an existing file"
3. Drag and drop all your website files
4. Scroll down to commit section
5. Add commit message: "Add complete book website"
6. Click "Commit changes"

### Method 2: Command Line (Recommended)

```bash
# Clone your repository locally
git clone https://github.com/USERNAME/REPOSITORY.git
cd REPOSITORY

# Copy your website files to this directory
# (index.html, styles.css, script.js, qr-code.html, etc.)

# Add all files to Git
git add .

# Commit with descriptive message
git commit -m "Add complete book website with Celtic theme"

# Push to GitHub
git push origin main
```

## Step 6: Repository Structure

Organize your repository like this:

```
red-hand-chronicle-website/
├── index.html              # Main website
├── styles.css              # Styling
├── script.js               # JavaScript functionality
├── qr-code.html           # QR code sharing page
├── images/                 # Image assets
│   ├── book-cover.jpg
│   ├── author-photo.jpg
│   └── README.txt         # Image specifications
├── README.md              # Project description
├── .gitignore             # Files to ignore
├── deploy-instructions.md  # Deployment guide
└── github-setup.md        # This file
```

## Step 7: Enable GitHub Pages

1. Go to your repository settings
2. Scroll to "Pages" section in left sidebar
3. Under "Source," select "Deploy from a branch"
4. Choose "main" branch and "/ (root)" folder
5. Click "Save"
6. Your website will be available at: `https://USERNAME.github.io/REPOSITORY`

## Step 8: Configure Repository Settings

### General Settings

1. **Description**: Add a clear description of your book website
2. **Website**: Add your GitHub Pages URL once available
3. **Topics**: Add relevant tags like `book`, `website`, `celtic`, `medieval`, `fantasy`

### Branch Protection (Optional)

For collaborative projects:

1. Go to Settings → Branches
2. Add rule for `main` branch
3. Enable "Require pull request reviews"
4. Enable "Require status checks"

### Issues and Discussions

1. Enable Issues for bug reports and feature requests
2. Enable Discussions for community engagement
3. Create issue templates for consistent reporting

## Step 9: Collaboration Setup

### Adding Collaborators

1. Go to Settings → Manage access
2. Click "Invite a collaborator"
3. Enter GitHub username or email
4. Choose permission level:
   - **Read**: View repository
   - **Write**: Push changes
   - **Admin**: Full access

### Working with Forks

For external contributors:

1. They fork your repository
2. Make changes in their fork
3. Submit pull request to your repository
4. Review and merge changes

## Step 10: Workflow Best Practices

### Branching Strategy

```bash
# Create feature branch
git checkout -b feature/new-chapter-content

# Make changes and commit
git add .
git commit -m "Add Chapter 15 content and character updates"

# Push branch
git push origin feature/new-chapter-content

# Create pull request on GitHub
# Merge after review
```

### Commit Message Guidelines

Use clear, descriptive commit messages:

```
✅ Good examples:
- "Add character biography for Theron"
- "Update book cover image and optimize for web"
- "Fix responsive design issues on mobile"
- "Update chapter synopsis with latest revisions"

❌ Poor examples:
- "updates"
- "fix stuff"
- "changes"
```

### Regular Maintenance

```bash
# Keep your local repository updated
git pull origin main

# Clean up old branches
git branch -d feature/completed-feature

# Check repository status
git status
```

## Step 11: Advanced Features

### GitHub Actions (CI/CD)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Deploy to GitHub Pages
      uses: peaceiris/actions-gh-pages@v3
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: ./
```

### Issue Templates

Create `.github/ISSUE_TEMPLATE/bug_report.md`:

```markdown
---
name: Bug report
about: Create a report to help improve the website
---

**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior

**Expected behavior**
What you expected to happen

**Screenshots**
If applicable, add screenshots

**Device Information:**
- Browser: [e.g. Chrome, Safari]
- Version: [e.g. 22]
- Device: [e.g. iPhone, Desktop]
```

### Wiki Setup

1. Enable Wiki in repository settings
2. Create pages for:
   - Book lore and background
   - Character guides
   - Development notes
   - FAQ

## Step 12: Security and Backup

### Security Best Practices

1. **Never commit sensitive information**:
   - API keys
   - Database passwords
   - Personal information

2. **Use `.gitignore` properly**:
   ```gitignore
   # Sensitive files
   .env
   config.local.js
   
   # System files
   .DS_Store
   Thumbs.db
   
   # Editor files
   .vscode/
   .idea/
   ```

3. **Review pull requests carefully**
4. **Enable two-factor authentication**

### Backup Strategy

1. **Regular local backups**:
   ```bash
   git clone --mirror https://github.com/USERNAME/REPOSITORY.git
   ```

2. **Multiple remotes** (optional):
   ```bash
   git remote add backup https://gitlab.com/USERNAME/REPOSITORY.git
   git push backup main
   ```

## Troubleshooting Common Issues

### Authentication Problems

**HTTPS Authentication**:
```bash
git config --global credential.helper store
git push origin main
# Enter username and personal access token
```

**SSH Setup** (recommended):
```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your.email@example.com"

# Add to SSH agent
ssh-add ~/.ssh/id_ed25519

# Add public key to GitHub account
cat ~/.ssh/id_ed25519.pub
```

### Merge Conflicts

```bash
# When conflicts occur
git status
# Edit conflicted files
git add .
git commit -m "Resolve merge conflicts"
```

### Large File Issues

For large images or assets:

```bash
# Install Git LFS
git lfs install

# Track large files
git lfs track "*.jpg"
git lfs track "*.png"
git lfs track "*.pdf"

# Add and commit
git add .gitattributes
git commit -m "Add Git LFS tracking"
```

## Monitoring and Analytics

### Repository Insights

Monitor your repository's activity:

1. **Traffic**: View page views and clones
2. **Contributors**: See who's contributing
3. **Community**: Track issues and pull requests
4. **Dependency graph**: Monitor dependencies

### Notifications

Configure notifications for:

- Pull requests
- Issues
- Releases
- Security alerts

## Next Steps

After setting up GitHub:

1. ✅ Repository created and configured
2. ✅ Website files uploaded
3. ✅ GitHub Pages enabled
4. ✅ Collaborators added (if needed)
5. ⏳ Set up custom domain (optional)
6. ⏳ Configure analytics
7. ⏳ Plan content updates and maintenance

## Support Resources

- **GitHub Documentation**: [docs.github.com](https://docs.github.com)
- **Git Tutorial**: [git-scm.com/docs/gittutorial](https://git-scm.com/docs/gittutorial)
- **GitHub Learning Lab**: [lab.github.com](https://lab.github.com)
- **Pro Git Book**: [git-scm.com/book](https://git-scm.com/book)

---

Your GitHub repository is now ready for your book website! This setup provides a solid foundation for version control, collaboration, and automated deployment.