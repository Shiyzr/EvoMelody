import random
import os
from typing import List

import matplotlib.pyplot as plt

from models import Melody
from fitness import FitnessEvaluator
from operations import (
    generate_initial_population,
    crossover,
    mutate,
    transpose,
    inversion,
    retrograde,
)


class GeneticAlgorithm:
    """
    遗传算法主类
    """
    
    def __init__(self, 
                 population_size: int = 20,
                 generations: int = 100,
                 mutation_rate: float = 0.2,
                 elite_size: int = 2):
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.elite_size = elite_size
        self.evaluator = FitnessEvaluator()
        self.population = []
        self.best_fitness_history = []
        self.avg_fitness_history = []
    
    def initialize_population(self):
        print(f"正在生成初始种群（{self.population_size}个个体）...")
        self.population = generate_initial_population(self.population_size)
        self._evaluate_population()
        print(f"初始种群生成完成！")
    
    def _evaluate_population(self):
        for melody in self.population:
            melody.fitness = self.evaluator.evaluate(melody)
    
    def _selection(self) -> Melody:
        tournament_size = 3
        tournament = random.sample(self.population, tournament_size)
        return max(tournament, key=lambda m: m.fitness)
    
    def evolve(self):
        new_population = []
        sorted_pop = sorted(self.population, key=lambda m: m.fitness, reverse=True)
        for i in range(self.elite_size):
            new_population.append(sorted_pop[i].copy())
        while len(new_population) < self.population_size:
            parent1 = self._selection()
            parent2 = self._selection()
            if random.random() < 0.8:
                child1, child2 = crossover(parent1, parent2)
            else:
                child1, child2 = parent1.copy(), parent2.copy()
            child1 = mutate(child1, self.mutation_rate)
            child2 = mutate(child2, self.mutation_rate)
            if random.random() < 0.1:
                operation = random.choice(['transpose', 'inversion', 'retrograde'])
                if operation == 'transpose':
                    semitones = random.randint(-3, 3)
                    child1 = transpose(child1, semitones)
                elif operation == 'inversion':
                    child1 = inversion(child1)
                elif operation == 'retrograde':
                    child1 = retrograde(child1)
            new_population.append(child1)
            if len(new_population) < self.population_size:
                new_population.append(child2)
        self.population = new_population[:self.population_size]
        self._evaluate_population()
    
    def run(self):
        print(f"\n开始遗传算法，共{self.generations}代...")
        print("=" * 60)
        for generation in range(self.generations):
            self.evolve()
            fitnesses = [m.fitness for m in self.population]
            best_fitness = max(fitnesses)
            avg_fitness = sum(fitnesses) / len(fitnesses)
            self.best_fitness_history.append(best_fitness)
            self.avg_fitness_history.append(avg_fitness)
            if generation % 10 == 0:
                print(f"第 {generation:3d} 代 | 最佳适应度: {best_fitness:.2f} | 平均适应度: {avg_fitness:.2f}")
        print("=" * 60)
        print("遗传算法完成！\n")
    
    def get_best_melody(self) -> Melody:
        return max(self.population, key=lambda m: m.fitness)
    
    def get_top_melodies(self, n: int = 5) -> List[Melody]:
        sorted_pop = sorted(self.population, key=lambda m: m.fitness, reverse=True)
        return sorted_pop[:n]
    
    def plot_fitness_history(self, save_path: str = None):
        plt.figure(figsize=(10, 6))
        plt.plot(self.best_fitness_history, label='Best Fitness', linewidth=2)
        plt.plot(self.avg_fitness_history, label='Average Fitness', linewidth=2)
        plt.xlabel('Generation')
        plt.ylabel('Fitness')
        plt.title('Fitness Evolution')
        plt.legend()
        plt.grid(True, alpha=0.3)
        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"适应度曲线已保存到: {save_path}")
        else:
            default_path = 'outputs/fitness_history.png'
            os.makedirs(os.path.dirname(default_path), exist_ok=True)
            plt.savefig(default_path, dpi=300, bbox_inches='tight')
            print(f"适应度曲线已保存到: {default_path}")
        plt.close()
