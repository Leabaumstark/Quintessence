# Quintessence
Python tool to summarize lecture videos

## How it works
Input a mp4 video file and specify the path and filename of the summary to be created. Quintessence will then isolate the audio, transcribe it to a textfile, and prompt gpt-4o-mini to summarize the content.

The prompt used is currently hardcoded, plan is to make it configurable more easily in the future. You can however change the prompt in the code directly.

## Limitations
Currently only returns summaries in english. 

## Prerequisites
For the OpenAI API requests to work, you need to add your personal OpenAI API key to your environment variables.
You also have to enable billing and make sure, that your OpenAI credit balance is high enough.

**CAUTION:**

The OpenAI API requests done by this script **cost money**. Usually it's <50ct. You will, however, have to add billing information to your OpenAI account. Please get informed about the conditions, I do not take responsibility for any amount of money OpenAI will charge you. 

**Note:**

This script was written before chatGPT also directly took mp4 files as an input. Using chatGPT directly for this purpose may be beneficial now regarding pricing.
