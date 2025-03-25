#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
from datetime import datetime
from pprint import pprint

# Get the absolute path to the script directory
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

# Activate virtual environment and import the SDK
try:
    from vapi import Vapi
except ImportError:
    print("Error: VAPI SDK not found. Installing via pip...")
    os.system(f"cd {SCRIPT_DIR} && python3 -m venv venv && source venv/bin/activate && pip install vapi_server_sdk")
    try:
        from vapi import Vapi
    except ImportError:
        print("Error: Failed to install VAPI SDK")
        sys.exit(1)

def explore_metadata():
    """Explore available metadata in VAPI calls"""
    client = Vapi(token=API_KEY)
    
    # Get assistants
    print("Fetching assistants...")
    assistants = list(client.assistants.list())
    
    if not assistants:
        print("No assistants found")
        return
    
    print(f"Found {len(assistants)} assistants")
    
    for i, assistant in enumerate(assistants):
        assistant_id = getattr(assistant, "id", "unknown")
        assistant_name = getattr(assistant, "name", "unknown")
        print(f"{i+1}. {assistant_name} (ID: {assistant_id})")
    
    # Use the first assistant for testing
    assistant = assistants[0]
    assistant_id = assistant.id
    print(f"\nUsing assistant: {getattr(assistant, 'name', 'unknown')} (ID: {assistant_id})")
    
    # Fetch calls
    print("\nFetching calls...")
    response = client.calls.list(assistant_id=assistant_id)
    calls = list(response)
    
    if not calls:
        print("No calls found")
        return
    
    print(f"Found {len(calls)} calls")
    
    # Analyze date format
    print("\nAnalyzing date formats in calls...")
    date_formats = {}
    for call in calls:
        created_at = getattr(call, "createdAt", None)
        if created_at and created_at not in date_formats:
            date_formats[created_at] = True
    
    print(f"Sample date formats ({len(date_formats)} unique):")
    for date_format in list(date_formats.keys())[:3]:  # Show first 3 samples
        print(f"- {date_format}")
    
    # Test date parsing
    print("\nTesting date parsing methods:")
    for date_str in list(date_formats.keys())[:1]:  # Test with first date
        print(f"Input: '{date_str}'")
        try:
            # Try standard ISO format
            date_obj = datetime.fromisoformat(date_str)
            print(f"√ Standard ISO format works: {date_obj}")
        except ValueError:
            print("× Standard ISO format failed")
            
            try:
                # Try with Z replacement
                date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                print(f"√ Z replacement works: {date_obj}")
            except ValueError:
                print("× Z replacement failed")

    # Examine available metadata
    print("\nExamining available metadata across calls...")
    metadata_fields = {}
    
    for call in calls[:5]:  # Check first 5 calls
        for attr in dir(call):
            if not attr.startswith('_'):  # Skip private attributes
                try:
                    value = getattr(call, attr)
                    if not callable(value):  # Skip methods
                        if attr not in metadata_fields:
                            metadata_fields[attr] = []
                        
                        # Add the type and a sample value
                        if len(metadata_fields[attr]) < 3:  # Keep up to 3 samples
                            if isinstance(value, (str, int, float, bool)) or value is None:
                                sample = value
                            elif hasattr(value, '__dict__'):
                                sample = "Object"
                            elif isinstance(value, (list, tuple)):
                                sample = f"List ({len(value)} items)"
                            else:
                                sample = type(value).__name__
                            
                            metadata_fields[attr].append(sample)
                except Exception as e:
                    if attr not in metadata_fields:
                        metadata_fields[attr] = []
                    metadata_fields[attr].append(f"Error: {str(e)}")
    
    print("\nAvailable metadata fields:")
    for field, samples in sorted(metadata_fields.items()):
        print(f"- {field}: {samples}")
    
    # Get complete structure of a single call
    print("\nComplete structure of a single call:")
    call = calls[0]
    for attr in sorted(dir(call)):
        if not attr.startswith('_'):  # Skip private attributes
            try:
                value = getattr(call, attr)
                if not callable(value):  # Skip methods
                    if isinstance(value, (str, int, float, bool)) or value is None:
                        print(f"- {attr}: {value}")
                    elif hasattr(value, '__dict__'):
                        # Print object structure
                        sub_attrs = [a for a in dir(value) if not a.startswith('_') and not callable(getattr(value, a))]
                        print(f"- {attr}: Object with {len(sub_attrs)} attributes")
                        for sub_attr in sorted(sub_attrs):
                            try:
                                sub_value = getattr(value, sub_attr)
                                print(f"  - {sub_attr}: {sub_value if not isinstance(sub_value, (list, dict)) else type(sub_value).__name__}")
                            except:
                                print(f"  - {sub_attr}: <error>")
                    elif isinstance(value, (list, tuple)):
                        print(f"- {attr}: List with {len(value)} items")
                        if len(value) > 0:
                            item = value[0]
                            if hasattr(item, '__dict__'):
                                print(f"  First item attributes: {', '.join(sorted([a for a in dir(item) if not a.startswith('_') and not callable(getattr(item, a))]))}")
                    else:
                        print(f"- {attr}: {type(value).__name__}")
            except Exception as e:
                print(f"- {attr}: Error: {str(e)}")

def main():
    try:
        explore_metadata()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()