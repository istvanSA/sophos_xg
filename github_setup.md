# GitHub and HACS Setup Guide

Follow these steps to upload your integration to GitHub and share it on HACS.

## 1. Create a Repository on GitHub
1. Log in to your GitHub account (istvanSA).
2. Create a new **public** repository named `sophos_xg`.
3. Do **not** initialize it with a README, license, or gitignore (we already have them!).

## 2. Push Your Code
Open a terminal in your project directory (`g:\gravities\Sophos XG`) and run:

```bash
# Initialize git
git init

# Add all files
git add .

# Initial commit
git commit -m "Initial commit - Sophos XG Firewall integration"

# Connect to your GitHub repo
git remote add origin https://github.com/istvanSA/sophos_xg.git

# Set your branch name
git branch -M main

# Push the code
git push -u origin main
```

## 3. Create a GitHub Release (for HACS versioning)
HACS uses GitHub Releases to track versions.
1. On your GitHub repo page, click **Releases** on the right sidebar.
2. Click **Create a new release**.
3. Set the tag version to `v1.0.0`.
4. Give it a title: `Release v1.0.0`.
5. Click **Publish release**.

## 4. Test in HACS
To see it in your own Home Assistant:
1. Go to **HACS** > **Integrations**.
2. Click the three dots in the corner > **Custom repositories**.
3. Repository: `https://github.com/istvanSA/sophos_xg`.
4. Category: `Integration`.
5. Click **Add**.
6. It should now appear in the list for you to download and install!

## 5. Share with the Community
If you want it to appear for *everyone* by default in HACS, you can eventually submit it to the [HACS Default Repositories](https://hacs.xyz/docs/publish/include/).

Enjoy your new integration!
