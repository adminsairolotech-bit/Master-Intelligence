"""
Code Fixer - Main CLI Entry Point
SAI ROLO TECH
"""

import argparse
import sys
from pathlib import Path

from analyzer import CodeAnalyzer
from fixer import CodeFixer


def main():
    parser = argparse.ArgumentParser(
        description="Code Fixer - Automated code analysis and fixing"
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze code for issues")
    analyze_parser.add_argument("path", help="File or directory to analyze")
    analyze_parser.add_argument("--fix", action="store_true", help="Auto-fix issues")

    # Fix command
    fix_parser = subparsers.add_parser("fix", help="Fix code issues")
    fix_parser.add_argument("path", help="File to fix")
    fix_parser.add_argument("--dry-run", action="store_true", help="Preview without changes")
    fix_parser.add_argument("--backup", action="store_true", default=True, help="Create backup")

    # Pattern list
    subparsers.add_parser("patterns", help="List available fix patterns")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == "analyze":
        analyzer = CodeAnalyzer(args.path)
        issues = analyzer.analyze()

        print(f"\n{'='*50}")
        print(f"ANALYSIS RESULTS: {args.path}")
        print(f"{'='*50}")

        if not issues:
            print("✅ No issues found!")
        else:
            for issue in issues:
                print(f"\n❌ {issue['type']}")
                print(f"   Location: {issue['file']}:{issue['line']}")
                print(f"   Message: {issue['message']}")

                if args.fix:
                    fixer = CodeFixer(args.path)
                    if fixer.fix_issue(issue):
                        print("   ✅ Fixed!")
                    else:
                        print("   ⚠️ Could not auto-fix")

    elif args.command == "fix":
        fixer = CodeFixer(args.path)

        if args.dry_run:
            print("🔍 Dry run mode - no changes will be made")

        result = fixer.fix_all(dry_run=args.dry_run, backup=args.backup)

        print(f"\n{'='*50}")
        print(f"FIX RESULTS")
        print(f"{'='*50}")
        print(f"Files processed: {result['processed']}")
        print(f"Issues fixed: {result['fixed']}")
        print(f"Errors: {result['errors']}")

    elif args.command == "patterns":
        print("\nAvailable Fix Patterns:")
        print("="*40)

        patterns = [
            ("unused-imports", "Remove unused imports"),
            ("unused-variables", "Remove or prefix unused variables"),
            ("missing-types", "Add type hints"),
            ("docstring", "Add missing docstrings"),
            ("naming", "Fix naming conventions"),
            ("formatting", "Fix code formatting"),
            ("security", "Fix security issues"),
        ]

        for pattern, desc in patterns:
            print(f"  {pattern:20} - {desc}")


if __name__ == "__main__":
    main()
