# Shorvid Generator

**A highly customizable short-form (brainrot) video generator.**  
Create dynamic, meme-style videos with your own characters, background music, voices, fonts, and even auto-generated, context-relevant images.

## Generated video examples
https://github.com/user-attachments/assets/9822470a-cbad-4848-b7bd-66891ef280f0

## Features
- Automatically displays context-based images
- Generate dialogues between any two characters you choose
- Supports both [ElevenLabs](https://elevenlabs.io) (freemium) and [Edge-TTS](https://learn.microsoft.com/en-us/azure/cognitive-services/speech-service/tts-overview) (completely free)

## Installation
 Use Python 3.10 or lower in your virtual environment, newer versions might break the install.
```bash
git clone https://github.com/dzotsee21/shorvid-generator.git
cd shorvid-generator
pip install -r requirements.txt
python app.py
```
Done!

## Configuration
To change characters, voices, TTS models, font colors, or other settings, edit the config.yaml file directly.
