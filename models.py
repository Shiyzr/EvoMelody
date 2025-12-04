from typing import List
 


class Note:
    """
    音符类：用三个参数刻画一个音符
    """
    def __init__(self, octave: int, pitch: int, duration: float):
        """
        octave: 八度，范围3-5
        pitch: 音高(0-12)，0=休止，1-12表示C到B（1=C, 12=B）
        duration: 持续时间(四分音符为单位)，0.5=八分音符, 1=四分音符, 2=二分音符, 4=全音符
        """
        self.octave = octave
        self.pitch = pitch
        self.duration = duration
    
    def __repr__(self):
        pitch_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        if self.pitch == 0:
            return f"R({self.duration})"
        idx = max(1, min(12, self.pitch)) - 1
        return f"{pitch_names[idx]}{self.octave}({self.duration})"
    
    def to_music21_note(self):
        """转换为music21的Note/Rest对象"""
        from music21 import note
        duration_value = self.duration
        if self.pitch == 0:
            return note.Rest(quarterLength=duration_value)
        pitch_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        idx = max(1, min(12, self.pitch)) - 1
        pitch_str = f"{pitch_names[idx]}{self.octave}"
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
        from music21 import stream, meter, tempo
        s = stream.Stream()
        s.append(meter.TimeSignature('4/4'))
        s.append(tempo.MetronomeMark(number=120))
        for n in self.notes:
            s.append(n.to_music21_note())
        return s

