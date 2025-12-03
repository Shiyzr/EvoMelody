from typing import List
from music21 import stream, note, meter, tempo


class Note:
    """
    音符类：用三个参数刻画一个音符
    """
    def __init__(self, octave: int, pitch: int, duration: int):
        """
        octave: 八度，范围3-5
        pitch: 音高(0-11)，0=C, 1=C#, 2=D, 3=D#, 4=E, 5=F, 6=F#, 7=G, 8=G#, 9=A, 10=A#, 11=B
        duration: 持续时间(八分音符为单位)，1=八分音符, 2=四分音符, 4=二分音符
        """
        self.octave = octave
        self.pitch = pitch
        self.duration = duration
    
    def __repr__(self):
        pitch_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        return f"{pitch_names[self.pitch]}{self.octave}({self.duration})"
    
    def to_music21_note(self):
        """转换为music21的Note对象"""
        pitch_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        pitch_str = f"{pitch_names[self.pitch]}{self.octave}"
        duration_value = self.duration * 0.5
        return note.Note(pitch_str, quarterLength=duration_value)
    
    def copy(self):
        return Note(self.octave, self.pitch, self.duration)


class Melody:
    """
    旋律类：一个4小节的旋律，4/4拍
    """
    def __init__(self, notes: List[Note] = None):
        self.notes = notes if notes else []
        self.fitness = 0.0
    
    def __len__(self):
        return len(self.notes)
    
    def total_duration(self):
        return sum(n.duration for n in self.notes)
    
    def copy(self):
        return Melody([n.copy() for n in self.notes])
    
    def to_music21_stream(self):
        s = stream.Stream()
        s.append(meter.TimeSignature('4/4'))
        s.append(tempo.MetronomeMark(number=120))
        for n in self.notes:
            s.append(n.to_music21_note())
        return s

