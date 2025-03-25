#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script for clipboard operations
"""

import subprocess
import sys

def copy_to_clipboard(text):
    """Copy text to clipboard"""
    print(f"Copying {len(text)} characters to clipboard...")
    try:
        subprocess.run('pbcopy', input=text.encode('utf-8'), check=True)
        print("Text successfully copied to clipboard!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error copying to clipboard: {e}")
        return False

def paste_from_clipboard():
    """Test paste from clipboard (just prints instructions)"""
    print("\nTo test pasting, place your cursor in a text field and run:")
    print("osascript -e 'tell application \"System Events\" to keystroke \"v\" using command down'")
    print("\nThis script won't perform the paste operation to avoid unexpected results.")

def main():
    # Test copying to clipboard
    test_text = "This is a test of the clipboard functionality.\n" * 5
    copy_to_clipboard(test_text)
    
    # Show paste instructions
    paste_from_clipboard()

if __name__ == "__main__":
    main()