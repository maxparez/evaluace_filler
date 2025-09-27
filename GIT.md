# Git Workflow & Branch Management - Evaluace Filler

## 📋 Branch Strategy

### Main Branches
- **`main`** - Primary development branch with complete codebase
  - Contains all development files, tests, documentation
  - Linux and Windows compatible
  - Full feature set including dev tools

- **`windows-installer`** - Clean Windows installation package
  - Only essential files for Windows users
  - Streamlined for end-user installation
  - No dev/test files, no Linux-specific code

## 🔄 Workflow Rules

### 1. Development Process
```bash
# Always work on main branch for development
git checkout main
git pull origin main

# Create feature branches from main for new features
git checkout -b feature/new-feature-name
# Work on feature...
git add .
git commit -m "[feat-XXX] description"
git push -u origin feature/new-feature-name

# Merge back to main via PR or direct merge
git checkout main
git merge feature/new-feature-name
git push origin main
```

### 2. Windows Installer Updates
```bash
# After significant changes to main, update windows-installer
git checkout windows-installer

# Cherry-pick specific commits or copy essential files
git checkout main -- file1 file2 file3

# Commit changes
git add .
git commit -m "[sync-installer] Update Windows package with latest changes"
git push origin windows-installer
```

### 3. Hotfixes for Both Branches
```bash
# Fix critical issues in main first
git checkout main
# Fix the issue...
git add .
git commit -m "[fix-critical] description"
git push origin main

# Apply same fix to windows-installer
git checkout windows-installer
# Apply same fix...
git add .
git commit -m "[fix-critical] description"
git push origin windows-installer
```

## 📝 Commit Message Standards

### Format
```
[tag-XXX] brief description (max 50 chars)

Detailed explanation if needed (wrap at 72 chars)
```

### Tags
- **`[feat-XXX]`** - New features
- **`[fix-XXX]`** - Bug fixes
- **`[refactor-XXX]`** - Code refactoring
- **`[test-XXX]`** - Tests
- **`[docs-XXX]`** - Documentation
- **`[config-XXX]`** - Configuration changes
- **`[cleanup-XXX]`** - Code cleanup
- **`[sync-installer]`** - Windows installer updates

### Examples
```bash
git commit -m "[feat-001] Add matrix random rating strategy

- Implement MATRIX_RANDOM_RATING in strategies
- Add A5/A6/A7 random selection logic
- Update configuration options for random_matrix"

git commit -m "[fix-windows] Fix import error for config module"

git commit -m "[sync-installer] Update Windows package with latest bug fixes"
```

## 🚀 Release Process

### 1. Main Branch Release
```bash
# Ensure all tests pass and code is stable
npm run test  # or python -m pytest
git add .
git commit -m "[release-vX.X] Prepare release version X.X"
git tag -a vX.X -m "Release version X.X"
git push origin main --tags
```

### 2. Windows Installer Update
```bash
# After main release, update installer branch
git checkout windows-installer
git checkout main -- batch_processor.py src/ scenarios/ config/
git add .
git commit -m "[sync-installer] Update to version X.X

- Sync with main branch vX.X
- Include latest bug fixes and features
- Maintain clean Windows package structure"
git push origin windows-installer
```

## 🛡️ Protection Rules

### Main Branch
- ✅ Direct commits allowed (trusted development)
- ✅ Force push allowed (for emergency fixes)
- ⚠️ Always pull before pushing
- 📋 Mandatory: Update documentation for major changes

### Windows-Installer Branch
- ✅ Manual sync from main branch
- ❌ No direct development work
- ✅ Only essential files
- 📋 Regular sync with main for critical fixes

## 📂 File Management

### Files in Main Only
```
# Development files
test_*.py
quick_*.py
demo_*.py
*_debug.py
run_survey_mapper.sh

# Development documentation
PROGRESS.md
CONTEXT.md
VISUAL_STATUS_README.md

# Build artifacts
__pycache__/
*.log
results/
logs/
temp/
venv/
```

### Files in Both Branches
```
# Core application
batch_processor.py
src/
scenarios/
config/
requirements.txt

# Windows setup
*.bat files
README_WINDOWS.md
.env.example
.gitignore
```

### Windows-Installer Specific
```
# Clean README focused on installation
README.md (different from main)
```

## 🔧 Branch Maintenance

### Regular Tasks
```bash
# Weekly: Sync windows-installer with main
git checkout windows-installer
git checkout main -- batch_processor.py src/ config/
git add .
git commit -m "[sync-installer] Weekly sync with main branch"
git push origin windows-installer

# Monthly: Clean up old feature branches
git branch -d feature/old-branch-name
git push origin --delete feature/old-branch-name
```

### Emergency Procedures
```bash
# Critical bug affects both branches
# Fix in main first
git checkout main
# Apply fix...
git add .
git commit -m "[fix-critical] description"
git push origin main

# Immediately apply to windows-installer
git checkout windows-installer
# Apply same fix...
git add .
git commit -m "[fix-critical] description"
git push origin windows-installer
```

## 📊 Quality Standards

### Before Committing
- [ ] Code works on target platform
- [ ] No hardcoded paths or secrets
- [ ] Proper error handling
- [ ] Documentation updated if needed
- [ ] Commit message follows standards

### Before Syncing Windows-Installer
- [ ] Main branch is stable
- [ ] All critical fixes included
- [ ] No dev files accidentally included
- [ ] Windows compatibility verified
- [ ] Installation tested

## 🎯 Best Practices

1. **Commit Frequently** - Every 1-2 hours or after completing a feature
2. **Push Daily** - Minimum 2x per day, always before breaks
3. **Descriptive Messages** - Clear, actionable commit messages
4. **Test Before Push** - Verify functionality before pushing
5. **Document Changes** - Update relevant documentation
6. **Clean History** - Use meaningful commits, avoid "WIP" commits in main

## 🆘 Troubleshooting

### Common Issues
```bash
# Merge conflicts
git status
git diff
# Resolve conflicts manually
git add .
git commit -m "[fix-merge] Resolve merge conflicts"

# Accidentally committed to wrong branch
git cherry-pick <commit-hash>
git checkout correct-branch
git cherry-pick <commit-hash>

# Need to undo last commit
git reset --soft HEAD~1  # Keep changes
git reset --hard HEAD~1  # Discard changes
```

### Recovery Procedures
```bash
# Restore deleted files
git checkout HEAD -- filename

# Recover lost commits
git reflog
git checkout <commit-hash>

# Reset branch to specific state
git reset --hard origin/main
```

---

**Last Updated**: 2025-09-27
**Maintained By**: Max Parez (max.parez@seznam.cz)