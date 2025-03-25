#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Integration tests for vapi-transcripts.py script
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock, mock_open
import subprocess
import json

# Add parent directory to path so we can import the script
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# We'll import the functions but mock external dependencies
import vapi_transcripts

class TestIntegration(unittest.TestCase):
    """Integration tests for VAPI transcripts script"""

    def setUp(self):
        """Set up test environment"""
        # Save actual environment to restore it after tests
        self.original_env = os.environ.copy()
        
        # Sample test data
        self.sample_assistant_id = "a37edc9f-852d-41b3-8601-801c20292716"
        self.sample_api_key = "test_api_key"  # Not a real API key
        
        # Create a temp .env file for testing
        with open('.env.test', 'w') as f:
            f.write(f"VAPI_API_KEY={self.sample_api_key}\n")
        
    def tearDown(self):
        """Clean up after tests"""
        # Restore original environment
        os.environ.clear()
        os.environ.update(self.original_env)
        
        # Remove test .env file
        if os.path.exists('.env.test'):
            os.remove('.env.test')
    
    @patch('subprocess.run')
    @patch('vapi_transcripts.get_foreground_tab_url')
    @patch('vapi_transcripts.check_venv_setup')
    @patch('vapi_transcripts.fetch_transcripts')
    @patch('vapi_transcripts.process_transcripts')
    @patch('vapi_transcripts.check_api_key')
    @patch('vapi_transcripts.parse_args')
    def test_workflow_with_foreground_tab(self, mock_parse_args, mock_check_api, mock_process, 
                                          mock_fetch, mock_venv, mock_get_url, mock_run):
        """Test the workflow when the assistant ID is in the foreground tab"""
        # Set up all mocks
        mock_args = MagicMock()
        mock_args.assistant_id = None
        mock_args.output = None
        mock_args.no_paste = False
        mock_args.min_duration = 0
        mock_args.days = None
        mock_args.today = False
        mock_args.limit = None
        mock_parse_args.return_value = mock_args
        
        mock_venv.return_value = True
        mock_check_api.return_value = self.sample_api_key
        mock_get_url.return_value = f"https://dashboard.vapi.ai/call/123?assistantId={self.sample_assistant_id}"
        mock_process.return_value = True
        mock_run.return_value = MagicMock(returncode=0)
        
        # Import the main function
        from vapi_transcripts import main
        
        # Call the main function directly
        result = main()
        
        # Check if the script executed without error
        self.assertEqual(result, 0)
        
        # Verify process_transcripts was called with correct parameters
        # The assistant ID should be extracted from the mock URL
        mock_process.assert_called_once_with(
            self.sample_assistant_id, 
            self.sample_api_key,
            output_file=None, 
            min_duration=0, 
            days_ago=None, 
            limit=None, 
            today_only=False, 
            no_paste=False
        )
            
    @patch('subprocess.run')
    @patch('vapi_transcripts.get_foreground_tab_url')
    @patch('vapi_transcripts.find_vapi_tabs') 
    @patch('vapi_transcripts.check_venv_setup')
    @patch('vapi_transcripts.process_transcripts')
    @patch('vapi_transcripts.check_api_key')
    @patch('vapi_transcripts.parse_args')
    def test_workflow_with_multiple_tabs(self, mock_parse_args, mock_check_api, mock_process, 
                                         mock_venv, mock_find_tabs, mock_get_url, mock_run):
        """Test the workflow when the assistant ID is not in the foreground tab"""
        # Set up all mocks
        mock_args = MagicMock()
        mock_args.assistant_id = None
        mock_args.output = None
        mock_args.no_paste = False
        mock_args.min_duration = 0
        mock_args.days = None
        mock_args.today = False
        mock_args.limit = None
        mock_parse_args.return_value = mock_args
        
        mock_venv.return_value = True
        mock_check_api.return_value = self.sample_api_key
        mock_get_url.return_value = "https://google.com"  # No assistant ID in foreground
        mock_find_tabs.return_value = [
            ("https://dashboard.vapi.ai/call/123?assistantId=a37edc9f-852d-41b3-8601-801c20292716", 
             "a37edc9f-852d-41b3-8601-801c20292716"),
            ("https://dashboard.vapi.ai/call/456?assistantId=b47edc9f-852d-41b3-8601-801c20292717",
             "b47edc9f-852d-41b3-8601-801c20292717")
        ]
        mock_process.return_value = True
        mock_run.return_value = MagicMock(returncode=0)
        
        # Import the main function
        from vapi_transcripts import main
        
        # Call the main function directly
        result = main()
        
        # Check if the script executed without error
        self.assertEqual(result, 0)
        
        # Verify process_transcripts was called with correct parameters (first tab should be used)
        mock_process.assert_called_once_with(
            "a37edc9f-852d-41b3-8601-801c20292716", 
            self.sample_api_key,
            output_file=None, 
            min_duration=0, 
            days_ago=None, 
            limit=None, 
            today_only=False, 
            no_paste=False
        )

    @patch('subprocess.run')
    @patch('vapi_transcripts.parse_args')
    @patch('vapi_transcripts.get_foreground_tab_url')
    @patch('vapi_transcripts.check_venv_setup')
    @patch('vapi_transcripts.process_transcripts')
    @patch('vapi_transcripts.check_api_key')
    def test_command_line_args(self, mock_check_api, mock_process, mock_venv, 
                               mock_get_url, mock_parse_args, mock_run):
        """Test the workflow with command-line arguments"""
        # Create a mock args object
        mock_args = MagicMock()
        mock_args.assistant_id = "manually-specified-id"
        mock_args.output = "test_output.md"
        mock_args.no_paste = True
        mock_args.min_duration = 60
        mock_args.days = 7
        mock_args.today = False
        mock_args.limit = 5
        
        # Set up all mocks
        mock_parse_args.return_value = mock_args
        mock_venv.return_value = True
        mock_check_api.return_value = self.sample_api_key
        mock_process.return_value = True
        mock_run.return_value = MagicMock(returncode=0)
        
        # Import the main function
        from vapi_transcripts import main
        
        # Call the main function directly
        result = main()
        
        # Check if the script executed without error
        self.assertEqual(result, 0)
        
        # Verify process_transcripts was called with correct parameters
        mock_process.assert_called_once_with(
            "manually-specified-id",
            self.sample_api_key,
            output_file="test_output.md",
            min_duration=60,
            days_ago=7,
            limit=5,
            today_only=False,
            no_paste=True
        )
        
        # Verify Chrome URL was not fetched since we provided assistant_id via args
        mock_get_url.assert_not_called()

if __name__ == '__main__':
    unittest.main()