#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Unit tests for vapi-transcripts.py script
"""

import os
import sys
import unittest
import subprocess
from unittest.mock import patch, MagicMock, mock_open
from datetime import datetime
import json

# Add parent directory to path so we can import the script
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import functions from the script
# Note: We're importing individual functions to avoid executing the main script
from vapi_transcripts import (
    extract_assistant_id,
    find_vapi_tabs,
    copy_to_clipboard,
    check_api_key,
    fetch_transcripts,
    paste_from_clipboard,
    get_foreground_tab_url,
    get_chrome_tabs,
    check_venv_setup,
    run_with_venv
)

class TestVAPITranscripts(unittest.TestCase):
    """Test suite for VAPI transcripts script"""

    def setUp(self):
        """Set up test environment"""
        # Mock environment variables and paths
        self.mock_env_vars = {
            'SCRIPT_DIR': '/fake/path',
            'LOG_FILE': '/fake/path/vapi_transcript_debug.log'
        }
        
        # Sample test data
        self.sample_assistant_id = "a37edc9f-852d-41b3-8601-801c20292716"
        self.sample_chrome_tabs = [
            "https://dashboard.vapi.ai/call/123?assistantId=a37edc9f-852d-41b3-8601-801c20292716",
            "https://google.com",
            "https://dashboard.vapi.ai/call/456?assistantId=b47edc9f-852d-41b3-8601-801c20292717"
        ]
        
    @patch('subprocess.run')
    def test_copy_to_clipboard(self, mock_run):
        """Test copy_to_clipboard function"""
        test_text = "Test transcript"
        mock_run.return_value = MagicMock(returncode=0)
        
        copy_to_clipboard(test_text)
        
        mock_run.assert_called_once()
        # Check that pbcopy was called with the correct input
        args, kwargs = mock_run.call_args
        self.assertEqual(kwargs['input'], test_text.encode('utf-8'))
        
    @patch('subprocess.run')
    def test_get_foreground_tab_url(self, mock_run):
        """Test get_foreground_tab_url function"""
        # Mock successful command execution
        mock_process = MagicMock()
        mock_process.stdout = "https://dashboard.vapi.ai/call/123?assistantId=a37edc9f-852d-41b3-8601-801c20292716"
        mock_process.returncode = 0
        mock_run.return_value = mock_process
        
        # Call the function
        url = get_foreground_tab_url()
        
        # Verify result
        self.assertEqual(url, "https://dashboard.vapi.ai/call/123?assistantId=a37edc9f-852d-41b3-8601-801c20292716")
        mock_run.assert_called_once()
        
    @patch('subprocess.run')
    def test_get_chrome_tabs(self, mock_run):
        """Test get_chrome_tabs function"""
        # First mock the Chrome running check
        check_mock = MagicMock()
        check_mock.stdout = "true"
        check_mock.returncode = 0
        
        # Then mock the tab retrieval
        tabs_mock = MagicMock()
        tabs_mock.stdout = "https://example.com|https://dashboard.vapi.ai/call/123?assistantId=a37edc9f-852d-41b3-8601-801c20292716|"
        tabs_mock.returncode = 0
        
        # Setup the mock to return different values on successive calls
        mock_run.side_effect = [check_mock, tabs_mock]
        
        # Call the function
        tabs = get_chrome_tabs()
        
        # Verify result
        self.assertEqual(len(tabs), 2)
        self.assertEqual(tabs[0], "https://example.com")
        self.assertEqual(tabs[1], "https://dashboard.vapi.ai/call/123?assistantId=a37edc9f-852d-41b3-8601-801c20292716")
        self.assertEqual(mock_run.call_count, 2)
        
    def test_extract_assistant_id(self):
        """Test extract_assistant_id function"""
        # Test valid URL with assistant ID
        url = "https://dashboard.vapi.ai/call/123?assistantId=a37edc9f-852d-41b3-8601-801c20292716"
        assistant_id = extract_assistant_id(url)
        self.assertEqual(assistant_id, "a37edc9f-852d-41b3-8601-801c20292716")
        
        # Test URL without assistant ID
        url = "https://google.com"
        assistant_id = extract_assistant_id(url)
        self.assertIsNone(assistant_id)
        
        # Test URL with assistant ID in different position
        url = "https://dashboard.vapi.ai?foo=bar&assistantId=a37edc9f-852d-41b3-8601-801c20292716&other=stuff"
        assistant_id = extract_assistant_id(url)
        self.assertEqual(assistant_id, "a37edc9f-852d-41b3-8601-801c20292716")
        
        # Test empty URL
        url = ""
        assistant_id = extract_assistant_id(url)
        self.assertIsNone(assistant_id)
        
    @patch('vapi_transcripts.get_chrome_tabs')
    def test_find_vapi_tabs(self, mock_get_tabs):
        """Test find_vapi_tabs function"""
        mock_get_tabs.return_value = self.sample_chrome_tabs
        
        tabs = find_vapi_tabs()
        
        self.assertEqual(len(tabs), 2)  # Should find 2 tabs with assistant IDs
        self.assertEqual(tabs[0][1], "a37edc9f-852d-41b3-8601-801c20292716")
        self.assertEqual(tabs[1][1], "b47edc9f-852d-41b3-8601-801c20292717")
        
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data="VAPI_API_KEY=test_api_key")
    def test_check_api_key(self, mock_file, mock_exists):
        """Test check_api_key function"""
        mock_exists.return_value = True
        
        api_key = check_api_key()
        
        self.assertEqual(api_key, "test_api_key")
        
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data="NOT_A_VAPI_KEY=something")
    def test_check_api_key_missing(self, mock_file, mock_exists):
        """Test check_api_key function when key is missing"""
        mock_exists.return_value = True
        
        api_key = check_api_key()
        
        self.assertIsNone(api_key)
    
    # Simple tests for paste_from_clipboard on different platforms
    @patch('sys.platform', 'darwin')
    @patch('subprocess.run')
    def test_darwin_paste(self, mock_run):
        """Test paste on macOS"""
        mock_run.return_value = MagicMock(returncode=0)
        self.assertTrue(paste_from_clipboard())
        mock_run.assert_called_once()

    @patch('sys.platform', 'linux')
    def test_linux_paste(self):
        """Test paste on Linux"""
        # On Linux we just return True for CI compatibility
        self.assertTrue(paste_from_clipboard())

    @patch('sys.platform', 'win32')
    @patch('builtins.print')  # Suppress output during test
    def test_windows_paste_no_pyautogui(self, mock_print):
        """Test paste on Windows without pyautogui"""
        # Mock the ImportError for pyautogui
        with patch('builtins.__import__', side_effect=ImportError("No module named 'pyautogui'")):
            # Without pyautogui, it returns False on Windows
            self.assertFalse(paste_from_clipboard())
            
    @patch('sys.platform', 'win32')
    def test_windows_paste_with_pyautogui(self):
        """Test paste on Windows with pyautogui available"""
        # Mock pyautogui module
        mock_pyautogui = MagicMock()
        # Use a context manager to temporarily mock the import of pyautogui
        with patch.dict('sys.modules', {'pyautogui': mock_pyautogui}):
            # With pyautogui available, it returns True
            self.assertTrue(paste_from_clipboard())
            # Verify that hotkey was called
            mock_pyautogui.hotkey.assert_called_once_with('ctrl', 'v')

    @patch('sys.platform', 'darwin')
    @patch('subprocess.run')
    @patch('builtins.print')  # Suppress output during test
    def test_darwin_paste_error(self, mock_print, mock_run):
        """Test paste error handling on macOS"""
        mock_run.side_effect = subprocess.CalledProcessError(1, "osascript")
        # The function returns False when subprocess.run raises an exception
        self.assertFalse(paste_from_clipboard())
        mock_run.assert_called_once()
        
    @patch('os.path.exists')
    @patch('vapi_transcripts.run_with_venv')
    def test_check_venv_setup_exists(self, mock_run_with_venv, mock_exists):
        """Test check_venv_setup function when venv exists"""
        # Mock venv directory exists
        mock_exists.return_value = True
        # Mock successful pip command
        mock_run_with_venv.return_value = MagicMock(stdout="vapi 1.0.0", returncode=0)
        
        result = check_venv_setup()
        
        self.assertTrue(result)
        mock_exists.assert_called_once()
        mock_run_with_venv.assert_called_once()
        
    @patch('os.path.exists')
    @patch('subprocess.run')
    def test_check_venv_setup_not_exists(self, mock_run, mock_exists):
        """Test check_venv_setup function when venv doesn't exist"""
        # Mock venv directory doesn't exist
        mock_exists.return_value = False
        # Mock successful venv creation
        mock_run.return_value = MagicMock(returncode=0)
        
        with patch('vapi_transcripts.run_with_venv') as mock_run_with_venv:
            mock_run_with_venv.return_value = MagicMock(stdout="vapi 1.0.0", returncode=0)
            result = check_venv_setup()
            
        self.assertTrue(result)
        mock_exists.assert_called_once()
        mock_run.assert_called_once()
        
    @patch('os.path.exists')
    @patch('os.path.join')
    @patch('vapi_transcripts.log')  # Patch the log function
    @patch('builtins.open', new_callable=mock_open)
    @patch('vapi_transcripts.run_with_venv')
    @patch('os.remove')
    def test_fetch_transcripts(self, mock_remove, mock_run_with_venv, mock_file, mock_log, mock_join, mock_exists):
        """Test fetch_transcripts function"""
        # Setup mocks
        mock_exists.return_value = True
        mock_join.return_value = "/fake/path/_temp_fetch.py"
        
        # Mock the run_with_venv output
        mock_run_with_venv.return_value = MagicMock(
            stdout="Sample transcript data",
            stderr="",
            returncode=0
        )
        
        # Call the function
        result = fetch_transcripts("test-assistant-id", "test-api-key")
        
        # Verify results
        self.assertEqual(result, "Sample transcript data")
        mock_run_with_venv.assert_called_once()
        self.assertTrue(mock_file.called)
        mock_remove.assert_called_once()
        
    @patch('os.path.exists')
    @patch('os.path.join')
    @patch('vapi_transcripts.log')  # Patch the log function
    @patch('builtins.open', new_callable=mock_open)
    @patch('vapi_transcripts.run_with_venv')
    @patch('os.remove')
    def test_fetch_transcripts_error(self, mock_remove, mock_run_with_venv, mock_file, mock_log, mock_join, mock_exists):
        """Test fetch_transcripts function when it encounters an error"""
        # Setup mocks
        mock_exists.return_value = True
        mock_join.return_value = "/fake/path/_temp_fetch.py"
        
        # Mock the run_with_venv output with an error
        mock_run_with_venv.return_value = MagicMock(
            stdout="",
            stderr="Error occurred",
            returncode=1
        )
        
        # Call the function
        result = fetch_transcripts("test-assistant-id", "test-api-key")
        
        # Verify results
        self.assertIsNone(result)
        mock_run_with_venv.assert_called_once()
        self.assertTrue(mock_file.called)

    @patch('argparse.ArgumentParser.parse_args')
    def test_parse_args(self, mock_parse_args):
        """Test command-line argument parsing"""
        # Create a mock args object with default values
        mock_args = MagicMock()
        mock_args.assistant_id = None
        mock_args.output = None
        mock_args.no_paste = False
        mock_args.min_duration = 0
        mock_args.days = None
        mock_args.today = False
        mock_args.limit = None
        
        # Set up the mock to return our mock args
        mock_parse_args.return_value = mock_args
        
        # Import the function directly to avoid issues with argv
        from vapi_transcripts import parse_args
        
        # Call the function
        args = parse_args()
        
        # Verify the result
        self.assertEqual(args.assistant_id, None)
        self.assertEqual(args.output, None)
        self.assertEqual(args.no_paste, False)
        self.assertEqual(args.min_duration, 0)
        self.assertEqual(args.days, None)
        self.assertEqual(args.today, False)
        self.assertEqual(args.limit, None)
        
    @patch('vapi_transcripts.fetch_transcripts')
    @patch('vapi_transcripts.copy_to_clipboard')
    @patch('re.match')  # Patch re.match to pass the UUID validation
    def test_process_transcripts_with_filters(self, mock_re_match, mock_copy, mock_fetch):
        """Test process_transcripts function with filters"""
        # Setup mocks
        mock_fetch.return_value = "Test transcript content"
        mock_re_match.return_value = True  # Make the UUID validation pass
        
        # Call the function with various filters
        from vapi_transcripts import process_transcripts
        result = process_transcripts(
            "a37edc9f-852d-41b3-8601-801c20292716", 
            "test-api-key",
            min_duration=60,
            days_ago=7,
            limit=5,
            today_only=True
        )
        
        # Verify fetch_transcripts was called with the correct arguments
        mock_fetch.assert_called_once_with(
            "a37edc9f-852d-41b3-8601-801c20292716", 
            "test-api-key",
            min_duration=60,
            days_ago=7,
            limit=5,
            today_only=True
        )
        
        # Verify copy_to_clipboard was called with the correct content
        mock_copy.assert_called_once_with("Test transcript content")
        
        # Verify the result
        self.assertTrue(result)
        
    @patch('vapi_transcripts.fetch_transcripts')
    @patch('vapi_transcripts.log')  # Patch the log function to avoid file opening
    @patch('re.match')  # Patch re.match to pass the UUID validation
    def test_process_transcripts_to_file(self, mock_re_match, mock_log, mock_fetch):
        """Test process_transcripts function with file output"""
        # Setup mocks
        mock_fetch.return_value = "Test transcript content"
        mock_re_match.return_value = True  # Make the UUID validation pass
        
        # Patch open and os functions
        with patch('builtins.open', new_callable=mock_open) as mock_file, \
             patch('os.path.dirname') as mock_dirname, \
             patch('os.path.exists') as mock_exists:
                
            # Set up directory mocks
            mock_exists.return_value = True
            mock_dirname.return_value = "/fake/path"
            
            # Call the function with file output
            from vapi_transcripts import process_transcripts
            result = process_transcripts(
                "a37edc9f-852d-41b3-8601-801c20292716", 
                "test-api-key",
                output_file="test_output.md"
            )
            
            # Verify fetch_transcripts was called with the correct arguments
            mock_fetch.assert_called_once()
            
            # Since multiple files might be opened (for logging), check that our target file was opened correctly
            mock_file.assert_any_call("test_output.md", 'w', encoding='utf-8')
            
            # Check that the content was written
            handle = mock_file()
            handle.write.assert_any_call("Test transcript content")
            
            # Verify the result
            self.assertTrue(result)

