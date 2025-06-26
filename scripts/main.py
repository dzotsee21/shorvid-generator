from .voice_generator import text_to_speech
from .transcriber import transcribe, create_subtitles
from .editor import edit
import yaml
import re

with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

# initialize values
tts_model = config['tts-model']
subtitles_color1 = config['character-1-subtitles-color']
tts_voice_name_1 = None
tts_voice_name_2 = None
tts_voice_id_1 = None
tts_voice_id_2 = None

if tts_model == 'edge-tts':
    tts_voice_name_1 = config['tts-voice-name-1']
    if config['tts-voice-name-2']:
        subtitles_color2 = config['character-2-subtitles-color']
        tts_voice_name_2 = config['tts-voice-name-2']
else:
    tts_voice_id_1 = config['tts-voice-id-1']
    if config['tts-voice-id-2']:
        subtitles_color2 = config['character-2-subtitles-color']
        tts_voice_id_2 = config['tts-voice-id-2']

async def generate_monologue_video(text, has_character, has_images, music_path, background_path, character_name='Yui'):
    if (tts_model == 'edge-tts' and not tts_voice_name_1) or \
       (tts_model == 'eleven-labs' and not tts_voice_id_1):
        raise ValueError("Missing voices (make sure primary tts-voice id/name is set inside config.yaml file)")

    print("start tts...")
    if tts_model == 'edge-tts':
        await text_to_speech(
            text,
            'static/temp/out.wav', 
            voice_name=tts_voice_name_1, 
            model=tts_model
        )
    else:
        await text_to_speech(
            text,
            'static/temp/out.wav', 
            voice_id=tts_voice_id_1, 
            model=tts_model
        )

    print("start transcribing...")
    subtitles, chunked_text = transcribe(has_images)

    print("start creating subtitles...")
    subtitles = create_subtitles()

    print("start editing...")
    edit(
        subtitles=subtitles, 
        chunked_text=chunked_text, 
        music_path=music_path, 
        background_path=background_path, 
        color1=subtitles_color1, 
        char_name1=character_name, 
        has_images=has_images, 
        has_character=has_character
    )


async def generate_dialogue_video(text, has_character, character_name1, character_name2, music_path, background_path, has_images=False):
    dialogues = re.findall(r"(?m)^(.+?):\r?\n(.+?)(?=\r?\n\r?\n|\Z)", text)

    if (tts_model == 'edge-tts' and not tts_voice_name_1 and not tts_voice_name_2) or \
       (tts_model == 'eleven-labs' and not tts_voice_id_1 and not tts_voice_id_2):
        raise ValueError("Missing voices (make sure voice id/names are set inside config.yaml file)")

    for idx, (speaker, line) in enumerate(dialogues):
        if speaker==character_name1:
            voice = tts_voice_name_1 if tts_model == 'edge-tts' else tts_voice_id_1
        else:
            voice=tts_voice_name_2 if tts_model == 'edge-tts' else tts_voice_id_2

        if tts_model=='edge-tts':
            await text_to_speech(
                line,
                model=tts_model,
                voice_name=voice,
                file_path=f"static/temp/audio/out_{idx}.wav"
            )
        else:
            await text_to_speech(
                line,
                model=tts_model,
                voice_id=voice,
                file_path=f"static/temp/audio/out_{idx}.wav"
            )

    print("start transcribing...")
    subtitles, chunked_text, character_apper_durations = transcribe(has_images, gen_type='dialogue')

    print("start creating subtitles...")
    subtitles = create_subtitles()

    print("start editing...")
    edit(
        subtitles=subtitles, 
        chunked_text=chunked_text, 
        music_path=music_path, 
        background_path=background_path, 
        color1=subtitles_color1,
        color2=subtitles_color2,
        char_name1=character_name1, 
        char_name2=character_name2, 
        has_images=has_images, 
        has_character=has_character, 
        character_apper_durations=character_apper_durations, 
        gen_type='dialogue'
    )
    