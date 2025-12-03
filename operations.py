import random
from typing import List, Tuple

from models import Melody, Note


def generate_random_melody(bars: int = 4) -> Melody:
    """
    随机生成一个旋律
    bars: 小节数
    """
    available_pitches = []
    for pitch in range(5, 12):
        available_pitches.append((3, pitch))
    for pitch in range(0, 12):
        available_pitches.append((4, pitch))
    for pitch in range(0, 8):
        available_pitches.append((5, pitch))
    target_duration = bars * 8 * 4
    notes = []
    current_duration = 0
    durations = [1, 2, 4, 8]
    while current_duration < target_duration:
        octave, pitch = random.choice(available_pitches)
        remaining = target_duration - current_duration
        valid_durations = [d for d in durations if d <= remaining]
        if not valid_durations:
            valid_durations = [1]
        duration = random.choice(valid_durations)
        notes.append(Note(octave, pitch, duration))
        current_duration += duration
    return Melody(notes)


def generate_initial_population(size: int = 15) -> List[Melody]:
    population = []
    for i in range(size):
        melody = generate_random_melody()
        population.append(melody)
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
                new_pitch = (n.pitch + delta) % 12
                n.pitch = new_pitch
            elif mutation_type == 'octave':
                delta = random.choice([-1, 1])
                new_octave = n.octave + delta
                n.octave = max(3, min(5, new_octave))
            elif mutation_type == 'duration':
                durations = [1, 2, 4, 8]
                n.duration = random.choice(durations)
    mutated = _adjust_melody_length(mutated)
    return mutated


def transpose(melody: Melody, semitones: int) -> Melody:
    transposed = melody.copy()
    for n in transposed.notes:
        total_pitch = n.octave * 12 + n.pitch + semitones
        n.octave = total_pitch // 12
        n.pitch = total_pitch % 12
        if n.octave < 3:
            n.octave = 3
        elif n.octave > 5:
            n.octave = 5
    return transposed


def inversion(melody: Melody) -> Melody:
    if not melody.notes:
        return melody.copy()
    inverted = melody.copy()
    first_note = melody.notes[0]
    axis = first_note.octave * 12 + first_note.pitch
    for i, n in enumerate(inverted.notes):
        if i == 0:
            continue
        original_pitch = melody.notes[i].octave * 12 + melody.notes[i].pitch
        interval = original_pitch - axis
        new_pitch = axis - interval
        n.octave = new_pitch // 12
        n.pitch = new_pitch % 12
        if n.octave < 3:
            n.octave = 3
        elif n.octave > 5:
            n.octave = 5
    return inverted


def retrograde(melody: Melody) -> Melody:
    reversed_notes = list(reversed(melody.notes))
    return Melody([n.copy() for n in reversed_notes])


def _adjust_melody_length(melody: Melody, target: int = 32) -> Melody:
    current = melody.total_duration()
    if current == target:
        return melody
    adjusted = melody.copy()
    if current < target:
        available_pitches = []
        for octave in range(3, 6):
            for pitch in range(12):
                if octave == 3 and pitch < 5:
                    continue
                if octave == 5 and pitch > 7:
                    continue
                available_pitches.append((octave, pitch))
        while adjusted.total_duration() < target:
            remaining = target - adjusted.total_duration()
            durations = [1, 2, 4, 8]
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

