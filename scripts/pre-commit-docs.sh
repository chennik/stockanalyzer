#!/bin/bash
# Pre-commit hook to update documentation

echo "🔄 Checking if documentation needs updates..."

# Check if core files were modified
CORE_MODIFIED=$(git diff --cached --name-only | grep -E "(core/|ui/)" | wc -l)

if [ $CORE_MODIFIED -gt 0 ]; then
    echo "📝 Core files modified, updating documentation..."
    
    # Run documentation updater
    cd scripts
    python update_docs.py
    
    # Add updated docs to commit
    git add ../CLAUDE.md ../CHANGELOG.md
    
    echo "✅ Documentation updated and staged"
else
    echo "ℹ️  No core changes detected, skipping doc update"
fi

exit 0