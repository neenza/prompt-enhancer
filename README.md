# Prompt Enhancer

A dark-themed tkinter application that enhances prompts using Google's Gemini API.

## Features

- Clean, dark minimal UI
- Input field for original prompts
- Enhanced prompt output
- Copy to clipboard functionality
- Real-time status updates
- Error handling and timeout protection

## Setup

1. Install the required dependencies:
   ```cmd
   pip install -r requirements.txt
   ```

2. Get a Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

3. Set your API key as an environment variable:
   ```cmd
   set GEMINI_API_KEY=your_api_key_here
   ```

4. Run the application:
   ```cmd
   python main.py
   ```

## Usage

1. Enter your prompt in the input field
2. Click "Enhance" to improve your prompt using Gemini AI
3. The enhanced prompt will appear in the output field
4. Use "Copy Enhanced Prompt" to copy the result to clipboard
5. Use "Clear" to reset both input and output fields

## Requirements

- Python 3.6+
- tkinter (usually included with Python)
- requests
- Valid Gemini API key
