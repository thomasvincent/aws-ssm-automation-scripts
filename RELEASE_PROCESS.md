# Release Process

This document outlines the release process for the AWS SSM Automation Scripts repository.

## Overview

The repository uses semantic versioning (SemVer) for releases and GitHub Packages for distribution. The release process is automated using GitHub Actions.

## Making a Release

### 1. Via GitHub Actions (Recommended)

1. Go to the GitHub repository page
2. Click on the "Actions" tab
3. Select the "Create Release" workflow
4. Click "Run workflow"
5. Select the version increment type:
   - `patch`: For bug fixes and minor changes (1.0.0 → 1.0.1)
   - `minor`: For new features (1.0.0 → 1.1.0)
   - `major`: For breaking changes (1.0.0 → 2.0.0)
6. Click "Run workflow" to start the release process

The workflow will:
- Bump the version in package.json
- Create a git tag for the new version
- Generate a changelog of changes since the last release
- Create a GitHub Release with release notes
- Create a distribution package (.zip) with all SSM documents
- Attach the package to the release
- Publish the package to GitHub Packages

### 2. Manual Releases (Advanced Users)

For manual releases, follow these steps:

```bash
# 1. Bump the version
npm run version-bump [patch|minor|major]

# 2. Create the package
npm run package

# 3. Create a release on GitHub (via web interface)
# Upload the zip file from the dist/ directory
```

## Installing from GitHub Packages

To install the package from GitHub Packages:

```bash
# Configure npm to use GitHub Packages (first time only)
echo "@thomasvincent:registry=https://npm.pkg.github.com" >> .npmrc

# Install the package
npm install @thomasvincent/aws-ssm-automation-scripts
```

## Package Structure

The release package contains:
- All SSM automation documents (*.yaml)
- Shared Python modules (shared/python/*.py)
- Documentation (README.md)
- License information (LICENSE)
- Manifest file with version information (MANIFEST.json)

## Versioning Guidelines

When deciding which version increment to use:

- **patch**: Bug fixes, documentation updates, or minor changes that don't affect functionality
- **minor**: New features or enhancements that are backward compatible
- **major**: Breaking changes that are not backward compatible

## Troubleshooting

If you encounter issues with the automated release process:

1. Check the GitHub Actions logs for errors
2. Verify that you have the necessary permissions
3. Ensure branch protection rules don't prevent the workflow from running

For permission issues, contact the repository owner.
