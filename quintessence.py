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
        

def summarize_text(textfile, output_file):
    # Read content of textfile into string to later use as prompt
    with open(textfile, 'r') as f:
        transcript = f.read()

    # Prompt the model to summarize the text
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Du bist ein hilfreicher Assistent."},
            {"role": "user", "content": "Ich bin Student und habe die Vorlesung, von der das folgende Transkript stammt, verpasst. Könntest du mir eine Stichpunktartige, aber ausführliche Zusammenfassung von den vermittelten Inhalten und Konzepten erstellen, die ich als einzige Quelle nutzen kann um mich auf die Klausur vorzubereiten? Bitte formatiere deine Antwort mit Markdown und schließe die Zusammenfassung mit dem Punkt \"Organisatorisches\" ab, unter welchem du Inhalte des Transkripts nennst, die nicht unmittelbar mit der Vorlesungsthematik zu tun haben. Hier das Transkript: " + transcript}
        ]
    )

    # for each choice in the response, save the summary to a file
    for i in range(len(response.choices)):

        # Print to console for debugging and verification
        print(f"Choice {i+1}:")
        print(response.choices[i].message.content)
        print()

        with open(f"{output_file.replace('.txt', '')}_{i}.txt", 'w') as f:
            f.write(response.choices[i].message.content)




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

    summarize_text(args.transcript_file, args.summ_file)

if __name__ == '__main__':
    main()
