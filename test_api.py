#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script for VAPI API calls
"""

import os
import sys
import json
import urllib.request
import urllib.error
import urllib.parse
import ssl
from pprint import pprint

# Load API key from .env file
API_KEY = None
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
try:
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if line.startswith('VAPI_API_KEY='):
                    API_KEY = line.strip().split('=', 1)[1]
                    break
except Exception as e:
    print(f"Warning: Could not read API key from .env file: {e}")

if not API_KEY:
    print("Error: VAPI API key not found. Please create a .env file with VAPI_API_KEY=your_api_key")
    sys.exit(1)

def api_request(url, params=None):
    """Make a request to the VAPI API"""
    full_url = url
    
    # Add query parameters if provided
    if params:
        query_string = urllib.parse.urlencode(params)
        full_url = f"{url}?{query_string}"
    
    print(f"Making request to: {full_url}")
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    # Create request object
    req = urllib.request.Request(full_url, headers=headers)
    
    try:
        # Ignore SSL verification for simplicity
        context = ssl._create_unverified_context()
        
        # Make the request
        with urllib.request.urlopen(req, context=context) as response:
            # Read and parse the response
            response_data = response.read().decode('utf-8')
            return json.loads(response_data)
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.reason}")
        response_data = e.read().decode('utf-8')
        print(f"Response: {response_data}")
        return {}
    except urllib.error.URLError as e:
        print(f"URL Error: {e.reason}")
        return {}
    except Exception as e:
        print(f"Error: {e}")
        return {}

def test_api_key():
    """Test if the API key is valid"""
    print(f"Testing API key (first 8 chars): {API_KEY[:8]}...")
    
    result = api_request("https://api.vapi.ai/assistants")
    
    if result and 'data' in result:
        print("Success! API key is valid.")
        return True
    else:
        print("Error: API key validation failed.")
        return False

def fetch_calls(assistant_id):
    """Test fetching calls for a given assistant ID"""
    print(f"Fetching calls for assistant ID: {assistant_id}")
    
    result = api_request("https://api.vapi.ai/calls", {"assistantId": assistant_id})
    
    if result and 'data' in result:
        calls = result.get('data', [])
        print(f"Success! Found {len(calls)} calls.")
        
        if calls:
            print("\nFirst call details:")
            pprint(calls[0])
        
        return calls
    else:
        print("Error: Failed to fetch calls.")
        return []

def fetch_transcript(call_id):
    """Test fetching transcript for a given call ID"""
    print(f"Fetching transcript for call ID: {call_id}")
    
    result = api_request(f"https://api.vapi.ai/calls/{call_id}/transcript")
    
    if result and 'data' in result:
        transcripts = result.get('data', [])
        print(f"Success! Found {len(transcripts)} transcript entries.")
        
        if transcripts:
            print("\nFirst transcript entry:")
            pprint(transcripts[0])
        
        return transcripts
    else:
        print("Error: Failed to fetch transcript.")
        return []

def main():
    if len(sys.argv) < 2:
        print("Usage: python test_api.py <assistant_id> [call_id]")
        print("If call_id is provided, it will test the transcript endpoint")
        sys.exit(1)
    
    assistant_id = sys.argv[1]
    
    # Test API key
    if not test_api_key():
        sys.exit(1)
    
    # Test fetching calls
    calls = fetch_calls(assistant_id)
    
    # If a call ID is provided, test fetching transcript
    if len(sys.argv) > 2:
        call_id = sys.argv[2]
        fetch_transcript(call_id)
    # Otherwise, if we found calls, test with the first one
    elif calls:
        call_id = calls[0].get('id')
        if call_id:
            print(f"\nTesting transcript with first call ID: {call_id}")
            fetch_transcript(call_id)

if __name__ == "__main__":
    main()