# 📋 VS CODE GITHUB QUICK REFERENCE

One-page cheat sheet for pushing to GitHub from VS Code.

---

## 🚀 FIRST TIME SETUP (Do Once)

### 1. Install & Configure Git
```bash
# Check if installed
git --version

# Configure (use your info!)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### 2. Sign in to GitHub in VS Code
- Open Source Control panel: `Ctrl+Shift+G`
- Click "Initialize Repository"
- Click "Sign in to GitHub" when prompted
- Authorize in browser

### 3. Create .gitignore (CRITICAL!)
Create file named `.gitignore` with:
```
.env
credentials.json
__pycache__/
*.pyc
venv/
.DS_Store
```

---

## 📤 PUSH TO GITHUB (First Time)

### Method A: Automatic (Easiest)
1. Source Control panel (`Ctrl+Shift+G`)
2. Stage all files (click "+" on "Changes")
3. Write commit message: "Initial commit"
4. Click "✓ Commit"
5. Click "Publish to GitHub"
6. Choose "Private" or "Public"
7. Done! ✅

### Method B: Manual
```bash
# In VS Code Terminal (Ctrl+`)
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/USERNAME/REPO.git
git branch -M main
git push -u origin main
```

---

## 🔄 DAILY WORKFLOW (After First Push)

### Visual Method (No Terminal)
```
1. Make changes to files
   ↓
2. Save files (Ctrl+S)
   ↓
3. Open Source Control (Ctrl+Shift+G)
   ↓
4. Stage changes (click "+")
   ↓
5. Write commit message
   ↓
6. Commit (click "✓")
   ↓
7. Push (click "Sync Changes" button)
```

### Terminal Method
```bash
git add .
git commit -m "Description of changes"
git push
```

---

## 🎮 KEYBOARD SHORTCUTS

| Action | Windows/Linux | Mac |
|--------|---------------|-----|
| Open Terminal | `` Ctrl+` `` | `` Cmd+` `` |
| Source Control | `Ctrl+Shift+G` | `Cmd+Shift+G` |
| Save File | `Ctrl+S` | `Cmd+S` |
| Save All | `Ctrl+K S` | `Cmd+K S` |
| Commit | `Ctrl+Enter` | `Cmd+Enter` |

---

## 📍 VS CODE INTERFACE GUIDE

```
┌────────────────────────────────────────────────────┐
│  File  Edit  Selection  View  ...                 │ ← Menu Bar
├────┬───────────────────────────────────────────────┤
│ 📁 │ EXPLORER                                      │
│ 🔍 │   shopping_list_app/                         │ ← Your Files
│ ⑂  │   ├── app.py                                 │
│ 🐛 │   ├── templates/                             │
│ 📦 │   ├── .gitignore                             │
│    │   └── README.md                               │
├────┼───────────────────────────────────────────────┤
│    │ SOURCE CONTROL: GIT                           │ ← Click ⑂ icon
│    │                                                │
│    │ Message (Ctrl+Enter to commit)                │ ← Type message
│    │ [____________________________]                │
│    │                                                │
│    │ [✓ Commit]  [... More Actions]                │ ← Commit button
│    │                                                │
│    │ CHANGES (3)                     [+]           │ ← Stage all
│    │   M app.py                    [+]             │ ← Stage one
│    │   M README.md                 [+]             │
│    │   A new_file.py               [+]             │
│    │                                                │
│    │ STAGED CHANGES (0)                            │
└────┴───────────────────────────────────────────────┘
         Bottom: [🔄 Sync Changes] ← Push/Pull
```

---

## 🔤 FILE STATUS ICONS

In Source Control panel:

| Icon | Meaning | Action |
|------|---------|--------|
| `U` | Untracked (new file) | Stage to add to Git |
| `M` | Modified (changed) | Stage to include changes |
| `A` | Added (staged new file) | Ready to commit |
| `D` | Deleted | File removed |
| `C` | Conflict | Need to resolve |

---

## ✅ CHECKLIST BEFORE PUSHING

```
BEFORE clicking "Commit" or "Push":

