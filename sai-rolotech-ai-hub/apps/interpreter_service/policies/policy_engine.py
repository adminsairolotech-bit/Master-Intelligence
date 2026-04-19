"""
Interpreter Service - Policy Engine
Security rules for code execution
"""

import re
import subprocess
import os
from typing import Dict, List, Tuple


class PolicyEngine:
    """
    Interpreter Policy Engine
    Enforces security rules for code execution
    """

    # ALLOWED - Safe to execute
    ALLOWED_COMMANDS = [
        "python", "python3", "pip", "node", "npm",
        "code", "notepad", "start", "open",
        "git", "dir", "type", "cat", "ls",
        "curl", "wget", "echo", "date", "time",
    ]

    # BLOCKED - Never execute
    BLOCKED_PATTERNS = [
        r"rm\s+-rf\s+/",           # Delete root
        r"del\s+/[sfq]",          # Windows delete
        r"format\s+[a-z]:",       # Format drive
        r"mkfs",                    # Make filesystem
        r">\s*/dev/sd",            # Write to disk
        r"\|\s*bash",              # Pipe to bash
        r"curl.*\|.*sh",           # Curl pipe sh
        r"wget.*\|.*sh",           # Wget pipe sh
        r"nc\s+-e",                # Netcat shell
        r"rm\s+-rf\s+\.",          # Delete current
        r":(){ :|:& };:",          # Fork bomb
        r"chmod\s+-R\s+777",       # Permission change
    ]

    # ALLOWED FOLDERS
    ALLOWED_PATHS = [
        os.path.expanduser("~"),
        "C:\\Users",
        "C:\\Program Files",
        os.getcwd(),
    ]

    def __init__(self):
        self.allowed_cmds = set(self.ALLOWED_COMMANDS)
        self.blocked_patterns = [re.compile(p, re.I) for p in self.BLOCKED_PATTERNS]

    def check_command(self, command: str) -> Tuple[bool, str]:
        """
        Check if command is safe to execute
        Returns: (is_safe, reason)
        """
        # Check blocked patterns
        for pattern in self.blocked_patterns:
            if pattern.search(command):
                return False, f"Blocked: matches dangerous pattern"

        # Check if command starts with allowed command
        first_word = command.strip().split()[0] if command.strip() else ""

        # Allow Python/Node code execution
        if first_word in ["python", "python3", "node", "npm"]:
            return True, "Allowed: safe language"

        # Check shell commands
        if first_word not in self.allowed_cmds and not first_word.startswith("./"):
            return False, f"Not in allowlist: {first_word}"

        return True, "Allowed"

    def check_file_access(self, filepath: str) -> Tuple[bool, str]:
        """Check if file path is accessible"""
        # Normalize path
        filepath = os.path.abspath(os.path.expanduser(filepath))

        # Check if in allowed paths
        for allowed in self.ALLOWED_PATHS:
            allowed = os.path.abspath(allowed)
            if filepath.startswith(allowed):
                return True, "Allowed"

        return False, f"Not in allowed paths: {filepath}"

    def sanitize_python(self, code: str) -> Tuple[bool, str]:
        """
        Sanitize Python code
        Returns: (is_safe, sanitized_code)
        """
        # Block imports that could be dangerous
        dangerous_imports = [
            "import os;",
            "import sys;",
            "from os import",
            "from sys import",
            "import subprocess;",
            "from subprocess import",
            "import socket;",
            "import requests;",
            "import urllib",
            "import httpx",
            "import websocket",
        ]

        for imp in dangerous_imports:
            if imp in code.lower():
                # Allow if it's just reading/writing files
                if "open(" not in code:
                    return False, f"Blocked import: {imp}"

        return True, code

    def execute(self, command: str, language: str = "shell") -> Dict:
        """
        Execute command with policy check
        Returns: {success, output, error, safe}
        """
        result = {
            "success": False,
            "output": "",
            "error": "",
            "safe": False,
            "command": command
        }

        # For Python/Node, use sanitize_python instead of check_command
        if language in ["python", "python3"]:
            is_safe, reason = self.sanitize_python(command)
            result["safe"] = is_safe
            if not is_safe:
                result["error"] = f"POLICY DENIED: {reason}"
                return result
        elif language == "node":
            # Node is generally safe for JS execution
            result["safe"] = True
        else:
            # Check policy for shell commands
            is_safe, reason = self.check_command(command)
            result["safe"] = is_safe

            if not is_safe:
                result["error"] = f"POLICY DENIED: {reason}"
                return result

        # Execute
        try:
            if language == "python":
                output = subprocess.run(
                    ["python", "-c", command],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    shell=True
                )
            elif language == "shell":
                output = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
            else:
                output = subprocess.run(
                    [language, "-e", command],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    shell=True
                )

            result["success"] = output.returncode == 0
            result["output"] = output.stdout
            result["error"] = output.stderr

        except subprocess.TimeoutExpired:
            result["error"] = "⏱️ Timeout: Command took too long"
        except Exception as e:
            result["error"] = f"Error: {str(e)}"

        return result


# Singleton
policy = PolicyEngine()
