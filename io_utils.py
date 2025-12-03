import os
from models import Melody


def save_melody_as_midi(melody: Melody, filename: str):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    s = melody.to_music21_stream()
    s.write('midi', fp=filename)
    print(f"MIDI文件已保存: {filename}")


def save_melody_as_musicxml(melody: Melody, filename: str):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    s = melody.to_music21_stream()
    s.write('musicxml', fp=filename)
    print(f"MusicXML文件已保存: {filename}")