□ Check Source Control panel
□ Make sure .env is NOT listed
□ Make sure credentials.json is NOT listed  
□ .gitignore file exists
□ All wanted files are staged
□ Commit message is clear
□ Ready to push!
```

---

## 🆘 COMMON ISSUES & FIXES

### "Git not found"
```bash
# Install Git, then in VS Code:
Ctrl+Shift+P → "Reload Window"
```

### "Authentication failed"
Create Personal Access Token:
1. GitHub.com → Settings → Developer settings → Tokens
2. Generate new token (classic)
3. Check "repo" scope
4. Use token as password

### "Can't push - rejected"
```bash
git pull origin main
# Resolve any conflicts
git push
```

### "Staged changes disappeared"
They're committed! Check:
- Click "..." menu in Source Control
- Select "View History" or "Show Git Graph"

### Files not staging
```bash
# In Terminal:
git status
# Shows what's wrong
```

---

## 💡 PRO TIPS

### Tip 1: GitLens Extension
Install for better Git integration:
- `Ctrl+Shift+X` → Search "GitLens" → Install

### Tip 2: Commit Messages
Good: `Fix WhatsApp formatting bug`
Bad: `changes` or `update`

### Tip 3: Check Changes Before Committing
- Click on a file in Source Control
- See what changed (green = added, red = removed)

### Tip 4: Undo Last Commit (Not Pushed Yet)
```bash
git reset --soft HEAD~1
```

### Tip 5: See All Commits
```bash
git log --oneline
# Press 'q' to exit
```

---

## 🔐 SECURITY REMINDER

### NEVER COMMIT THESE:
- ❌ `.env` files
- ❌ `credentials.json`
- ❌ API keys
- ❌ Passwords
- ❌ Private keys

### ALWAYS HAVE IN .gitignore:
```
.env
credentials.json
*.key
secrets/
```

### IF YOU ACCIDENTALLY PUSHED SECRETS:
```bash
git rm --cached .env credentials.json
git commit -m "Remove sensitive files"
git push

# Then: ROTATE ALL CREDENTIALS!
```

---

## 📚 USEFUL GIT COMMANDS

```bash
# See what changed
git status

# See commit history
git log --oneline

# Discard changes to a file
git checkout -- filename

# Undo last commit (keep changes)
git reset --soft HEAD~1

# See remote URL
git remote -v

# Pull latest from GitHub
git pull

# Push to GitHub
git push

# Create new branch
git checkout -b feature-name

# Switch branches
git checkout main
```

---

## 🎯 WORKFLOW SUMMARY

### First Time:
```
Install Git → Configure → Sign in GitHub → 
Initialize Repo → Create .gitignore → 
Stage All → Commit → Publish to GitHub ✅
```

### Every Update:
```
Make changes → Save → Stage → Commit → Sync ✅
```

---

## 📱 QUICK TROUBLESHOOTING

| Problem | Solution |
|---------|----------|
| Can't see Source Control | Press `Ctrl+Shift+G` |
| Git not installed | Download from git-scm.com |
| Can't sign in | Use Personal Access Token |
| Changes not showing | Click refresh icon in Source Control |
| Can't push | Run `git pull` first |
| Wrong credentials | Create new Personal Access Token |

---

## 🎓 LEARNING PATH

1. **Day 1:** Push your first commit
2. **Day 2:** Make a change and push update
3. **Day 3:** Explore commit history
4. **Week 1:** Get comfortable with daily workflow
5. **Week 2:** Learn branches for features

---

## 🔗 HELPFUL LINKS

- Full Guide: `GITHUB_VSCODE_GUIDE.md`
- VS Code Git: [code.visualstudio.com/docs/sourcecontrol/overview](https://code.visualstudio.com/docs/sourcecontrol/overview)
- GitHub Docs: [docs.github.com](https://docs.github.com)
- Git Cheat Sheet: [education.github.com/git-cheat-sheet-education.pdf](https://education.github.com/git-cheat-sheet-education.pdf)

---

## ✨ YOU'VE GOT THIS!

Keep this reference handy while learning.
After a few pushes, it becomes second nature! 🚀

---

*Print this page and keep it next to your computer!*
*Or bookmark GITHUB_VSCODE_GUIDE.md for the full tutorial.*
