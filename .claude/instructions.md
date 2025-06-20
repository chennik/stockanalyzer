# Claude Documentation Maintenance Instructions

## 🤖 Auto-Documentation Protocol

When making changes to the Stock Forecaster codebase, Claude should ALWAYS:

### 1. Before Major Changes
- [ ] Read current `CLAUDE.md` to understand existing state
- [ ] Note which files will be modified
- [ ] Plan documentation updates needed

### 2. After Making Changes  
- [ ] Update `CLAUDE.md` with new features/changes
- [ ] Add entry to `CHANGELOG.md` with timestamp
- [ ] Update version number if applicable
- [ ] Run documentation update script if available

### 3. Specific Update Triggers

**Always update docs when:**
- Adding new rating types (BUY, RISKY_BUY, etc.)
- Modifying core algorithms in `analyzer.py`
- Adding new market support (countries, exchanges)
- Changing UI/UX significantly
- Adding new API endpoints
- Fixing major bugs

**Update format:**
```markdown
## [Version] - YYYY-MM-DD - Description

### 🚀 New Features
- Feature description with file references

### 🔧 Technical Changes  
- Algorithm improvements
- Performance optimizations

### 🐛 Bug Fixes
- Issue fixed with code location
```

### 4. Documentation Standards

**CLAUDE.md Structure:**
- Keep "CURRENT STATE" section updated
- Maintain file references with line numbers
- Update performance metrics
- List known issues/fixes

**CHANGELOG.md:**
- Use semantic versioning
- Include file locations for changes
- Explain WHY changes were made
- Reference specific functions modified

**Function Documentation:**
```python
def new_function():
    """
    Brief description.
    
    WHY: Explain the trading/business reason
    WHEN: Describe when this triggers
    EXAMPLE: Show sample usage
    """
```

### 5. Context Preservation Commands

**For Claude to run:**
```python
# Update documentation programmatically
python scripts/update_docs.py

# Check current state
grep -n "def.*trading" core/*.py
grep -n "class.*Rating" core/*.py
```

### 6. Version Bump Protocol

**Minor changes (1.0.1):**
- Bug fixes, small improvements
- UI tweaks, performance optimizations

**Major changes (1.1.0):** 
- New features, algorithm changes
- New markets, rating types

**Breaking changes (2.0.0):**
- API changes, major restructures
- Complete algorithm rewrites

### 7. Emergency Recovery

**If context is lost:**
1. Read `CLAUDE.md` current state section
2. Check `CHANGELOG.md` for recent changes  
3. Review `QUICK_REFERENCE.md` for key functions
4. Run `python scripts/update_docs.py` to refresh

### 8. Quality Checklist

Before finishing any session:
- [ ] All new features documented
- [ ] Performance impacts noted
- [ ] File locations with line numbers provided
- [ ] WHY explanations included for trading logic
- [ ] Version updated if warranted

## 🎯 Goal

Ensure any future Claude session can:
1. Understand current system capabilities
2. Know where key logic is implemented  
3. Maintain trading algorithm quality
4. Continue development seamlessly