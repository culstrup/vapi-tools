#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import traceback

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

# Activate virtual environment and import the SDK
venv_activation = f"source {os.path.dirname(os.path.abspath(__file__))}/venv/bin/activate"
os.system(venv_activation)

try:
    from vapi import Vapi
except ImportError:
    print("Error: VAPI SDK not found. Make sure to run:")
    print("cd /Users/christianulstrup/Documents/scripts/vapi-tools && python3 -m venv venv && source venv/bin/activate && pip install vapi_server_sdk")
    sys.exit(1)

def examine_call_object(assistant_id):
    """Examine a call object to understand its structure"""
    try:
        client = Vapi(token=API_KEY)
        response = client.calls.list(assistant_id=assistant_id)
        calls = list(response)
        
        if not calls:
            print("No calls found for this assistant ID")
            return
        
        call = calls[0]
        
        # Print all attributes
        print("Call object attributes:")
        for key in dir(call):
            if not key.startswith('_'):  # Skip internal attributes
                try:
                    value = getattr(call, key)
                    if not callable(value):  # Skip methods
                        print(f"{key}: {value}")
                except:
                    print(f"{key}: <error getting value>")
        
        # Print dictionary representation if possible
        try:
            call_dict = call.dict()
            print("\nCall as dictionary:")
            print(json.dumps(call_dict, indent=2))
        except:
            print("\nCould not convert call to dictionary")
            traceback.print_exc()
            
        # Check for transcript-related methods
        print("\nChecking for transcript methods:")
        client_dir = dir(client)
        for item in client_dir:
            if 'transcript' in item.lower() or 'message' in item.lower():
                print(f"Found potential method: {item}")
                
        # Check for calls methods
        print("\nCalls methods:")
        calls_dir = dir(client.calls)
        for item in calls_dir:
            if not item.startswith('_'):
                print(f"- {item}")
        
    except Exception as e:
        print(f"Error examining call: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        assistant_id = sys.argv[1]
    else:
        assistant_id = "a37edc9f-852d-41b3-8601-801c20292716"  # Default assistant ID
        
    examine_call_object(assistant_id)