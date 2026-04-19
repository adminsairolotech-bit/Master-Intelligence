#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SikuliX Integration for Python
Uses subprocess to call SikuliX JAR for GUI automation
"""

import os
import subprocess
import sys

SIKULIX_JAR = os.path.expanduser("~/sikulix/sikulix.jar")

def check_sikulix():
    """Check if SikuliX is available"""
    if not os.path.exists(SIKULIX_JAR):
        print("[ERROR] SikuliX JAR not found at:", SIKULIX_JAR)
        print("Download from: https://sikulix.github.io/")
        return False
    print("[OK] SikuliX found:", SIKULIX_JAR)
    return True

def run_sikulix_script(script_path):
    """Run a SikuliX script (.sikuli folder)"""
    if not check_sikulix():
        return False

    cmd = ["java", "-jar", SIKULIX_JAR, "-r", script_path]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        print(result.stdout)
        return result.returncode == 0
    except Exception as e:
        print("[ERROR]", e)
        return False

if __name__ == "__main__":
    print("SikuliX Integration Test")
    print("=" * 40)
    check_sikulix()
    print("\nNote: For Python GUI automation, consider:")
    print("  pip install pyautogui")
    print("  pip install pywinauto")
    print("  pip install opencv-python")
