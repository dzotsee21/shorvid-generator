from .utils import parse_timestamp, format_timestamp, clean_word_data
from .image_finder import google_search, download_images
import whisper
import subprocess
import sys
import re
import os
import spacy
from pydub import AudioSegment

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Model 'en_core_web_sm' not found. Downloading it...")
    subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"], check=True)
    nlp = spacy.load("en_core_web_sm")
model = whisper.load_model('base')

def extract_number(filename):
    match = re.search(r'out_(\d+)', filename)
    return int(match.group(1)) if match else -1


def concatenate_audio_from_folder(folder_path='static/temp/audio', output_file='static/temp/combined_out.wav'):
    file_paths = sorted([
        os.path.join(folder_path, f)
        for f in os.listdir(folder_path)
        if f.endswith('.wav')
    ], key=lambda f: extract_number(os.path.basename(f)))

    if not file_paths:
        print("No audio files found.")
        return

    combined = AudioSegment.empty()

    total_duration = 0
    character_appearence_durations = []
    for file_path in file_paths:
        print(f"Adding {file_path}")
        audio = AudioSegment.from_file(file_path)
        duration_sec = len(audio) / 1000
        character_appearence_durations.append((total_duration, total_duration+duration_sec))
        total_duration += duration_sec
        combined += audio
        os.remove(file_path)

    combined.export(output_file, format='wav')
    print(f"Saved to {output_file}")

    return character_appearence_durations


def transcribe(has_images, gen_type='monologue', filename='static/temp/out.wav'):
    if gen_type=='dialogue':
        character_apper_durations = concatenate_audio_from_folder()
        filename='static/temp/combined_out.wav'

    result = model.transcribe(filename, word_timestamps=True)

    chunked_text = ""
    if has_images:
        chunked_text, full_text = chunk_text(result)

        fetched_images = google_search(full_text)

        download_images(fetched_images)

    with open("static/temp/transcription.txt", "w", encoding="utf-8") as f:
        f.truncate()

    for segment in result["segments"]:
        words = segment['words']
        split_and_write_words(words)

    if gen_type=='monologue':
        return result["segments"], chunked_text
    else:
        return result["segments"], chunked_text, character_apper_durations


def split_and_write_words(words, max_words=5):
    for i in range(0, len(words), max_words):
        chunk = words[i:i+max_words]
        start = chunk[0]['start']
        end = chunk[-1]['end']
        text = ' '.join([w['word'].strip() for w in chunk])
        with open("static/temp/transcription.txt", "a", encoding="utf-8") as f:
            f.write(f"[{format_timestamp(start)} - {format_timestamp(end)}] {text} - {chunk}\n")



def chunk_text(transcribed_text, min_len=20):
    text = transcribed_text['text']

    doc = nlp(text)
    chunks = []
    current_chunk = ""
    chunk_start = None
    chunk_end = None
    prev_point = 0

    words = []
    for segment in transcribed_text.get('segments', []):
        words.extend(segment.get('words', []))

    full_text = ""
    for sent in doc.sents:
        sentence = sent.text.strip()
        sent_len = len(sentence)

        sent_word_length = len(sentence.split(" "))
        sent_words = words[prev_point:prev_point+sent_word_length]

        if not sent_words:
            continue

        prev_point += sent_word_length

        if sent_word_length < 3:
            continue

        full_text += sentence + " [] "

        start = sent_words[0]['start']
        end = sent_words[-1]['end']

        if len(current_chunk) + sent_len < min_len:
            if not current_chunk:
                chunk_start = start
            current_chunk += " " + sentence
            chunk_end = end
        else:
            if current_chunk:
                chunks.append({
                    'text': current_chunk.strip(),
                    'start': chunk_start,
                    'end': chunk_end
                })
                current_chunk = ""
                chunk_start = None
                chunk_end = None
            
            chunks.append({
                'text': sentence,
                'start': start,
                'end': end
            })

    print(full_text)
    return chunks, full_text

def create_subtitles():
    with open("static/temp/transcription.txt", "r", encoding="utf-8") as f:
        transcript = f.read()

    subtitles = []
    for transcript_line in transcript.split("\n"):
        try:
            words_match = re.search(r"\[(.*?) - (.*?)\] (.*?) - (.+)", transcript_line)
            start_time = parse_timestamp(words_match.group(1))
            end_time = parse_timestamp(words_match.group(2))
            text = words_match.group(3).strip()
            words_raw = words_match.group(4).strip()

            words = clean_word_data(words_raw)

            subtitles_obj = {
                "start": start_time,
                "end": end_time,
                "text": text,
                "words": words
            }
            
            subtitles.append(subtitles_obj)
        except Exception as e:
            print(e)

    return subtitles
