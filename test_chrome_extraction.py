#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script for extracting assistant IDs from Chrome tabs
"""

import os
import sys
import subprocess
import re
from typing import List, Optional, Tuple

def get_foreground_tab_url() -> str:
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
        return ""

def get_chrome_tabs() -> List[str]:
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

def extract_assistant_id(url: str) -> Optional[str]:
    """Extract assistant ID from URL"""
    match = re.search(r'assistantId=([^&]+)', url)
    if match:
        return match.group(1)
    return None

def find_vapi_tabs() -> List[Tuple[str, str]]:
    """Find all Chrome tabs with VAPI assistant IDs"""
    all_tabs = get_chrome_tabs()
    vapi_tabs = []
    
    for url in all_tabs:
        assistant_id = extract_assistant_id(url)
        if assistant_id:
            vapi_tabs.append((url, assistant_id))
    
    return vapi_tabs

def main():
    print("Testing Chrome URL extraction...")
    
    # Test foreground tab URL
    print("\n=== TEST 1: Get foreground tab URL ===")
    foreground_url = get_foreground_tab_url()
    print(f"Foreground tab URL: {foreground_url}")
    
    # Test foreground tab assistant ID extraction
    print("\n=== TEST 2: Extract assistant ID from foreground tab ===")
    foreground_assistant_id = extract_assistant_id(foreground_url)
    if foreground_assistant_id:
        print(f"Found assistant ID: {foreground_assistant_id}")
    else:
        print("No assistant ID found in foreground tab")
    
    # Test all Chrome tabs
    print("\n=== TEST 3: Get all Chrome tabs ===")
    all_tabs = get_chrome_tabs()
    print(f"Found {len(all_tabs)} Chrome tabs")
    
    # Test finding all VAPI tabs
    print("\n=== TEST 4: Find all VAPI tabs ===")
    vapi_tabs = find_vapi_tabs()
    if vapi_tabs:
        print(f"Found {len(vapi_tabs)} VAPI tabs:")
        for i, (url, assistant_id) in enumerate(vapi_tabs):
            print(f"  {i+1}. URL: {url}")
            print(f"     ID: {assistant_id}")
    else:
        print("No VAPI tabs found")
    
    # Test specific URL
    test_url = "https://dashboard.vapi.ai/calls?assistantId=a37edc9f-852d-41b3-8601-801c20292716"
    print(f"\n=== TEST 5: Extract ID from specific URL ===")
    print(f"URL: {test_url}")
    test_id = extract_assistant_id(test_url)
    print(f"Extracted ID: {test_id}")
    
    # Verify it matches expected ID
    expected_id = "a37edc9f-852d-41b3-8601-801c20292716"
    if test_id == expected_id:
        print("✅ ID matches expected value")
    else:
        print("❌ ID doesn't match expected value")
        print(f"Expected: {expected_id}")
        print(f"Got: {test_id}")

if __name__ == "__main__":
    main()