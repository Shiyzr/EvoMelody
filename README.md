### EvoMelody · 遗传算法旋律生成器

一个用遗传算法自动进化旋律的教学/研究型项目。项目以 4/4 拍、约 4 小节为基本单位，从给定的初始种群出发，通过选择、交叉、变异与若干音乐学启发式操作（移调、倒影、逆行等）逐代优化旋律，最终导出 MIDI（可选导出 MusicXML）与适应度演化曲线。


### 功能特性
- **可复现实验**：固定随机种子（47），结果可重复。
- **完整演化流程**：初始化 → 评估 → 选择 → 交叉/变异 → 可选乐理操作 → 记录指标。
- **多指标适应度**：音域、级进/跳进、节奏多样性、动机重复、终止稳定性、音符密度、重音对齐、和声暗示、音高分布等（见 `fitness.py`）。
- **结果可视化与导出**：
  - 输出最佳若干旋律的 `.mid` 文件
  - 输出演化过程中最佳/平均适应度曲线 `outputs/fitness_history.png`
  - 提供阶段性导出示例（第 0/20/50/80/100 代）


### 环境与依赖
- Python 3.8+
- 依赖包：`numpy`, `matplotlib`, `music21`

安装依赖（建议使用虚拟环境）：

```bash
pip install -U numpy matplotlib music21
```

提示：
- `music21` 用于构建乐谱流并导出 MIDI/MusicXML。首次使用可能下载相关资源。
- 试听 MIDI 可使用任意播放器；如需查看/编辑乐谱（MusicXML），推荐安装 MuseScore。


### 快速开始
在项目根目录执行：

```bash
python main.py
```

运行结束后可在 `outputs/` 目录找到：
- `melody_top1.mid` ~ `melody_top5.mid`：当前演化结束时适应度最高的前 5 条旋律
- `fitness_history.png`：最佳/平均适应度随代数变化的曲线

演化过程阶段性保存示例：

```bash
python save_evolution_midi.py
```

生成的文件位于 `outputs/evolution_demo/`：
- `gen_00_best.mid`, `gen_20_best.mid`, `gen_50_best.mid`, `gen_80_best.mid`, `gen_100_best.mid`


### 参数与可配置项
主要参数位于 `main.py`/`algorithm.py` 中创建 `GeneticAlgorithm` 时传入：
- `population_size`：种群规模（默认 20）
- `generations`：演化代数（默认 150 于 `main.py`，示例 100 于 `save_evolution_midi.py`）
- `mutation_rate`：变异概率（默认 0.2）
- `elite_size`：精英保留数量（默认 2）

适应度各子项的权重在 `fitness.py` 的 `FitnessEvaluator.weights` 中设置，可按需微调。


### 初始种群与数据格式
默认从 `input/initial_population.json` 读取若干旋律作为初始候选，并在需要时复制补全到指定种群规模。每个音符使用三元组表示：

```
[octave, pitch, duration]
```

- `octave`：八度（整数，通常 3~5）
- `pitch`：音高（0~12；0 表示休止，1~12 表示 C~B，其中 1=C, 12=B）
- `duration`：时值（以四分音符为 1.0；0.5=八分，1=四分，2=二分，4=全音）

演化过程中会通过 `_adjust_melody_length` 自动将旋律“对齐”到目标总时值（默认 16 个四分音符=4 小节）。


### 目录结构
- `main.py`：标准演化流程入口，导出前 5 条最佳旋律与适应度曲线。
- `save_evolution_midi.py`：按若干代数检查点导出最佳旋律 MIDI，用于演化对比展示。
- `algorithm.py`：`GeneticAlgorithm` 实现（初始化、评估、选择、交叉/变异、可选乐理操作、日志与可视化）。
- `models.py`：核心数据结构
  - `Note`：音符对象（含 `to_music21_note` 转换）
  - `Melody`：旋律对象（含 `to_music21_stream` 转换）
- `operations.py`：操作与算子
  - `generate_initial_population`、`crossover`、`mutate`、`transpose`、`inversion`、`retrograde` 等
- `fitness.py`：多维度适应度评估器与各子项计算逻辑
- `io_utils.py`：导出工具（保存为 MIDI/MusicXML）
- `input/`：初始种群数据（`initial_population.json` 等）
- `outputs/`：运行输出（MIDI、演化曲线、演化示例）


### 自定义与扩展
- **调整演化强度**：增大 `generations` 或 `population_size`，通常会得到更高分的旋律，但耗时更长。
- **调权重/指标**：在 `fitness.py` 调整 `weights` 或新增/替换指标函数。
- **新增算子**：在 `operations.py` 中新增新的变换（如节奏缩放、局部转位等），并在 `GeneticAlgorithm.evolve` 中插入调用。
- **自定义初始种群**：编辑 `input/initial_population.json` 或在 `operations.generate_initial_population` 中更换加载策略。


### 常见问题（FAQ）
- 运行提示缺少依赖/库？请先执行上文的 `pip install` 命令安装依赖。
- 生成了 MIDI，但无法打开？请使用任意支持 MIDI 的播放器；若要看谱面，导出 MusicXML 并用 MuseScore 打开。
- 输出在哪？所有结果默认写入 `outputs/`，脚本运行时会自动创建目录。
- 结果可复现吗？项目固定了随机种子（`random.seed(47)` 与 `numpy.random.seed(47)`）。


