import os
import random
import numpy as np

from algorithm import GeneticAlgorithm
from io_utils import save_melody_as_midi, save_melody_as_musicxml


def main():
    print("\n" + "=" * 60)
    print("遗传算法作曲系统")
    print("音乐与数学 - 期中研究题")
    print("=" * 60)
    random.seed(42)
    np.random.seed(42)
    ga = GeneticAlgorithm(
        population_size=20,
        generations=150,
        mutation_rate=0.2,
        elite_size=2,
    )
    ga.initialize_population()
    ga.run()
    best_melody = ga.get_best_melody()
    print(f"\n最佳旋律适应度: {best_melody.fitness:.2f}")
    print(f"音符数量: {len(best_melody.notes)}")
    print(f"总时长: {best_melody.total_duration()} 个四分音符")
    print("\n正在保存结果...")
    output_dir = os.path.join(os.getcwd(), 'outputs')
    os.makedirs(output_dir, exist_ok=True)
    top_melodies = ga.get_top_melodies(5)
    for i, melody in enumerate(top_melodies):
        print(f"\n第 {i+1} 名旋律 (适应度: {melody.fitness:.2f})")
        midi_path = os.path.join(output_dir, f'melody_top{i+1}.mid')
        save_melody_as_midi(melody, midi_path)
        # xml_path = f'/mnt/user-data/outputs/melody_top{i+1}.musicxml'
        # save_melody_as_musicxml(melody, xml_path)
    ga.plot_fitness_history()
    print("\n" + "=" * 60)
    print("实验完成！")
    print("=" * 60)
    print("\n输出文件：")
    print(f"- 适应度曲线: {os.path.join(output_dir, 'fitness_history.png')}")
    print(f"- 前5个最佳旋律MIDI文件: {os.path.join(output_dir, 'melody_top*.mid')}")
    print("\n可以使用任何MIDI播放器或音乐软件（如MuseScore）打开MIDI文件进行试听。")


if __name__ == "__main__":
    main()
