import re
import ast
import random

def format_timestamp(seconds: float) -> str:
    minutes = int(seconds // 60)
    secs = seconds % 60
    return f"{minutes:02}:{secs:06.3f}"

def parse_timestamp(ts):
    minutes, seconds = ts.split(":")
    return int(minutes) * 60 + float(seconds)

def clean_word_data(raw):
    raw = re.sub(r'np\.float64\(([\d.]+)\)', r'\1', raw)
    return ast.literal_eval(raw)

def random_filename(len):
    chars = ['a', 'b', 'c', 'd', 'e', 'f']
    random.shuffle(chars)
    rslt = ''
    for _ in range(2):
        char = random.choice(chars)
        rslt += char
    rslt += f'_{len}'
    return rslt 