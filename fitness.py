import numpy as np

from models import Melody


class FitnessEvaluator:
    """
    适应度评估器
    根据提供的音乐理论规则进行加权打分
    """
    
    def __init__(self):
        # 定义各项评分指标的权重
        self.weights = {
            'range': 1.0,               # 音域范围权重
            'large_leap': 1.5,          # 大跳音程权重（避免过度大跳）
            'prefer_pentatonic': 1.2,   # 五声音阶偏好权重
            'rhythm_variety': 1.0,      # 节奏变化权重
            'motif_repetition': 2.0,    # 动机重复权重
            'stable_ending': 1.5,       # 稳定结尾权重
            'avoid_continuous_repeat': 1.0, # 避免连续重复音权重
            'harmony': 1.0,             # 和声暗示权重
            'pitch_variety': 1.0,       # 音高变化权重
            'tonality': 1.5,            # 调性权重
            'pitch_distribution': 1.2,  # 音高分布权重
            'smoothness': 1.3,          # 旋律平滑度权重
            'large_leap_count': 1.0,    # 大跳次数权重
        }
    
    def evaluate(self, melody: Melody) -> float:
        """
        评估旋律的总分
        :param melody: Melody对象
        :return: 加权总分
        """
        scores = {}
        # 计算各项指标得分
        scores['range'] = self._evaluate_range(melody)
        scores['large_leap'] = self._evaluate_large_leap(melody)
        scores['prefer_pentatonic'] = self._evaluate_scale_preference(melody)
        scores['rhythm_variety'] = self._evaluate_rhythm_variety(melody)
        scores['motif_repetition'] = self._evaluate_motif_repetition(melody)
        scores['stable_ending'] = self._evaluate_stable_ending(melody)
        scores['avoid_continuous_repeat'] = self._evaluate_continuous_repeat(melody)
        scores['harmony'] = self._evaluate_harmony_hint(melody)
        scores['pitch_distribution'] = self._evaluate_pitch_distribution(melody)
        scores['smoothness'] = self._evaluate_smoothness(melody)
        scores['large_leap_count'] = self._evaluate_large_leap_count(melody)
        
        # 根据权重计算总分
        total_score = sum(scores[key] * self.weights[key] for key in scores)
        return total_score
    
    def _evaluate_range(self, melody: Melody) -> float:
        """
        评估音域范围
        理想范围是8到15个不同的音高
        """
        pitches = set((n.octave, n.pitch) for n in melody.notes)
        num_pitches = len(pitches)
        if 8 <= num_pitches <= 15:
            return 10.0
        elif num_pitches < 8:
            return num_pitches * 1.0
        else:
            return 10.0 - (num_pitches - 15) * 0.5
    
    def _evaluate_large_leap(self, melody: Melody) -> float:
        """
        评估大跳音程
        惩罚超过7个半音（纯五度以上）的跳进
        """
        if len(melody.notes) < 2:
            return 10.0
        penalty = 0
        for i in range(len(melody.notes) - 1):
            n1, n2 = melody.notes[i], melody.notes[i+1]
            interval = abs((n2.octave * 12 + n2.pitch) - (n1.octave * 12 + n1.pitch))
            if interval > 7:
                penalty += (interval - 7) * 0.5
        return max(0, 10.0 - penalty)
    
    def _evaluate_scale_preference(self, melody: Melody) -> float:
        """
        评估调性偏好
        检查旋律是否符合大调音阶或五声音阶
        """
        major_scale = {0, 2, 4, 5, 7, 9, 11}
        pentatonic_scale = {0, 2, 4, 7, 9}
        max_score = 0
        for root in range(12):
            # 移调
            major_transposed = {(p + root) % 12 for p in major_scale}
            pentatonic_transposed = {(p + root) % 12 for p in pentatonic_scale}
            
            # 计算符合音阶的音符数量
            major_count = sum(1 for n in melody.notes if n.pitch in major_transposed)
            pentatonic_count = sum(1 for n in melody.notes if n.pitch in pentatonic_transposed)
            
            major_ratio = major_count / len(melody.notes)
            pentatonic_ratio = pentatonic_count / len(melody.notes)
            
            # 五声音阶给予更高的权重 (12 vs 10)
            score = max(major_ratio * 10, pentatonic_ratio * 12)
            max_score = max(max_score, score)
        return max_score
    
    def _evaluate_rhythm_variety(self, melody: Melody) -> float:
        """
        评估节奏多样性
        理想情况是有3-4种不同的音符时值
        """
        durations = set(n.duration for n in melody.notes)
        num_durations = len(durations)
        if 3 <= num_durations <= 4:
            return 10.0
        elif num_durations == 2:
            return 7.0
        elif num_durations == 1:
            return 3.0
        else:
            return 8.0
    
    def _evaluate_motif_repetition(self, melody: Melody) -> float:
        """
        评估动机重复
        检测是否有重复的旋律片段（动机）
        """
        if len(melody.notes) < 3:
            return 5.0
        max_repetition = 0
        for motif_len in [2, 3, 4]:
            if len(melody.notes) < motif_len:
                continue
            motifs = []
            # 提取所有可能的动机
            for i in range(len(melody.notes) - motif_len + 1):
                motif = []
                for j in range(motif_len - 1):
                    n1 = melody.notes[i + j]
                    n2 = melody.notes[i + j + 1]
                    # 记录音程关系作为动机特征
                    interval = (n2.octave * 12 + n2.pitch) - (n1.octave * 12 + n1.pitch)
                    motif.append(interval)
                motifs.append(tuple(motif))
            
            from collections import Counter
            counter = Counter(motifs)
            if counter:
                max_repetition = max(max_repetition, max(counter.values()))
        
        # 根据重复次数打分
        if max_repetition == 2:
            return 10.0
        elif max_repetition == 3:
            return 9.0
        elif max_repetition >= 4:
            return 7.0
        else:
            return 5.0
    
    def _evaluate_stable_ending(self, melody: Melody) -> float:
        """
        评估结尾稳定性
        检查最后一个音是否为主音或属音
        """
        if not melody.notes:
            return 0
        last_note = melody.notes[-1]
        for root in range(12):
            tonic = root
            dominant = (root + 7) % 12
            if last_note.pitch == tonic:
                return 10.0
            elif last_note.pitch == dominant:
                return 8.0
        return 5.0
    
    def _evaluate_continuous_repeat(self, melody: Melody) -> float:
        """
        评估连续重复音
        惩罚连续重复同一个音高的情况
        """
        if len(melody.notes) < 2:
            return 10.0
        continuous_count = 0
        for i in range(len(melody.notes) - 1):
            n1, n2 = melody.notes[i], melody.notes[i+1]
            if n1.octave == n2.octave and n1.pitch == n2.pitch:
                continuous_count += 1
        penalty = continuous_count * 1.5
        return max(0, 10.0 - penalty)
    
    def _evaluate_harmony_hint(self, melody: Melody) -> float:
        """
        评估和声暗示
        检查旋律是否暗示了大三和弦或小三和弦
        """
        if len(melody.notes) < 3:
            return 5.0
        pitches = [(n.octave * 12 + n.pitch) for n in melody.notes]
        pitch_set = set([p % 12 for p in pitches])
        max_score = 0
        for root in range(12):
            major_chord = {root, (root + 4) % 12, (root + 7) % 12}
            minor_chord = {root, (root + 3) % 12, (root + 7) % 12}
            major_match = len(pitch_set & major_chord)
            minor_match = len(pitch_set & minor_chord)
            
            if major_match == 3:
                max_score = max(max_score, 10.0)
            elif minor_match == 3:
                max_score = max(max_score, 10.0)
            elif major_match == 2 or minor_match == 2:
                max_score = max(max_score, 7.0)
        return max(max_score, 5.0)
    
    def _evaluate_pitch_distribution(self, melody: Melody) -> float:
        """
        评估音高分布
        使用信息熵来衡量音高分布的均匀程度
        """
        from collections import Counter
        pitches = [n.pitch for n in melody.notes]
        counter = Counter(pitches)
        total = len(pitches)
        probs = [counter[i] / total for i in range(12)]
        # 计算熵
        entropy = -sum(p * np.log2(p) if p > 0 else 0 for p in probs)
        
        if entropy < 2.0:
            return 10.0
        elif entropy < 2.5:
            return 8.0
        elif entropy < 3.0:
            return 6.0
        else:
            return 4.0
    
    def _evaluate_smoothness(self, melody: Melody) -> float:
        """
        评估旋律平滑度
        计算级进（3个半音以内）与跳进的比例
        """
        if len(melody.notes) < 2:
            return 10.0
        stepwise = 0
        leaps = 0
        for i in range(len(melody.notes) - 1):
            n1, n2 = melody.notes[i], melody.notes[i+1]
            interval = abs((n2.octave * 12 + n2.pitch) - (n1.octave * 12 + n1.pitch))
            if interval <= 3:
                stepwise += 1
            else:
                leaps += 1
        total = stepwise + leaps
        if total == 0:
            return 5.0
        ratio = stepwise / total
        
        # 理想的级进比例在 60% 到 80% 之间
        if 0.6 <= ratio <= 0.8:
            return 10.0
        elif 0.4 <= ratio < 0.6:
            return 8.0
        elif 0.8 < ratio <= 0.9:
            return 8.0
        else:
            return 6.0
    
    def _evaluate_large_leap_count(self, melody: Melody) -> float:
        """
        评估大跳次数
        惩罚超过一个八度（12个半音）的极大跳进
        """
        if len(melody.notes) < 2:
            return 10.0
        large_leaps = 0
        for i in range(len(melody.notes) - 1):
            n1, n2 = melody.notes[i], melody.notes[i+1]
            interval = abs((n2.octave * 12 + n2.pitch) - (n1.octave * 12 + n1.pitch))
            if interval > 12:
                large_leaps += 1
        penalty = large_leaps * 3.0
        return max(0, 10.0 - penalty)