# Additional tests to improve coverage
    @patch('vapi_transcripts.log')
    def test_run_with_venv(self, mock_log):
        """Test run_with_venv function"""
        with patch('subprocess.run') as mock_run:
            # Configure the mock
            mock_process = MagicMock()
            mock_process.returncode = 0
            mock_process.stdout = "Test output"
            mock_process.stderr = ""
            mock_run.return_value = mock_process
            
            # Call the function
            result = run_with_venv("test command")
            
            # Verify subprocess.run was called correctly
            mock_run.assert_called_once()
            args, kwargs = mock_run.call_args
            self.assertIn("source", args[0])
            self.assertIn("test command", args[0])
            
            # Verify result
            self.assertEqual(result, mock_process)
            
    @patch('vapi_transcripts.check_venv_setup')
    @patch('vapi_transcripts.check_api_key')
    @patch('vapi_transcripts.log')
    def test_setup_environment_success(self, mock_log, mock_check_api, mock_check_venv):
        """Test setup_environment function success path"""
        # Configure mocks
        mock_check_venv.return_value = True
        mock_check_api.return_value = "test-api-key"
        
        # Call the function
        from vapi_transcripts import setup_environment
        success, api_key = setup_environment()
        
        # Verify result
        self.assertTrue(success)
        self.assertEqual(api_key, "test-api-key")
        
    @patch('vapi_transcripts.check_venv_setup')
    @patch('vapi_transcripts.log')
    def test_setup_environment_venv_fail(self, mock_log, mock_check_venv):
        """Test setup_environment function when venv setup fails"""
        # Configure mock
        mock_check_venv.return_value = False
        
        # Call the function
        from vapi_transcripts import setup_environment
        success, api_key = setup_environment()
        
        # Verify result
        self.assertFalse(success)
        self.assertIsNone(api_key)
    @patch('os.path.exists')
    def test_check_api_key_no_env_file(self, mock_exists):
        """Test check_api_key function when .env file doesn't exist"""
        mock_exists.return_value = False
        
        api_key = check_api_key()
        
        self.assertIsNone(api_key)
        
    @patch('vapi_transcripts.get_foreground_tab_url')  
    @patch('vapi_transcripts.find_vapi_tabs')
    @patch('vapi_transcripts.log')
    @patch('vapi_transcripts.extract_assistant_id')
    def test_find_assistant_id_foreground(self, mock_extract, mock_log, mock_find_tabs, mock_foreground):
        """Test find_assistant_id function with foreground tab"""
        # Configure mocks
        mock_foreground.return_value = "https://dashboard.vapi.ai/calls?assistantId=a37edc9f-852d-41b3-8601-801c20292716"
        mock_extract.return_value = "a37edc9f-852d-41b3-8601-801c20292716"
        
        # Call function
        from vapi_transcripts import find_assistant_id
        result = find_assistant_id()
        
        # Verify result
        self.assertEqual(result, "a37edc9f-852d-41b3-8601-801c20292716")
        # Verify find_vapi_tabs wasn't called since foreground tab had an ID
        mock_find_tabs.assert_not_called()
        
    @patch('vapi_transcripts.get_foreground_tab_url')  
    @patch('vapi_transcripts.find_vapi_tabs')
    @patch('vapi_transcripts.log')
    @patch('vapi_transcripts.extract_assistant_id')
    def test_find_assistant_id_no_foreground(self, mock_extract, mock_log, mock_find_tabs, mock_foreground):
        """Test find_assistant_id function when foreground tab has no assistant ID"""
        # Configure mocks
        mock_foreground.return_value = "https://example.com"
        mock_extract.side_effect = [None, "a37edc9f-852d-41b3-8601-801c20292716"]
        mock_find_tabs.return_value = [
            ("https://dashboard.vapi.ai/calls?assistantId=a37edc9f-852d-41b3-8601-801c20292716", 
             "a37edc9f-852d-41b3-8601-801c20292716")
        ]
        
        # Call function
        from vapi_transcripts import find_assistant_id
        result = find_assistant_id()
        
        # Verify result
        self.assertEqual(result, "a37edc9f-852d-41b3-8601-801c20292716")
        # Verify find_vapi_tabs was called since foreground tab had no ID
        mock_find_tabs.assert_called_once()
        
    @patch('vapi_transcripts.get_foreground_tab_url')  
    @patch('vapi_transcripts.find_vapi_tabs')
    @patch('vapi_transcripts.log')
    @patch('vapi_transcripts.extract_assistant_id')
    def test_find_assistant_id_no_tabs(self, mock_extract, mock_log, mock_find_tabs, mock_foreground):
        """Test find_assistant_id function when no tabs have assistant IDs"""
        # Configure mocks
        mock_foreground.return_value = "https://example.com"
        mock_extract.return_value = None
        mock_find_tabs.return_value = []
        
        # Call function
        from vapi_transcripts import find_assistant_id
        result = find_assistant_id()
        
        # Verify result
        self.assertIsNone(result)
    
    @patch('vapi_transcripts.find_assistant_id')
    @patch('vapi_transcripts.setup_environment')
    @patch('vapi_transcripts.process_transcripts')
    @patch('vapi_transcripts.log')
    @patch('vapi_transcripts.parse_args')
    def test_main_success(self, mock_parse_args, mock_log, mock_process, mock_setup, mock_find):
        """Test main function success path"""
        # Configure mocks
        mock_parse_args.return_value = MagicMock(assistant_id=None, output=None, min_duration=0, 
                                                days=None, limit=None, today=False, no_paste=False)
        mock_setup.return_value = (True, "test-api-key")
        mock_find.return_value = "test-assistant-id"
        mock_process.return_value = True
        
        # Call main function
        from vapi_transcripts import main
        result = main()
        
        # Verify mocks were called correctly
        mock_setup.assert_called_once()
        mock_find.assert_called_once()
        mock_process.assert_called_once_with(
            "test-assistant-id", "test-api-key", 
            output_file=None, min_duration=0, days_ago=None, 
            limit=None, today_only=False, no_paste=False
        )
        
        # Verify result
        self.assertEqual(result, 0)
    
    @patch('vapi_transcripts.find_assistant_id')
    @patch('vapi_transcripts.setup_environment')
    @patch('vapi_transcripts.log')
    @patch('vapi_transcripts.parse_args')
    def test_main_no_assistant_id(self, mock_parse_args, mock_log, mock_setup, mock_find):
        """Test main function when no assistant ID is found"""
        # Configure mocks
        mock_parse_args.return_value = MagicMock(assistant_id=None)
        mock_setup.return_value = (True, "test-api-key")
        mock_find.return_value = None
        
        # Call main function
        from vapi_transcripts import main
        result = main()
        
        # Verify result
        self.assertEqual(result, 1)
    
    @patch('vapi_transcripts.log')
    @patch('vapi_transcripts.parse_args')
    @patch('vapi_transcripts.setup_environment')
    def test_main_setup_fails(self, mock_setup, mock_parse_args, mock_log):
        """Test main function when environment setup fails"""
        # Configure mocks
        mock_parse_args.return_value = MagicMock()
        mock_setup.return_value = (False, None)
        
        # Call main function
        from vapi_transcripts import main
        result = main()
        
        # Verify result
        self.assertEqual(result, 1)

if __name__ == '__main__':
    unittest.main()