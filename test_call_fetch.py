#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script to verify call fetching and transcript extraction
"""

import os
import sys
import json
import traceback
from datetime import datetime

# Get absolute path to script directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Load API key from .env file
API_KEY = None
env_path = os.path.join(SCRIPT_DIR, '.env')
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

# Activate virtual environment
venv_activation = f"source {SCRIPT_DIR}/venv/bin/activate"
os.system(venv_activation)

try:
    from vapi import Vapi
except ImportError:
    print("Error: VAPI SDK not found. Please run:")
    print(f"cd {SCRIPT_DIR} && python3 -m venv venv && source venv/bin/activate && pip install vapi_server_sdk")
    sys.exit(1)

def get_all_calls(assistant_id):
    """Fetch all calls for a given assistant ID"""
    print(f"Fetching calls for assistant ID: {assistant_id}")
    client = Vapi(token=API_KEY)
    
    try:
        response = client.calls.list(assistant_id=assistant_id)
        calls = list(response)
        print(f"Found {len(calls)} calls")
        return calls
    except Exception as e:
        print(f"Error fetching calls: {e}")
        traceback.print_exc()
        return []

def get_call_by_id(all_calls, call_id):
    """Find a specific call by ID from a list of calls"""
    print(f"Looking for call with ID: {call_id}")
    for call in all_calls:
        if getattr(call, "id", "") == call_id:
            print(f"Found call with ID: {call_id}")
            return call
    
    print(f"Call with ID {call_id} not found in the list of calls")
    return None

def dump_call_object(call, output_file=None):
    """Dump call object structure for debugging"""
    try:
        call_dict = call.dict()
        json_str = json.dumps(call_dict, indent=2)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(json_str)
            print(f"Call structure written to {output_file}")
        else:
            print(json_str)
    except Exception as e:
        print(f"Error dumping call object: {e}")
        # Try direct attribute dump if dict conversion fails
        print("\nAttributes:")
        for attr in dir(call):
            if not attr.startswith('_') and not callable(getattr(call, attr)):
                try:
                    value = getattr(call, attr)
                    print(f"{attr}: {value}")
                except:
                    print(f"{attr}: <error getting value>")

def extract_transcript(call):
    """Extract transcript from call object using multiple approaches"""
    if not call:
        return "No call data available"
    
    call_id = getattr(call, "id", "unknown")
    try:
        created_at = getattr(call, "createdAt", "")
        call_date = datetime.fromisoformat(created_at.replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M:%S')
    except (ValueError, TypeError, AttributeError) as e:
        print(f"Error parsing date: {e}")
        call_date = "Unknown date"
    
    result = f"# Call - {call_date} (ID: {call_id})\n\n"
    transcript_found = False
    
    # Print all available attributes on the call object for debugging
    print("\nAll call attributes:")
    for attr_name in dir(call):
        if not attr_name.startswith('_') and not callable(getattr(call, attr_name)):
            try:
                attr_value = getattr(call, attr_name)
                if attr_name in ['artifact', 'transcript', 'messages']:
                    print(f"- {attr_name}: {type(attr_value)}")
                    if attr_value:
                        if isinstance(attr_value, list):
                            print(f"  List with {len(attr_value)} items")
                            if len(attr_value) > 0:
                                print(f"  First item type: {type(attr_value[0])}")
                                for prop in dir(attr_value[0]):
                                    if not prop.startswith('_') and not callable(getattr(attr_value[0], prop)):
                                        try:
                                            prop_value = getattr(attr_value[0], prop)
                                            print(f"    - {prop}: {prop_value}")
                                        except:
                                            print(f"    - {prop}: <error>")
                        else:
                            # If it's an object, print its properties
                            for prop in dir(attr_value):
                                if not prop.startswith('_') and not callable(getattr(attr_value, prop)):
                                    try:
                                        prop_value = getattr(attr_value, prop)
                                        if isinstance(prop_value, list):
                                            print(f"  - {prop}: List with {len(prop_value)} items")
                                            if len(prop_value) > 0:
                                                print(f"    First item type: {type(prop_value[0])}")
                                        else:
                                            print(f"  - {prop}: {prop_value}")
                                    except:
                                        print(f"  - {prop}: <error>")
                else:
                    print(f"- {attr_name}: {attr_value}")
            except:
                print(f"- {attr_name}: <error getting value>")
                
    # 1. Try direct transcript attribute if available
    transcript = getattr(call, "transcript", None)
    if transcript:
        print(f"\nFound transcript attribute with {len(transcript)} entries")
        transcript_found = True
        # Sort transcript entries by creation time
        sorted_entries = sorted(transcript, key=lambda x: getattr(x, "createdAt", ""))
        
        for entry in sorted_entries:
            role = "AI" if getattr(entry, "role", "") == "assistant" else "Human"
            content = getattr(entry, "content", "")
            result += f"{role}: {content}\n\n"
    
    # 2. Try messages in artifact
    artifact = getattr(call, "artifact", None)
    if artifact:
        messages = getattr(artifact, "messages", [])
        if messages:
            print(f"\nFound artifact messages with {len(messages)} entries")
            transcript_found = True
            # Sort messages by time
            sorted_messages = sorted(messages, key=lambda x: getattr(x, "time", 0))
            
            for message in sorted_messages:
                role = "AI" if getattr(message, "role", "") == "bot" else "Human"
                content = getattr(message, "message", "")
                result += f"{role}: {content}\n\n"
    
    # 3. Try the messages attribute directly if available
    messages = getattr(call, "messages", [])
    if messages:
        print(f"\nFound messages attribute with {len(messages)} entries")
        transcript_found = True
        sorted_messages = sorted(messages, key=lambda x: getattr(x, "createdAt", ""))
        
        for message in sorted_messages:
            role = "AI" if getattr(message, "role", "") == "assistant" else "Human"
            content = getattr(message, "content", "")
            result += f"{role}: {content}\n\n"
    
    if not transcript_found:
        print("No transcript found in any attribute")
        result += "No transcript available for this call\n\n"
    
    result += "---\n\n"
    return result

def main():
    # Use specific assistant ID and call ID for testing
    assistant_id = "a37edc9f-852d-41b3-8601-801c20292716"
    specific_call_id = "aafc223a-49fa-4964-96c3-dd320832ca5f"
    
    client = Vapi(token=API_KEY)
    
    # Test 1: Get all calls for assistant
    print("\n=== TEST 1: Fetch all calls for assistant ===")
    calls = get_all_calls(assistant_id)
    if not calls:
        print("No calls found for this assistant")
        sys.exit(1)
    
    # Display call count and IDs 
    print(f"Found {len(calls)} calls")
    print("First 5 call IDs:")
    for i, call in enumerate(calls[:5]):
        call_id = getattr(call, "id", "unknown")
        duration = getattr(call, "duration", 0)
        print(f"  {i+1}. ID: {call_id}, Duration: {duration}s")
    
    # Test 2: Find specific call by ID from the list
    print("\n=== TEST 2: Find specific call by ID ===")
    specific_call = get_call_by_id(calls, specific_call_id)
    if not specific_call:
        print(f"Could not find call with ID: {specific_call_id}")
    else:
        print(f"Successfully found call with ID: {specific_call_id}")
        
        # Dump call structure for debugging
        dump_output = os.path.join(SCRIPT_DIR, "call_structure.json")
        dump_call_object(specific_call, dump_output)
        
        # Test 3: Extract transcript
        print("\n=== TEST 3: Extract transcript ===")
        transcript = extract_transcript(specific_call)
        print("\nExtracted transcript:")
        print(transcript)
        
        # Write transcript to file for review
        transcript_file = os.path.join(SCRIPT_DIR, "test_transcript.txt")
        with open(transcript_file, 'w') as f:
            f.write(transcript)
        print(f"Transcript written to {transcript_file}")

if __name__ == "__main__":
    main()