# Known Bugs and Issues

## Tab Detection Issues

### Non-Focused VAPI Tab Not Detected

**Description:** When a VAPI dashboard tab is open but not in focus, the script sometimes fails to detect it with the message "Looking for VAPI assistant tabs in Chrome..." followed by "No VAPI assistant tabs found".

**Steps to Reproduce:**
1. Open Chrome with multiple tabs
2. Open a VAPI dashboard tab with an assistant ID in the URL
3. Switch to a different tab (so the VAPI tab is not in focus)
4. Run the script

**Expected Behavior:** The script should detect the VAPI tab even when it's not in focus.

**Actual Behavior:** The script displays "Looking for VAPI assistant tabs in Chrome..." and then "No VAPI assistant tabs found".

**Potential Fix:**
1. Improve the URL pattern matching in `find_vapi_tabs` to recognize more VAPI URL formats
2. Add better logging to understand which URLs are being found but not recognized
3. Consider adding additional URL patterns to the `extract_assistant_id` function

## Suggested Improvements

### Better URL Pattern Recognition

The current tab detection in `find_vapi_tabs` uses a simple string search:

```python
vapi_dashboard_tabs = [url for url in all_tabs if 'vapi' in url.lower() or 'dashboard' in url.lower()]
```

This might miss certain URL formats or new dashboard URLs. Consider expanding this to:

```python
vapi_dashboard_tabs = [url for url in all_tabs 
                       if ('vapi' in url.lower() or 
                           'dashboard' in url.lower() or 
                           'calls' in url.lower() or
                           'assistant' in url.lower())]
```

### Log Full Tab URLs

For better debugging, consider updating the log in `find_vapi_tabs` to show all found URLs:

```python
log(f"All tabs: {all_tabs}")
log(f"Potential VAPI tabs: {vapi_dashboard_tabs}")
```

This would help identify why certain tabs aren't being recognized properly.

### Error Reports

Please report any additional bugs or issues by opening an issue on GitHub: https://github.com/culstrup/vapi-tools/issues