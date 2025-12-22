import os
import random
import numpy as np
from algorithm import GeneticAlgorithm
from io_utils import save_melody_as_midi

def main():
    print("Evolution of Melody - Saving MIDI files...")
    
    # Set seeds for reproducibility
    random.seed(42)
    np.random.seed(42)
    
    # Create output directory for evolution steps
    output_dir = os.path.join(os.getcwd(), 'outputs', 'evolution_demo')
    os.makedirs(output_dir, exist_ok=True)
    print(f"Output directory: {output_dir}")

    # Initialize GA
    ga = GeneticAlgorithm(
        population_size=20,
        generations=100,
        mutation_rate=0.2,
        elite_size=2
    )
    
    ga.initialize_population()
    
    # Save Generation 0
    best_gen0 = ga.get_best_melody()
    filename_gen0 = os.path.join(output_dir, 'gen_00_best.mid')
    save_melody_as_midi(best_gen0, filename_gen0)
    print(f"Saved Generation 0 Best Melody (Fitness: {best_gen0.fitness:.2f})")
    
    # Evolve and save intermediate results
    checkpoints = [20, 50, 80, 100]
    current_gen = 0
    
    for target_gen in checkpoints:
        steps = target_gen - current_gen
        for _ in range(steps):
            ga.evolve()
        current_gen = target_gen
        
        best_current = ga.get_best_melody()
        filename = os.path.join(output_dir, f'gen_{target_gen:02d}_best.mid')
        save_melody_as_midi(best_current, filename)
        print(f"Saved Generation {target_gen} Best Melody (Fitness: {best_current.fitness:.2f})")

    print("\nAll MIDI files have been saved successfully.")

if __name__ == "__main__":
    main()
