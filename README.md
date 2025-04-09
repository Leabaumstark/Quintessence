# Quintessence
Python tool to summarize lecture videos

## Limitations
Currently only returns summaries in german. 

## Prerequisites
For the OpenAI API requests to work, you need to add your personal OpenAI API key to your environment variables.
You also have to enable billing and make sure, that your OpenAI credit balance is high enough.

**CAUTION:**

The OpenAI API requests done by this script **cost money**. Usually it's <50ct. You will, however, have to add billing information to your OpenAI account. Please get informed about the conditions, I do not take responsibility for any amount of money OpenAI will charge you. 

Also, the following python packages are required:
- moviepy
- openai
- argparse
- pydub
