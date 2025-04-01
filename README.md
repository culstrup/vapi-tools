# VAPI Tools

A Raycast script for quickly extracting and analyzing transcripts from [VAPI](https://vapi.ai) (Voice API) voice assistant calls.

## Overview

VAPI is great for handling intake across many different use cases, but it's often useful to aggregate the call transcripts for analysis in your AI assistant of choice. This script dramatically reduces the number of clicks needed to extract transcripts - with a Raycast keyboard shortcut, you can pull all the transcripts from a specific assistant in seconds.

This tool is especially useful when you've collected feedback or information using multiple bespoke VAPI assistants and want to perform deeper analysis with a more powerful model like Claude or ChatGPT. By reducing the extraction process to a single keyboard shortcut, you can spend more time on analysis and less time on data collection.

### Use Cases

- **Inbound lead intake analysis**
- **Candidate screening calls** at the beginning of the hiring process
- **Employee check-ins**
- **Client workshop preparation** - analyze attendee calls to know where to focus and who to invite on stage
- **Customer feedback aggregation**
- And many more!

## How It Works

1. You navigate to the VAPI dashboard and filter calls for the assistant you want to analyze
2. Run the script via Raycast (or command line)
3. The script automatically extracts the assistant ID from your Chrome tab
4. All transcripts for that assistant are copied to your clipboard and pasted where your cursor is
5. Analyze the aggregated transcripts in your tool of choice (Claude, ChatGPT, etc.)

## Setup

### Prerequisites

- Python 3.9+
- Operating System:
  - macOS (full clipboard and paste functionality)
  - Linux (limited clipboard support, requires xclip or xsel for copying)
  - Windows (limited clipboard support, requires pywin32 or clip.exe for copying)
- Google Chrome
- VAPI API key
- [Raycast](https://raycast.com) (for Raycast integration, macOS only)

### Installation

1. Clone this repository:
```
git clone https://github.com/culstrup/vapi-tools.git
cd vapi-tools
```

2. Create a virtual environment and install dependencies:
```
python3 -m venv venv
source venv/bin/activate
pip install vapi_server_sdk
```

3. Create a `.env` file in the repository root with your VAPI API key:
```
VAPI_API_KEY=your_vapi_api_key_here
```

### Raycast Setup

1. Open Raycast
2. Go to Extensions → Script Commands
3. Click "Add Directories"
4. Select the `vapi-tools` directory 
5. The "VAPI: Extract Voice Call Transcripts" command should now appear in Raycast
6. Optionally, set a keyboard shortcut for quick access

## Usage

### Performance Tips

- **First Run**: The first run after restarting your computer may take 30-60 seconds as it sets up the virtual environment and SDK
- **Subsequent Runs**: After the initial run, the script will be much faster (typically 2-4 seconds)
- **Preload Environment**: For fastest performance, run the included preload script once in Terminal before using Raycast:
  ```
  ./scripts/preload_env.sh
  ```
- **Troubleshooting Slow Performance**: If the script is consistently slow, check the log file at `vapi_transcript_debug.log` for details

### Raycast Usage

1. Open Chrome to a VAPI dashboard page containing an assistantId in the URL
   (e.g., `https://dashboard.vapi.ai/calls?assistantId=your_assistant_id`)
2. Position your cursor where you want the transcripts to be pasted
3. Run the "VAPI: Extract Voice Call Transcripts" command from Raycast (or use your keyboard shortcut)
4. The script will automatically find the assistant ID from your Chrome tab, extract all transcripts, copy them to your clipboard, and paste them where your cursor is

### Step-by-Step Guide with Screenshots

#### 1. Set Up the Environment File

Create a `.env` file in the repository root and add your VAPI API key:

![Environment File Setup](https://github.com/culstrup/vapi-tools/raw/main/screenshots/env_setup.png)

*Create a .env file with your VAPI API key*

#### 2. Configure Raycast

Open Raycast preferences (Command+,), go to Extensions > Script Commands, and click "Add Directories" to add the project directory:

![Raycast Configuration](https://github.com/culstrup/vapi-tools/raw/main/screenshots/raycast_config.png)

*Add the project directory to Raycast*

#### 3. Preload the Environment

Run the preload script to make future commands run faster:

![Preload Environment](https://github.com/culstrup/vapi-tools/raw/main/screenshots/preload_env.png)

*Run the preload_env.sh script for faster performance*

#### 4. Filter VAPI Dashboard by Assistant

Go to the VAPI dashboard, open call logs, and filter by the assistant you want:

![VAPI Dashboard](https://github.com/culstrup/vapi-tools/raw/main/screenshots/vapi_dashboard.png)

*Filter the VAPI dashboard by specific assistant*

#### 5. Run Command and Use the Data

Open Raycast, run the "VAPI: Extract Voice Call Transcripts" command, and the transcripts will be copied to your clipboard and pasted where your cursor is:

![Transcript Output](https://github.com/culstrup/vapi-tools/raw/main/screenshots/transcript_output.png)

*Example of extracted transcripts in a text file*

#### Pro Tip
Place your cursor in a text file and run the command - it works great with the ChatGPT app, which can see the text file content for analysis.

### Command-Line Usage

You can also run the script directly from the command line with additional options:

```
python vapi_transcripts.py [options]
```

#### Command-Line Options

```
usage: vapi_transcripts.py [-h] [-a ASSISTANT_ID] [-o OUTPUT] [--no-paste]
                          [-d MIN_DURATION] [--days DAYS] [--today]
                          [-l LIMIT]

Extract transcripts from VAPI voice assistant calls

optional arguments:
  -h, --help            Show this help message and exit
  -a ASSISTANT_ID, --assistant-id ASSISTANT_ID
                        VAPI assistant ID to fetch transcripts for
  -o OUTPUT, --output OUTPUT
                        Save transcripts to the specified file instead of clipboard
  --no-paste            Don't paste clipboard content automatically (default is to paste)
  -d MIN_DURATION, --min-duration MIN_DURATION
                        Minimum call duration in seconds (default: 0, includes all calls)
  --days DAYS           Only include calls from the last N days
  --today               Only include calls from today
  -l LIMIT, --limit LIMIT
                        Maximum number of calls to include
```

#### Command-Line Examples

Extract transcripts from a specific assistant ID and copy to clipboard:
```
python vapi_transcripts.py --assistant-id a37edc9f-852d-41b3-8601-801c20292716
```

Extract transcripts from Chrome tabs and save to a file:
```
python vapi_transcripts.py --output transcripts.md
```

Extract only calls from today with a minimum duration of 60 seconds:
```
python vapi_transcripts.py --today --min-duration 60
```

Extract calls from the last 7 days and limit to the 5 most recent:
```
python vapi_transcripts.py --days 7 --limit 5
```

#### Assistant ID Detection

The script automatically detects the assistant ID from your Chrome tabs:
1. It first checks the foreground tab in Chrome for a VAPI dashboard URL with an assistant ID
2. If not found, it searches all open Chrome tabs for VAPI dashboard URLs

For best results, have the VAPI dashboard page open in Chrome before running the script. This ensures the script gets the correct assistant ID for the transcripts you want to extract. You must have a Chrome tab open with the VAPI dashboard for the script to work automatically.

## Development

### Running Tests

```
pytest tests/
```

Or with coverage:

```
pytest --cov=. tests/
```

### Project Structure

- `vapi_transcripts.py` - Main script for transcript extraction
- `tests/` - Unit and integration tests

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Blog Post

This tool is featured in a blog post collaboration with VAPI. Read more about how this tool was created and how it can be used for efficient voice assistant data collection and analysis in the VAPI blog post: [Scaling Client Intake Engine with VAPI Voice AI Agents](https://vapi.ai/blog/scaling-client-intake-engine-with-vapi-voice-ai-agents).

## About the Author

This tool was created by [Christian Ulstrup](https://github.com/culstrup), founder of [GSD at Work](https://gsdat.work), a consultancy that helps visionary leaders, founders, and enterprise executives accelerate AI adoption. GSD at Work focuses on helping clients become more productive and energized while serving customers better through the prudent use of AI as a complement to high-quality human labor and interaction.

## Acknowledgements

- [VAPI](https://vapi.ai) for their excellent voice assistant API and collaboration on the blog post
- [Raycast](https://raycast.com) for the extensible command platform
- [GSD at Work](https://gsdat.work) for supporting the development and open-sourcing of this tool