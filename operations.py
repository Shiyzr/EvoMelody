import random
import json
import os
from typing import List, Tuple

from models import Melody, Note


def generate_random_melody(bars: int = 4, rest_probability: float = 0.15) -> Melody:
    """
    随机生成一个旋律
    bars: 小节数
    """
    available_pitches = []
    for pitch in range(6, 13):
        available_pitches.append((3, pitch))
    for pitch in range(1, 13):
        available_pitches.append((4, pitch))
    for pitch in range(1, 9):
        available_pitches.append((5, pitch))
    target_duration = bars * 4
    notes = []
    current_duration = 0
    durations = [0.5, 1, 2, 4]
    while current_duration < target_duration:
        remaining = target_duration - current_duration
        valid_durations = [d for d in durations if d <= remaining]
        if not valid_durations:
            valid_durations = [1]
        duration = random.choice(valid_durations)
        if random.random() < rest_probability:
            notes.append(Note(4, 0, duration))
        else:
            octave, pitch = random.choice(available_pitches)
            notes.append(Note(octave, pitch, duration))
        current_duration += duration
    return Melody(notes)


def generate_initial_population(size: int = 15) -> List[Melody]:
    path = os.path.join('input', 'initial_population.json')
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    loaded: List[Melody] = []
    for item in data:
        notes = [Note(int(n[0]), int(n[1]), float(n[2])) for n in item.get('notes', [])]
        melody = Melody(notes)
        # print(f"原始旋律长度: {melody.total_duration()}")
        # from io_utils import save_melody_as_midi
        # save_melody_as_midi(melody, f"output/initial_population/{item['name']}.mid")
        melody = _adjust_melody_length(melody)
        loaded.append(melody)
    if size is None or size <= 0:
        return loaded
    if len(loaded) >= size:
        return loaded[:size]
    population = list(loaded)
    while len(population) < size and loaded:
        population.append(random.choice(loaded).copy())
    return population


def crossover(parent1: Melody, parent2: Melody) -> Tuple[Melody, Melody]:
    if len(parent1.notes) < 2 or len(parent2.notes) < 2:
        return parent1.copy(), parent2.copy()
    point1 = random.randint(1, len(parent1.notes) - 1)
    point2 = random.randint(1, len(parent2.notes) - 1)
    child1_notes = parent1.notes[:point1] + parent2.notes[point2:]
    child2_notes = parent2.notes[:point2] + parent1.notes[point1:]
    child1 = Melody(child1_notes)
    child2 = Melody(child2_notes)
    child1 = _adjust_melody_length(child1)
    child2 = _adjust_melody_length(child2)
    return child1, child2


def mutate(melody: Melody, mutation_rate: float = 0.2) -> Melody:
    mutated = melody.copy()
    for i in range(len(mutated.notes)):
        if random.random() < mutation_rate:
            n = mutated.notes[i]
            mutation_type = random.choice(['pitch', 'octave', 'duration'])
            if mutation_type == 'pitch':
                delta = random.randint(-2, 2)
                if n.pitch == 0:
                    n.pitch = random.randint(1, 12)
                else:
                    base = n.pitch - 1
                    new_pitch_index = (base + delta) % 12
                    n.pitch = new_pitch_index + 1
            elif mutation_type == 'octave':
                delta = random.choice([-1, 1])
                new_octave = n.octave + delta
                n.octave = max(3, min(5, new_octave))
            elif mutation_type == 'duration':
                durations = [0.5, 1, 2, 4]
                n.duration = random.choice(durations)
    mutated = _adjust_melody_length(mutated)
    return mutated


def transpose(melody: Melody, semitones: int) -> Melody:
    transposed = melody.copy()
    for n in transposed.notes:
        if n.pitch == 0:
            continue
        base = n.pitch - 1
        total_pitch = n.octave * 12 + base + semitones
        n.octave = total_pitch // 12
        new_class = total_pitch % 12
        n.pitch = new_class + 1
        if n.octave < 3:
            n.octave = 3
        elif n.octave > 5:
            n.octave = 5
    return transposed


def inversion(melody: Melody) -> Melody:
    if not melody.notes:
        return melody.copy()
    inverted = melody.copy()
    first_note = None
    for n in melody.notes:
        if n.pitch != 0:
            first_note = n
            break
    if first_note is None:
        return inverted
    axis = first_note.octave * 12 + (first_note.pitch - 1)
    for i, n in enumerate(inverted.notes):
        if i == 0:
            continue
        src = melody.notes[i]
        if src.pitch == 0:
            n.pitch = 0
            continue
        original_pitch = src.octave * 12 + (src.pitch - 1)
        interval = original_pitch - axis
        new_pitch = axis - interval
        n.octave = new_pitch // 12
        n.pitch = (new_pitch % 12) + 1
        if n.octave < 3:
            n.octave = 3
        elif n.octave > 5:
            n.octave = 5
    return inverted


def retrograde(melody: Melody) -> Melody:
    reversed_notes = list(reversed(melody.notes))
    return Melody([n.copy() for n in reversed_notes])


def _adjust_melody_length(melody: Melody, target: int = 16) -> Melody:
    current = melody.total_duration()
    if current == target:
        return melody
    adjusted = melody.copy()
    if current < target:
        available_pitches = []
        for octave in range(3, 6):
            for pitch in range(1, 13):
                if octave == 3 and pitch < 6:
                    continue
                if octave == 5 and pitch > 8:
                    continue
                available_pitches.append((octave, pitch))
        while adjusted.total_duration() < target:
            remaining = target - adjusted.total_duration()
            durations = [0.5, 1, 2, 4]
            valid_durations = [d for d in durations if d <= remaining]
            if not valid_durations:
                break
            octave, pitch = random.choice(available_pitches)
            duration = random.choice(valid_durations)
            adjusted.notes.append(Note(octave, pitch, duration))
    elif current > target:
        while adjusted.total_duration() > target:
            if not adjusted.notes:
                break
            excess = adjusted.total_duration() - target
            if excess >= adjusted.notes[-1].duration:
                adjusted.notes.pop()
            else:
                adjusted.notes[-1].duration -= excess
                if adjusted.notes[-1].duration <= 0:
                    adjusted.notes.pop()
    return adjusted

