"""
Code Analyzer - AST-based code analysis
SAI ROLO TECH
"""

import ast
from pathlib import Path
from typing import List, Dict


class CodeAnalyzer:
    """Analyzes code files for issues using AST parsing."""

    def __init__(self, path: str):
        self.path = Path(path)
        self.issues = []

    def analyze(self) -> List[Dict]:
        """Analyze file or directory."""
        if self.path.is_file():
            return self._analyze_file(self.path)
        elif self.path.is_dir():
            return self._analyze_directory()
        else:
            return [{"type": "ERROR", "file": str(self.path), "line": 0,
                     "message": "Path does not exist"}]

    def _analyze_file(self, filepath: Path) -> List[Dict]:
        """Analyze single file."""
        issues = []

        if filepath.suffix not in ['.py', '.js', '.ts', '.go']:
            return issues

        try:
            if filepath.suffix == '.py':
                issues = self._analyze_python(filepath)
        except Exception as e:
            issues.append({
                "type": "PARSE_ERROR",
                "file": str(filepath),
                "line": 0,
                "message": str(e)
            })

        return issues

    def _analyze_directory(self) -> List[Dict]:
        """Analyze all Python files in directory."""
        all_issues = []

        for filepath in self.path.rglob("*.py"):
            issues = self._analyze_file(filepath)
            all_issues.extend(issues)

        return all_issues

    def _analyze_python(self, filepath: Path) -> List[Dict]:
        """Analyze Python file using AST."""
        issues = []

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        try:
            tree = ast.parse(content)

            # Check for unused imports
            used_names = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Name):
                    used_names.add(node.id)
                elif isinstance(node, ast.Attribute):
                    if isinstance(node.value, ast.Name):
                        used_names.add(node.value.id)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        name = alias.asname or alias.name.split('.')[0]
                        if name not in used_names:
                            issues.append({
                                "type": "unused-import",
                                "file": str(filepath),
                                "line": node.lineno,
                                "message": f"Unused import: {alias.name}",
                                "fix_type": "remove_import"
                            })
                elif isinstance(node, ast.ImportFrom):
                    if node.module and node.module not in ['__future__']:
                        for alias in node.names:
                            name = alias.asname or alias.name
                            if name not in used_names:
                                issues.append({
                                    "type": "unused-import",
                                    "file": str(filepath),
                                    "line": node.lineno,
                                    "message": f"Unused import: from {node.module} import {alias.name}",
                                    "fix_type": "remove_import"
                                })

            # Check for missing docstrings
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    if not ast.get_docstring(node):
                        issues.append({
                            "type": "missing-docstring",
                            "file": str(filepath),
                            "line": node.lineno,
                            "message": f"Missing docstring: {node.name}",
                            "fix_type": "add_docstring"
                        })

            # Check for bare except
            for node in ast.walk(tree):
                if isinstance(node, ast.ExceptHandler):
                    if node.type is None:
                        issues.append({
                            "type": "bare-except",
                            "file": str(filepath),
                            "line": node.lineno,
                            "message": "Bare except clause (use specific exception)",
                            "fix_type": "specific_except"
                        })

            # Check for TODO without format
            for i, line in enumerate(content.split('\n'), 1):
                if 'TODO' in line or 'FIXME' in line or 'XXX' in line:
                    if '# ' not in line and '// ' not in line:
                        issues.append({
                            "type": "todo-format",
                            "file": str(filepath),
                            "line": i,
                            "message": f"TODO/FIXME comment without description",
                            "fix_type": "add_todo_desc"
                        })

        except SyntaxError as e:
            issues.append({
                "type": "syntax-error",
                "file": str(filepath),
                "line": e.lineno or 0,
                "message": str(e)
            })

        return issues
