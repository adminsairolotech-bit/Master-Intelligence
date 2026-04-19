"""
Code Validator - Quality checks for generated code
SAI ROLO TECH
"""

import ast
import re
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class ValidationIssue:
    severity: str  # HIGH, MEDIUM, LOW
    category: str   # security, style, logic, completeness
    message: str
    line: int = 0
    suggestion: str = ""


class CodeValidator:
    """Validates generated code for quality and issues."""

    def __init__(self):
        self.issues: List[ValidationIssue] = []

    def validate(self, code: str, language: str = "python") -> Dict:
        """
        Run all validation checks on code.
        Returns dict with status, score, and issues.
        """
        self.issues = []

        if language == "python":
            self._validate_python(code)
        elif language in ["javascript", "typescript"]:
            self._validate_js(code)
        else:
            self._validate_generic(code)

        return self._format_result()

    def _validate_python(self, code: str):
        """Validate Python code."""
        # Syntax check
        try:
            ast.parse(code)
        except SyntaxError as e:
            self.issues.append(ValidationIssue(
                severity="HIGH",
                category="syntax",
                message=f"Syntax error: {e.msg}",
                line=e.lineno or 0,
                suggestion="Fix syntax before continuing"
            ))

        # Security checks
        self._check_security(code)

        # Style checks
        self._check_style(code)

        # Completeness checks
        self._check_completeness(code)

    def _validate_js(self, code: str):
        """Validate JavaScript/TypeScript code."""
        # Basic checks for JS
        if "console.log" in code or "console.warn" in code:
            self.issues.append(ValidationIssue(
                severity="LOW",
                category="style",
                message="Console statements found",
                suggestion="Remove debug console statements"
            ))

    def _validate_generic(self, code: str):
        """Generic validation for any language."""
        if len(code.strip()) < 20:
            self.issues.append(ValidationIssue(
                severity="HIGH",
                category="completeness",
                message="Code appears empty or too short",
                suggestion="Generate actual implementation"
            ))

    def _check_security(self, code: str):
        """Check for security issues."""
        # Hardcoded secrets
        patterns = [
            (r'password\s*=\s*["\'][^"\']{1,}', "Hardcoded password"),
            (r'api_key\s*=\s*["\'][^"\']{8,}', "Hardcoded API key"),
            (r'secret\s*=\s*["\'][^"\']{8,}', "Hardcoded secret"),
            (r'eval\s*\(', "Use of eval() - security risk"),
            (r'exec\s*\(', "Use of exec() - security risk"),
        ]

        for pattern, message in patterns:
            if re.search(pattern, code, re.IGNORECASE):
                self.issues.append(ValidationIssue(
                    severity="HIGH",
                    category="security",
                    message=message,
                    suggestion="Use environment variables for secrets"
                ))

    def _check_style(self, code: str):
        """Check for style issues."""
        lines = code.split('\n')

        # Long lines
        for i, line in enumerate(lines, 1):
            if len(line) > 120:
                self.issues.append(ValidationIssue(
                    severity="LOW",
                    category="style",
                    message=f"Line exceeds 120 characters ({len(line)})",
                    line=i,
                    suggestion="Break long lines"
                ))

        # Missing docstrings on functions
        if 'def ' in code and '"""' not in code and "'''" not in code:
            self.issues.append(ValidationIssue(
                severity="MEDIUM",
                category="style",
                message="Functions without docstrings",
                suggestion="Add docstrings to public functions"
            ))

    def _check_completeness(self, code: str):
        """Check for completeness."""
        # Check for TODO/FIXME without description
        for i, line in enumerate(code.split('\n'), 1):
            if ('TODO' in line or 'FIXME' in line) and '# ' not in line:
                self.issues.append(ValidationIssue(
                    severity="MEDIUM",
                    category="completeness",
                    message="TODO/FIXME without description",
                    line=i,
                    suggestion="Add a description to TODO comments"
                ))

    def _format_result(self) -> Dict:
        """Format validation results."""
        high_count = sum(1 for i in self.issues if i.severity == "HIGH")
        medium_count = sum(1 for i in self.issues if i.severity == "MEDIUM")
        low_count = sum(1 for i in self.issues if i.severity == "LOW")

        # Calculate score
        base_score = 100
        base_score -= high_count * 20
        base_score -= medium_count * 10
        base_score -= low_count * 5
        score = max(0, min(100, base_score))

        status = "PASS"
        if high_count > 0:
            status = "FAIL"
        elif medium_count > 2:
            status = "REVISE"

        return {
            "status": status,
            "score": score,
            "issues": [
                {
                    "severity": i.severity,
                    "type": i.category,
                    "message": i.message,
                    "line": i.line,
                    "suggestion": i.suggestion
                }
                for i in self.issues
            ],
            "summary": {
                "high": high_count,
                "medium": medium_count,
                "low": low_count
            }
        }
