from flask import Flask, render_template, request, redirect, url_for
from scripts import main, publish_videos
import asyncio
import os

app = Flask(__name__)

app.config['SECRET_KEY'] = "Jknvfk805034bnf58034jngfj034gnjr"

@app.route("/", methods=['GET', 'POST'])
def monologue_generator():
    if request.method == 'POST':
        if 'generate' in request.form:
            char_name = request.form.get('character')
            user_text = request.form.get('script')
            background_path = request.form.get('background')
            music_path = request.form.get('music')
            has_character = bool(request.form.get('character'))
            has_images = bool(request.form.get('images'))

            asyncio.run(main.generate_monologue_video(user_text, has_character, has_images, music_path, background_path, character_name=char_name))

            return redirect(url_for('monologue_generator'))

    # make folder if it doesn't exist
    if not os.path.exists('static/musics'):
        os.makedirs('static/musics')
    music_files = os.listdir('static/musics')

    if not os.path.exists('static/background_videos'):
        os.makedirs('static/background_videos')
    background_files = os.listdir('static/background_videos')

    if not os.path.exists('static/temp/videos'):
        os.makedirs('static/temp/videos')
    video_files = os.listdir('static/temp/videos')

    return render_template('monologue_generate.html', music_files=music_files, background_files=background_files, videos_path=video_files)


@app.route("/dialogue_content", methods=['GET', 'POST'])
def dialogue_generator():
    if request.method == 'POST':
        if 'generate' in request.form:
            char_name1 = request.form.get('character_1')
            char_name2 = request.form.get('character_2')
            user_text = request.form.get('script')
            background_path = request.form.get('background')
            music_path = request.form.get('music')
            has_character = bool(request.form.get('character'))

            asyncio.run(main.generate_dialogue_video(user_text, has_character, char_name1, char_name2, music_path, background_path))

            return redirect(url_for('dialogue_generator'))
        
    music_files = os.listdir('static/musics')
    background_files = os.listdir('static/background_videos')
    video_files = os.listdir('static/temp/videos')

    return render_template('duo_generate.html', music_files=music_files, background_files=background_files, videos_path=video_files, dialogue=True)

@app.route("/upload_video/<video_path>", methods=['GET', 'POST'])
def upload_video(video_path):
    if request.method == 'POST':
        if 'publish' in request.form:
            title = request.form.get('title')
            description = request.form.get('description')
            tags = request.form.get('tags').split(" ")

            youtube = publish_videos.authenticate_youtube()
            video_path = request.form.get('video_path')
            publish_videos.upload_video(
                youtube,
                video_path,
                title,
                description,
                tags
                )
            
            os.remove(f'static/temp/videos/{video_path}')
            return redirect(url_for('monologue_generator'))
        elif 'remove' in request.form:
            os.remove(f'static/temp/videos/{video_path}')
            return redirect(url_for('monologue_generator'))

    return render_template('publish.html', video_path=video_path)


if __name__ == '__main__':
    app.run(debug=True)