#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script for Chrome URL extraction
"""

import subprocess
import sys

def get_foreground_tab_url():
    """Get URL from the active Chrome tab"""
    script = '''
    tell application "Google Chrome"
        get URL of active tab of front window
    end tell
    '''
    try:
        result = subprocess.run(['osascript', '-e', script], 
                               capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error: Could not get URL from Chrome: {e}")
        print(f"stderr: {e.stderr}")
        return None

def get_chrome_tabs():
    """Get URLs from all Chrome tabs"""
    script = '''
    tell application "Google Chrome"
        set tabList to {}
        set windowList to every window
        repeat with theWindow in windowList
            set tabList to tabList & (URL of every tab of theWindow)
        end repeat
        return tabList
    end tell
    '''
    try:
        result = subprocess.run(['osascript', '-e', script], 
                               capture_output=True, text=True, check=True)
        return result.stdout.strip().split(', ')
    except subprocess.CalledProcessError as e:
        print(f"Error: Could not get URLs from Chrome: {e}")
        print(f"stderr: {e.stderr}")
        return []

def main():
    print("Testing Chrome URL extraction...")
    
    # Test foreground tab
    print("\n1. Testing foreground tab URL extraction:")
    url = get_foreground_tab_url()
    if url:
        print(f"Success! Foreground tab URL: {url}")
    else:
        print("Failed to get foreground tab URL")
    
    # Test all tabs
    print("\n2. Testing all tabs URL extraction:")
    urls = get_chrome_tabs()
    if urls:
        print(f"Success! Found {len(urls)} tabs:")
        for i, url in enumerate(urls):
            print(f"  {i+1}. {url}")
    else:
        print("Failed to get Chrome tabs")

if __name__ == "__main__":
    main()