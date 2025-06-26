import edge_tts
from elevenlabs.client import ElevenLabs
from elevenlabs import save
import os

elevenlabs = ElevenLabs(
  api_key=os.environ.get("ELEVENLABS_API_KEY"),
)


async def text_to_speech(text, file_path, voice_id='Xb7hH8MSUJpSbSDYk0k2', voice_name='en-US-AvaMultilingualNeural', model='eleven-labs'):

    if model=='eleven-labs':
        audio = elevenlabs.text_to_speech.convert(
            text=text,
            voice_id=voice_id,
            model_id="eleven_multilingual_v2",
        )

        save(audio, file_path)
    elif model=='edge-tts':
        audio = edge_tts.Communicate(
            text=text,
            voice=voice_name
        )
        await audio.save(file_path)

    with open("static/temp/text.txt", "w", encoding="utf-8") as f:
        f.truncate()
    with open("static/temp/text.txt", "a", encoding="utf-8") as f:
        f.write(text)
