# 🚀 Creating Your GitHub Repository

## Step-by-Step Guide

Your local Git repository is ready! Now follow these steps to create the GitHub repository:

### 1. Create GitHub Repository

1. **Go to GitHub.com** and sign in to your account
   - If you don't have an account, create one at github.com

2. **Click the "+" icon** in the top right corner and select "New repository"

3. **Fill in repository details:**
   - **Repository name:** `stone-sceptre-website`
   - **Description:** `Epic website for "The Stone and the Sceptre: A Scribe's Tale" - A chronicle of divine providence and royal destiny`
   - **Visibility:** Choose "Public" (recommended for GitHub Pages)
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)

4. **Click "Create repository"**

### 2. Connect Your Local Repository

Here are the exact commands to run in your terminal:

```bash
git remote add origin https://github.com/reversesingularity/stone-sceptre-website.git
git branch -M main
git push -u origin main
```

### 3. Enable GitHub Pages

1. In your GitHub repository, go to **Settings**
2. Scroll down to **Pages** section
3. Under "Source", select **Deploy from a branch**
4. Choose **main** branch and **/ (root)** folder
5. Click **Save**

Your website will be available at:
`https://reversesingularity.github.io/stone-sceptre-website`

### 4. Connect Your Domain

Once GitHub Pages is active:

1. **In GitHub Pages settings**, add your custom domain
2. **In Squarespace domain settings:**
   - Add CNAME record: `www` pointing to `reversesingularity.github.io`
   - Add A records pointing to GitHub Pages IPs:
     - 185.199.108.153
     - 185.199.109.153
     - 185.199.110.153
     - 185.199.111.153

### 5. Commands Ready to Run

Here are the exact commands you need to run in your terminal:

```bash
# Add your GitHub repository as origin
git remote add origin https://github.com/reversesingularity/stone-sceptre-website.git

# Rename main branch and push
git branch -M main
git push -u origin main
```

## 🎉 What's Included

Your repository contains:
- ✅ Complete website files
- ✅ Professional README.md
- ✅ Deployment instructions
- ✅ .gitignore file
- ✅ Deployment zip package
- ✅ All images and assets

## 📞 Need Help?

If you encounter any issues:
1. Check that your GitHub username is correct in the commands
2. Make sure you're signed in to GitHub
3. Verify your internet connection
4. Try refreshing the GitHub page

Your website is ready to go live! 🚀
