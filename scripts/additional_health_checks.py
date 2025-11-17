#!/usr/bin/env python3
"""
Additional Health Checks
Performs extended health checks including tests, documentation, and code quality
"""
import sys
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List

def check_test_files(workspace_root: Path) -> Dict:
    """Check for test files and test coverage"""
    results = {
        "test_files_found": 0,
        "test_directories": [],
        "test_types": {
            "unit": 0,
            "integration": 0,
            "e2e": 0,
            "security": 0
        }
    }
    
    # Find test files
    test_patterns = [
        "**/test_*.py",
        "**/*_test.py",
        "**/tests/**/*.py",
        "**/__tests__/**/*.ts",
        "**/__tests__/**/*.tsx",
        "**/*.test.ts",
        "**/*.test.tsx",
        "**/*.spec.ts",
        "**/*.spec.tsx"
    ]
    
    for pattern in test_patterns:
        for test_file in workspace_root.glob(pattern):
            if "node_modules" not in str(test_file) and ".venv" not in str(test_file):
                results["test_files_found"] += 1
                
                # Categorize tests
                path_str = str(test_file)
                if "unit" in path_str.lower():
                    results["test_types"]["unit"] += 1
                if "integration" in path_str.lower():
                    results["test_types"]["integration"] += 1
                if "e2e" in path_str.lower() or "end_to_end" in path_str.lower():
                    results["test_types"]["e2e"] += 1
                if "security" in path_str.lower():
                    results["test_types"]["security"] += 1
                
                # Track test directories
                test_dir = test_file.parent
                if test_dir not in results["test_directories"]:
                    results["test_directories"].append(str(test_dir.relative_to(workspace_root)))
    
    return results

def check_documentation(workspace_root: Path) -> Dict:
    """Check for documentation files"""
    results = {
        "readme_files": [],
        "doc_files": [],
        "api_docs": []
    }
    
    # Find README files
    for readme in workspace_root.glob("**/README*.md"):
        if "node_modules" not in str(readme):
            results["readme_files"].append(str(readme.relative_to(workspace_root)))
    
    # Find documentation files
    for doc in workspace_root.glob("docs/**/*.md"):
        results["doc_files"].append(str(doc.relative_to(workspace_root)))
    
    # Find API documentation
    for api_doc in workspace_root.glob("**/*API*.md"):
        if "node_modules" not in str(api_doc):
            results["api_docs"].append(str(api_doc.relative_to(workspace_root)))
    
    return results

def check_code_quality(workspace_root: Path) -> Dict:
    """Check code quality metrics"""
    results = {
        "python_files": 0,
        "typescript_files": 0,
        "total_lines": 0,
        "has_linting_config": False,
        "has_formatting_config": False
    }
    
    # Count files
    for py_file in workspace_root.glob("**/*.py"):
        if "node_modules" not in str(py_file) and ".venv" not in str(py_file) and "venv" not in str(py_file):
            results["python_files"] += 1
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    results["total_lines"] += len(f.readlines())
            except:
                pass
    
    for ts_file in workspace_root.glob("**/*.{ts,tsx}"):
        if "node_modules" not in str(ts_file):
            results["typescript_files"] += 1
            try:
                with open(ts_file, 'r', encoding='utf-8') as f:
                    results["total_lines"] += len(f.readlines())
            except:
                pass
    
    # Check for config files
    config_files = [
        ".eslintrc",
        ".eslintrc.js",
        ".eslintrc.json",
        "eslint.config.js",
        ".prettierrc",
        ".prettierrc.js",
        ".prettierrc.json",
        "prettier.config.js",
        "pyproject.toml",
        "setup.cfg",
        ".flake8",
        "pytest.ini"
    ]
    
    for config in config_files:
        if (workspace_root / config).exists():
            if "eslint" in config or "prettier" in config:
                results["has_formatting_config"] = True
            if "flake8" in config or "pytest" in config or "pyproject" in config:
                results["has_linting_config"] = True
    
    return results

def check_docker_files(workspace_root: Path) -> Dict:
    """Check for Docker configuration"""
    results = {
        "dockerfiles": [],
        "docker_compose": [],
        "has_docker": False
    }
    
    for dockerfile in workspace_root.glob("**/Dockerfile*"):
        if "node_modules" not in str(dockerfile):
            results["dockerfiles"].append(str(dockerfile.relative_to(workspace_root)))
            results["has_docker"] = True
    
    for compose in workspace_root.glob("**/docker-compose*.yml"):
        if "node_modules" not in str(compose):
            results["docker_compose"].append(str(compose.relative_to(workspace_root)))
            results["has_docker"] = True
    
    for compose in workspace_root.glob("**/docker-compose*.yaml"):
        if "node_modules" not in str(compose):
            results["docker_compose"].append(str(compose.relative_to(workspace_root)))
            results["has_docker"] = True
    
    return results

def main():
    """Run additional health checks"""
    workspace_root = Path(__file__).parent.parent
    
    print("=" * 80)
    print("ADDITIONAL HEALTH CHECKS")
    print("=" * 80)
    print()
    
    # Test files check
    print("📋 Checking test files...")
    test_results = check_test_files(workspace_root)
    print(f"  ✅ Found {test_results['test_files_found']} test files")
    print(f"  📊 Test types: Unit={test_results['test_types']['unit']}, "
          f"Integration={test_results['test_types']['integration']}, "
          f"E2E={test_results['test_types']['e2e']}, "
          f"Security={test_results['test_types']['security']}")
    print()
    
    # Documentation check
    print("📚 Checking documentation...")
    doc_results = check_documentation(workspace_root)
    print(f"  ✅ Found {len(doc_results['readme_files'])} README files")
    print(f"  ✅ Found {len(doc_results['doc_files'])} documentation files")
    print(f"  ✅ Found {len(doc_results['api_docs'])} API documentation files")
    print()
    
    # Code quality check
    print("💻 Checking code quality metrics...")
    quality_results = check_code_quality(workspace_root)
    print(f"  ✅ Found {quality_results['python_files']} Python files")
    print(f"  ✅ Found {quality_results['typescript_files']} TypeScript files")
    print(f"  ✅ Total lines of code: {quality_results['total_lines']:,}")
    print(f"  {'✅' if quality_results['has_linting_config'] else '❌'} Linting config: {quality_results['has_linting_config']}")
    print(f"  {'✅' if quality_results['has_formatting_config'] else '❌'} Formatting config: {quality_results['has_formatting_config']}")
    print()
    
    # Docker check
    print("🐳 Checking Docker configuration...")
    docker_results = check_docker_files(workspace_root)
    print(f"  {'✅' if docker_results['has_docker'] else '❌'} Docker support: {docker_results['has_docker']}")
    if docker_results['dockerfiles']:
        print(f"  ✅ Found {len(docker_results['dockerfiles'])} Dockerfiles")
    if docker_results['docker_compose']:
        print(f"  ✅ Found {len(docker_results['docker_compose'])} docker-compose files")
    print()
    
    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Test Files: {test_results['test_files_found']}")
    print(f"Documentation Files: {len(doc_results['readme_files']) + len(doc_results['doc_files'])}")
    print(f"Code Files: {quality_results['python_files'] + quality_results['typescript_files']}")
    print(f"Docker Support: {'Yes' if docker_results['has_docker'] else 'No'}")
    print("=" * 80)
    
    return 0

if __name__ == '__main__':
    sys.exit(main())

