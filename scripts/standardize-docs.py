#!/usr/bin/env python3
"""
Standardize documentation files with versioning and formatting.
"""

import os
import re
from pathlib import Path

def fix_headings(content, is_first_file=False):
    """Fix heading hierarchy - H1 in first file, H2 in subsequent."""
    lines = content.split('\n')
    result = []
    
    for line in lines:
        # Convert H1 to H2 if not first file
        if not is_first_file and line.startswith('# '):
            line = '## ' + line[2:]
        result.append(line)
    
    return '\n'.join(result)

def ensure_code_blocks_have_language(content):
    """Ensure all code blocks have language identifiers."""
    # Pattern: ``` followed by optional language, then newline
    pattern = r'```(\w+)?\n'
    
    def replace_code_block(match):
        lang = match.group(1)
        if lang:
            return match.group(0)
        return '```text\n'  # Default to text if no language
    
    content = re.sub(pattern, replace_code_block, content)
    
    # Also handle code blocks with no newline after ```
    pattern2 = r'```\n(?!\w)'
    content = re.sub(pattern2, '```text\n', content)
    
    return content

def fix_spacing(content):
    """Ensure proper spacing between sections."""
    # Remove multiple consecutive blank lines
    content = re.sub(r'\n{3,}', '\n\n', content)
    return content

def process_file(source_path, dest_path, is_first_file=False):
    """Process a single markdown file."""
    with open(source_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Apply transformations
    content = fix_headings(content, is_first_file)
    content = ensure_code_blocks_have_language(content)
    content = fix_spacing(content)
    
    # Write to destination
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    with open(dest_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Processed: {os.path.basename(source_path)} → {os.path.basename(dest_path)}")

def add_frontmatter(content, title, subtitle, doc_type):
    """Add frontmatter to content."""
    frontmatter = f'''---
title: "{title}"
subtitle: "{subtitle}"
author: "Alpine Analytics LLC"
date: "2025-11-12"
version: "1.0"
documentType: "{doc_type}"
toc: true
toc-depth: 3
linkcolor: "#0066CC"
urlcolor: "#0066CC"
geometry: "a4paper"
margin: "2cm"
fontsize: "12pt"
linestretch: 1.5
mainfont: "Georgia"
sansfont: "DejaVu Sans"
monofont: "DejaVu Sans Mono"
papersize: "a4"
---

'''
    return frontmatter + content

def process_file_with_frontmatter(source_path, dest_path, is_first_file, title, subtitle, doc_type):
    """Process file and add frontmatter if first file."""
    with open(source_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Apply transformations
    content = fix_headings(content, is_first_file)
    content = ensure_code_blocks_have_language(content)
    content = fix_spacing(content)
    
    # Add frontmatter to first file
    if is_first_file:
        content = add_frontmatter(content, title, subtitle, doc_type)
    
    # Write to destination
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    with open(dest_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Processed: {os.path.basename(source_path)} → {os.path.basename(dest_path)}")

def main():
    base_dir = Path(__file__).parent.parent
    docs_dir = base_dir / 'docs'
    root_dir = base_dir
    
    # InvestorDocs mapping
    investor_mapping = [
        ('executive-summary.md', 'v1.0_01_executive_summary.md', True, 
         'Alpine Analytics - Investor Documentation', 'Executive Summary & Investment Opportunity', 'Investor Documentation'),
        ('business-model.md', 'v1.0_02_business_model.md', False, None, None, None),
        ('competitive-advantage.md', 'v1.0_03_competitive_advantage.md', False, None, None, None),
        ('intellectual-property.md', 'v1.0_04_intellectual_property.md', False, None, None, None),
        ('financial-projections.md', 'v1.0_05_financial_projections.md', False, None, None, None),
        ('team-and-operations.md', 'v1.0_06_team_and_operations.md', False, None, None, None),
        ('acquisition-readiness.md', 'v1.0_07_acquisition_readiness.md', False, None, None, None),
    ]
    
    # TechnicalDocs mapping
    technical_mapping = [
        ('technical-overview.md', 'v1.0_01_technical_overview.md', True,
         'Alpine Analytics - Technical Documentation', 'System Architecture & Technology', 'Technical Documentation'),
        ('SYSTEM_AUDIT_REPORT.md', 'v1.0_02_system_audit_report.md', False, None, None, None),
        ('OPTIMIZATION_SUMMARY.md', 'v1.0_03_optimization_summary.md', False, None, None, None),
        ('OPTIMIZATION_IMPLEMENTATION.md', 'v1.0_04_optimization_implementation.md', False, None, None, None),
        ('DEPLOYMENT_GUIDE.md', 'v1.0_05_deployment_guide.md', False, None, None, None),
        ('DEPLOYMENT_COMPLETE.md', 'v1.0_06_deployment_complete.md', False, None, None, None),
    ]
    
    # SystemDocs mapping
    system_mapping = [
        ('README.md', 'v1.0_01_readme.md', True,
         'Argo → Alpine Monorepo', 'Intelligent Trading Signal Platform', 'System Documentation'),
        ('MONOREPO_SETUP.md', 'v1.0_02_monorepo_setup.md', False, None, None, None),
        ('API_ENDPOINTS_SUMMARY.md', 'v1.0_03_api_endpoints_summary.md', False, None, None, None),
        ('DEPLOYMENT_SUCCESS.md', 'v1.0_04_deployment_success.md', False, None, None, None),
    ]
    
    investor_docs_dir = docs_dir / 'InvestorDocs'
    technical_docs_dir = docs_dir / 'TechnicalDocs'
    system_docs_dir = docs_dir / 'SystemDocs'
    
    print("📝 Processing InvestorDocs...")
    for source, dest, is_first, title, subtitle, doc_type in investor_mapping:
        source_path = docs_dir / source
        dest_path = investor_docs_dir / dest
        if source_path.exists():
            if is_first:
                process_file_with_frontmatter(source_path, dest_path, is_first, title, subtitle, doc_type)
            else:
                process_file(source_path, dest_path, is_first)
        else:
            print(f"⚠️  Not found: {source_path}")
    
    print("\n📝 Processing TechnicalDocs...")
    for source, dest, is_first, title, subtitle, doc_type in technical_mapping:
        source_path = docs_dir / source
        dest_path = technical_docs_dir / dest
        if source_path.exists():
            if is_first:
                process_file_with_frontmatter(source_path, dest_path, is_first, title, subtitle, doc_type)
            else:
                process_file(source_path, dest_path, is_first)
        else:
            print(f"⚠️  Not found: {source_path}")
    
    print("\n📝 Processing SystemDocs...")
    for source, dest, is_first, title, subtitle, doc_type in system_mapping:
        source_path = root_dir / source if source == 'README.md' else root_dir / source
        dest_path = system_docs_dir / dest
        if source_path.exists():
            if is_first:
                process_file_with_frontmatter(source_path, dest_path, is_first, title, subtitle, doc_type)
            else:
                process_file(source_path, dest_path, is_first)
        else:
            print(f"⚠️  Not found: {source_path}")
    
    print("\n✅ Standardization complete!")

if __name__ == '__main__':
    main()

