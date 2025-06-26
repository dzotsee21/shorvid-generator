from .utils import random_filename
from moviepy import TextClip, CompositeVideoClip, AudioFileClip, VideoFileClip, CompositeAudioClip, ImageClip, afx
from PIL import Image, ImageOps
import glob
import os


def create_character_clip(start, end, position, char_name='Yui', flip=False):
    original_path = f'static/characters/{char_name}.png'
    flipped_path = f'static/characters/flipped_characters/{char_name}_flipped.png'

    path = original_path
    if flip:
        if not os.path.exists(flipped_path):
            image = Image.open(original_path)
            mirrored = ImageOps.mirror(image)
            mirrored.save(flipped_path)
        path = flipped_path
    
    clip = ImageClip(path) \
        .with_start(start) \
        .with_end(end) \
        .resized(height=700) \
        .with_position(position)
    
    return clip

def pop_in_word(word_text, start_time, end_time, color='white'):
    base_font_size = 80
    duration = end_time-start_time

    txt = TextClip(
        text=word_text,
        size=(800, 200),
        font_size=base_font_size,
        font='static/fonts/Rubik-Black.ttf',
        color=color,
        stroke_color='black',
        stroke_width=2,
        method='caption',
    ).with_start(start_time).with_duration(duration).with_position('center')

    def scaling(t):
        duration = 0.07
        if t < duration:
            return 0.5 + (1.0 - 0.5) * (t / duration)
        return 1

    txt = txt.resized(scaling)

    return txt

def edit(subtitles, chunked_text, music_path, background_path, color1, char_name1, color2=None, char_name2=None, has_images=False, has_character=False, character_apper_durations=None, gen_type='monologue'):
    if gen_type == 'monologue':
        audio = AudioFileClip('static/temp/out.wav')
    else:
        audio = AudioFileClip('static/temp/combined_out.wav')

    duration = audio.duration

    background = VideoFileClip(f"static/background_videos/{background_path}").subclipped(0, duration).resized((1080, 1920))

    bg_music = AudioFileClip(f'static/musics/{music_path}')
    bg_music = bg_music.subclipped(0, audio.duration)
    bg_music = bg_music.with_effects([afx.MultiplyVolume(0.05)])


    additional_images_clips = []
    if has_images:
        for idx, chunk in enumerate(chunked_text):
            try:
                start = chunk['start']
                end = chunk['end']
                position = ('center', 100)

                image_file = glob.glob(f"static/temp/fetched_images/image_{idx+1}.*")
            
                if not image_file:
                    continue

                image_path = image_file[0]

                image_clip = ImageClip(image_path) \
                    .with_start(start) \
                    .with_end(end) \
                    .resized(height=500, width=500) \
                    .with_position(position)

                os.remove(image_path)
                
                additional_images_clips.append(image_clip)
            except:
                continue
    character_clips = []    
    if has_character:
        if gen_type=='monologue':
                for iter_i in range(2):
                    start = None
                    end = None
                    position = (None, None)
                    flip = False

                    if iter_i == 0:
                        start = 0
                        end = duration/2
                        position = ("right", "bottom")
                    elif iter_i == 1:
                        start = duration/2
                        end = duration
                        flip = True
                        position = ("left", "bottom")

                    character_clip = create_character_clip(start, end, position, char_name1, flip)
                    character_clips.append(character_clip)

        elif gen_type=='dialogue':
            for idx, dur_pos in enumerate(character_apper_durations):
                start = dur_pos[0]
                end = dur_pos[1]
                if idx % 2 == 1:
                    position = ("left", "bottom")
                    flip=True
                    char_name = char_name2
                else:
                    position = ("right", "bottom")
                    flip = False
                    char_name = char_name1

                character_clip = create_character_clip(start, end, position, char_name, flip)
                character_clips.append(character_clip)
        

    subtitle_clips = []

    if gen_type=='monologue':
        for segment in subtitles:
            for word in segment['words']:
                word_clip = pop_in_word(word['word'], word['start'], word['end'], color1)

                subtitle_clips.append(word_clip)

    elif gen_type=='dialogue':
        color = color1
        idx = 0
        start = character_apper_durations[idx][0]
        end = character_apper_durations[idx][1]

        for segment in subtitles:
            for word in segment['words']:
                word_start = word['start']
                word_end = word['end']

                if word_start > end:
                    idx += 1
                    if idx >= len(character_apper_durations):
                        idx = len(character_apper_durations) - 1
                    start = character_apper_durations[idx][0]
                    end = character_apper_durations[idx][1]

                color = color2 if idx % 2 == 1 else color1

                word_clip = pop_in_word(word['word'], word_start, word_end, color)

                subtitle_clips.append(word_clip)

    final = CompositeVideoClip([background, *additional_images_clips, *character_clips, *subtitle_clips])
    final_audio = CompositeAudioClip([bg_music, audio])
    final = final.with_audio(final_audio)



    folder_length = len(os.listdir('static/temp/videos'))
    filename = random_filename(folder_length)
    final.write_videofile(f'static/temp/videos/video{filename}.mp4', fps=24)