#!/usr/bin/env python3
"""
Automated documentation updater for Stock Forecaster.
This script analyzes the codebase and updates documentation automatically.
"""

import os
import sys
import json
import re
from datetime import datetime
from pathlib import Path

def get_project_stats():
    """Analyze codebase to extract current stats."""
    stats = {
        'files_count': 0,
        'functions_count': 0,
        'classes_count': 0,
        'lines_of_code': 0,
        'features': [],
        'last_modified': datetime.now().isoformat()
    }
    
    # Analyze core files
    core_dir = Path('../core')
    ui_dir = Path('../ui')
    
    for directory in [core_dir, ui_dir]:
        if directory.exists():
            for file_path in directory.glob('*.py'):
                stats['files_count'] += 1
                with open(file_path, 'r') as f:
                    content = f.read()
                    stats['lines_of_code'] += len(content.splitlines())
                    stats['functions_count'] += len(re.findall(r'^def ', content, re.MULTILINE))
                    stats['classes_count'] += len(re.findall(r'^class ', content, re.MULTILINE))
    
    return stats

def detect_new_features():
    """Scan code for new features or capabilities."""
    features = []
    
    # Check for rating types
    models_file = Path('../core/models.py')
    if models_file.exists():
        with open(models_file, 'r') as f:
            content = f.read()
            if 'RISKY_BUY' in content:
                features.append('RISKY_BUY rating system')
            if 'MOMENTUM_BUY' in content:
                features.append('Momentum-based ratings')
    
    # Check for European support
    data_fetcher = Path('../core/data_fetcher.py')
    if data_fetcher.exists():
        with open(data_fetcher, 'r') as f:
            content = f.read()
            if '.DE' in content and '.AS' in content:
                features.append('European market support')
            if 'rheinmetall' in content.lower():
                features.append('Company name translation')
    
    # Check for UI enhancements
    app_js = Path('../ui/app.js')
    if app_js.exists():
        with open(app_js, 'r') as f:
            content = f.read()
            if 'scrollIntoView' in content:
                features.append('Smooth scrolling UI')
            if 'classList.add(\'active\')' in content:
                features.append('Interactive stock selection')
    
    return features

def update_claude_md():
    """Update CLAUDE.md with current project state."""
    stats = get_project_stats()
    features = detect_new_features()
    
    # Read current CLAUDE.md
    claude_md_path = Path('../CLAUDE.md')
    if claude_md_path.exists():
        with open(claude_md_path, 'r') as f:
            content = f.read()
    else:
        content = ""
    
    # Generate status update
    status_update = f"""
# AUTO-UPDATED STATUS ({datetime.now().strftime('%Y-%m-%d %H:%M')})

## 📊 Current Codebase Stats
- **Files**: {stats['files_count']} Python files
- **Functions**: {stats['functions_count']} total functions
- **Classes**: {stats['classes_count']} data classes
- **Lines of Code**: {stats['lines_of_code']} total LOC

## 🚀 Active Features Detected
""" + '\n'.join(f"- ✅ {feature}" for feature in features) + f"""

## 🔄 Last Auto-Update
- **Timestamp**: {stats['last_modified']}
- **Scan Result**: {len(features)} features detected

---
"""
    
    # Update or append to CLAUDE.md
    if '# AUTO-UPDATED STATUS' in content:
        # Replace existing auto-update section
        start_marker = '# AUTO-UPDATED STATUS'
        end_marker = '\n---\n'
        start_idx = content.find(start_marker)
        end_idx = content.find(end_marker, start_idx) + len(end_marker)
        
        if start_idx != -1 and end_idx != -1:
            content = content[:start_idx] + status_update + content[end_idx:]
        else:
            content += status_update
    else:
        # Append new section
        content += status_update
    
    # Write back to file
    with open(claude_md_path, 'w') as f:
        f.write(content)
    
    return stats, features

def update_changelog():
    """Add entry to CHANGELOG.md if significant changes detected."""
    changelog_path = Path('../CHANGELOG.md')
    
    # For now, just timestamp the last check
    timestamp_entry = f"""
## [Auto-Check] - {datetime.now().strftime('%Y-%m-%d %H:%M')}
- Documentation auto-updated
- Codebase scanned for changes
"""
    
    if changelog_path.exists():
        with open(changelog_path, 'r') as f:
            content = f.read()
        
        # Insert after first heading
        lines = content.split('\n')
        insert_idx = 2  # After "# Stock Forecaster Changelog"
        lines.insert(insert_idx, timestamp_entry)
        
        with open(changelog_path, 'w') as f:
            f.write('\n'.join(lines))

def main():
    """Main documentation update routine."""
    print("🔄 Updating Stock Forecaster documentation...")
    
    try:
        stats, features = update_claude_md()
        update_changelog()
        
        print(f"✅ Documentation updated successfully!")
        print(f"📊 Found {len(features)} features in {stats['files_count']} files")
        print(f"🕒 Timestamp: {stats['last_modified']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating documentation: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)