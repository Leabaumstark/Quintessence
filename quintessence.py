from moviepy.editor import *
from openai import OpenAI
import argparse
from pydub import AudioSegment


def mp4_to_mp3(mp4file, mp3file):
    videoclip = VideoFileClip(mp4file)
    audioclip = videoclip.audio
    audioclip.write_audiofile(mp3file)
    audioclip.close()
    videoclip.close()

def speech_to_text(mp3file, textfile):

    # If textfile does not exist, create it
    if not os.path.exists(textfile):
        with open(textfile, 'w') as f:
            f.write('')

    # Read content of textfile into string to later use as prompt
    with open(textfile, 'r') as f:
        prevTranscript = f.read()

    # Transcribe audio file
    client = OpenAI()
    audio_file = open(mp3file, 'rb')
    transcription = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        prompt=prevTranscript
    )

    # if textfile does not exist yet, create it, then append the transcription
    with open(textfile, 'a') as f:
        f.write(transcription.text + ' ')
    audio_file.close()


def promptGPT(transcript):
    # Prompt the model to summarize the text
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
        {"role": "system", "content": "You are an AI tutor that helps students to summarize lecture transcripts."},
            {"role": "user", "content": "The central statements from the following transcript of a lecture are to be summarized in a Markdown file. To do this, first extract all core statements from the transcript. If necessary, convert mathematical expressions from natural language into mathematical terms. Then estimate the relevance of the core statements with regard to the criteria \“Understanding this core statement is a prerequisite for understanding other core statements in the transcript\”, \“Understanding this core statement is a prerequisite for understanding related topics\”, \"Knowledge of this core statement could easily be tested in a written exam\” \“This key statement refers to the procedure, organization, tools, content or similar information for the upcoming exam\”. Keep all key statements that fulfill at least one of the above criteria. Then group the key statements by topic and, if appropriate, by subtopic. To create the content of the resulting Markdown file, first create a heading for each topic, such as \“# Test\” for the topic \“Test\”, and for each subtopic a heading subordinate to the heading, such as \“## Subtopic\”, arranged \“# Test\\n## Subtopic\”, for the subtopic \“Subtopic\” of the topic \“Test\”. Then arrange the core statements under the corresponding headings as bullet points, whereby bullet points are identified in Markdown syntax by a leading \“- \”. Here is the transcript: " + transcript}
        ]
    )
    return response
        

def summarize_text(textfile, output_file):
    # Read content of textfile into string to later use as prompt
    with open(textfile, 'r') as f:
        transcript = f.read()

    
    # check if summary is too long (more than ~50000 chars)
    # if it is, split the summary into multiple files
    # and process each separately
    if len(transcript) >= 50000:
        # Split transcript into 20000 char chunks
        transcript_chunks = [transcript[i:i+40000] for i in range(0, len(transcript), 40000)]
        for i, chunk in enumerate(transcript_chunks):
            print(f"Processing transcript chunk {i}")
            response = promptGPT(chunk)
            
            # append first choice of response to output file
            with open(output_file, 'a') as f:
                f.write("\n\n")
                f.write("-------------------------------------------------------------\n")
                f.write("Zusammenfassung Teil " + str(i+1) + "\n")
                f.write("-------------------------------------------------------------\n\n")

                f.write(response.choices[0].message.content + ' ')

    else:
        response = promptGPT(transcript) 
        # append first choice of response to output file
        with open(output_file, 'a') as f:
            f.write(response.choices[0].message.content + ' ')



def main():
    parser = argparse.ArgumentParser(description='Quintessence - Convert video to text')
    parser.add_argument('-i', dest='video_file', help='input file, has to be mp4 video file', required=True)
    parser.add_argument('-t', dest='transcript_file', help='transcript output file name', required=True)
    parser.add_argument('-o', dest='summ_file', help='output summary file name', required=True)
    args = parser.parse_args()

    # Check all arguments for right suffix
    # If not, raise an error
    if not args.video_file.endswith('.mp4'):
        raise ValueError('Input file has to be a mp4 video file')
    if not args.transcript_file.endswith('.txt'):
        raise ValueError('Transcript output file has to be a txt file')
    if not args.summ_file.endswith('.txt'):
        raise ValueError('Summary output file has to be a txt file')
     
    # Convert mp4 file to mp3 file
    mp3file = args.video_file.replace('.mp4', '.mp3')
    mp4_to_mp3(args.video_file, mp3file)

    # Check if mp3 file size exceeds 25MB
    # If it does, split the mp3 file into smaller chunks
    # and process each chunk separately
    mp3file_size = os.path.getsize(mp3file)
    if mp3file_size >= 25000000:
        # Split mp3 file in 10min chunks
        audio = AudioSegment.from_file(mp3file, format="mp3")
        audio_chunks = audio[::600000]
        for i, chunk in enumerate(audio_chunks):
            chunk.export(f"{mp3file.replace('.mp3', '')}_{i}.mp3", format="mp3")
            print(f"Processing chunk {i}")

            # Transcribe each chunk
            speech_to_text(f"{mp3file.replace('.mp3', '')}_{i}.mp3", args.transcript_file)

            # Remove chunk after processing
            os.remove(f"{mp3file.replace('.mp3', '')}_{i}.mp3")
    else:
        # Transcribe the mp3 file
        speech_to_text(mp3file, args.transcript_file)

    # remove mp3 file after processing
    os.remove(mp3file)

    # Summarize the transcript
    summarize_text(args.transcript_file, args.summ_file)

if __name__ == '__main__':
    main()
