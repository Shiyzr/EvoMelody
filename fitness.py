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
            'range': 1.0,               # 音高多样性权重
            'large_leap': 1.5,          # 大跳音程权重（避免过度大跳）
            'prefer_pentatonic': 1.2,   # 音阶偏好权重
            'rhythm_variety': 1.0,      # 节奏变化权重
            'motif_repetition': 2.0,    # 动机重复权重
            'stable_ending': 1.5,       # 稳定结尾权重
            'avoid_continuous_repeat': 1.0, # 避免连续重复音权重
            'harmony': 1.0,             # 和声暗示权重
            'note_density': 1.0,        # 音符密度权重
            'beat_alignment': 0.9,      # 重音与节拍对齐权重
            'pitch_distribution': 1.2,  # 音高分布权重
            'smoothness': 1.3,          # 旋律平滑度权重
            'very_large_leap': 1.0,    # 超大跳次数权重
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
        scores['note_density'] = self._evaluate_note_density(melody)
        scores['beat_alignment'] = self._evaluate_beat_alignment(melody)
        scores['pitch_distribution'] = self._evaluate_pitch_distribution(melody)
        scores['smoothness'] = self._evaluate_smoothness(melody)
        scores['very_large_leap'] = self._evaluate_very_large_leap(melody)
        
        # 根据权重计算总分
        total_score = sum(scores[key] * self.weights[key] for key in scores)
        return total_score
    
    def _evaluate_range(self, melody: Melody) -> float:
        """
        评估音高多样性
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
        评估结尾稳定性（修正版）
        先估计旋律的主音(root)，再判断最后一个音是否落在主音/属音等稳定音上
        """
        if not melody.notes:
            return 0.0

        major_scale = {0, 2, 4, 5, 7, 9, 11}
        pentatonic_scale = {0, 2, 4, 7, 9}

        # 1) 估计最可能的 root：选择“调内覆盖率”最高的 root
        best_root = 0
        best_score = -1.0
        n = len(melody.notes)

        for root in range(12):
            major_transposed = {(p + root) % 12 for p in major_scale}
            pent_transposed = {(p + root) % 12 for p in pentatonic_scale}

            major_count = sum(1 for note in melody.notes if note.pitch in major_transposed)
            pent_count = sum(1 for note in melody.notes if note.pitch in pent_transposed)

            major_ratio = major_count / n
            pent_ratio = pent_count / n

            # 五声音阶略微偏好（可调），但不让它“碾压”大调
            score = max(major_ratio, 1.05 * pent_ratio)

            # 可选：让“主音出现次数”作为轻微 tie-breaker
            tonic_bonus = sum(1 for note in melody.notes if note.pitch == root) / n
            score += 0.02 * tonic_bonus

            if score > best_score:
                best_score = score
                best_root = root

        # 2) 用估计出的 root 判断结尾稳定性
        last_pitch = melody.notes[-1].pitch
        tonic = best_root
        dominant = (best_root + 7) % 12
        mediant_major = (best_root + 4) % 12  # 大三度（大调稳定音）
        mediant_minor = (best_root + 3) % 12  # 小三度（小调稳定音）

        if last_pitch == tonic:
            return 10.0
        if last_pitch == dominant:
            return 8.0
        if last_pitch == mediant_major or last_pitch == mediant_minor:
            return 6.5
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
        # 转换为 0-based pitch class，忽略休止符
        pitches = [(n.pitch - 1) % 12 for n in melody.notes if n.pitch > 0]
        if not pitches:
            return 5.0
            
        pitch_set = set(pitches)
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
        # 转换为 0-based pitch class，忽略休止符
        pitches = [(n.pitch - 1) % 12 for n in melody.notes if n.pitch > 0]
        if not pitches:
            return 5.0
            
        counter = Counter(pitches)
        total = len(pitches)
        # range(12) 覆盖 0-11
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
    
    def _evaluate_very_large_leap(self, melody: Melody) -> float:
        """
        评估超大跳次数
        惩罚超过一个八度（12个半音）的极大跳进
        """
        if len(melody.notes) < 2:
            return 10.0
        very_large_leaps = 0
        for i in range(len(melody.notes) - 1):
            n1, n2 = melody.notes[i], melody.notes[i+1]
            interval = abs((n2.octave * 12 + n2.pitch) - (n1.octave * 12 + n1.pitch))
            if interval > 12:
                very_large_leaps += 1
        penalty = very_large_leaps * 3.0
        return max(0, 10.0 - penalty)

    def _evaluate_note_density(self, melody: Melody) -> float:
        """
        评估音符密度
        计算平均每小节的音符数量
        理想范围是每小节 4 到 12 个音符
        """
        total_duration = melody.total_duration()
        if total_duration == 0:
            return 0.0
        
        # 假设4/4拍，一个小节4拍
        num_measures = total_duration / 4.0
        # 避免极短旋律导致的除零或异常，虽然total_duration!=0已判断，但若极小比如0.1
        if num_measures < 0.1:
             return 0.0

        density = len(melody.notes) / num_measures
        
        if 4 <= density <= 12:
            return 10.0
        elif density < 4:
            return density * 2.5
        else:
            return max(0, 10.0 - (density - 12) * 1.0)

    def _evaluate_beat_alignment(self, melody: Melody) -> float:
        """
        评估重音与节拍对齐
        鼓励音符落在强拍（第1、3拍）或正拍上
        惩罚过度的切分节奏（连续偏离拍点）
        """
        if not melody.notes:
            return 0.0

        current_time = 0.0
        on_beat_score = 0.0
        consecutive_off_beat = 0
        syncopation_penalty = 0.0
        
        # 4/4拍，每拍1.0
        for note in melody.notes:
            # 计算当前音符起始位置在小节内的位置 (0.0 - 4.0)
            measure_pos = current_time % 4.0
            
            # 判断是否在拍点上 (允许微小误差)
            # 强拍: 0.0 (第1拍), 2.0 (第3拍)
            # 弱拍: 1.0 (第2拍), 3.0 (第4拍)
            
            is_strong_beat = False
            is_weak_beat = False
            
            # 检查是否接近整数拍
            dist_to_beat = min(abs(measure_pos - round(measure_pos)), abs(measure_pos - round(measure_pos) - 4.0))
            
            if dist_to_beat < 0.05: # 认为是在正拍上
                beat_idx = round(measure_pos) % 4
                if beat_idx == 0 or beat_idx == 2:
                    is_strong_beat = True
                else:
                    is_weak_beat = True
            
            if is_strong_beat:
                on_beat_score += 2.0
                consecutive_off_beat = 0
            elif is_weak_beat:
                on_beat_score += 1.0
                consecutive_off_beat = 0
            else:
                # 切分/Off-beat
                consecutive_off_beat += 1
                # 如果连续切分超过2个音符，开始惩罚
                if consecutive_off_beat > 2:
                    syncopation_penalty += (consecutive_off_beat - 2) * 1.0
            
            current_time += note.duration
            
        # 归一化得分
        # 理论最高分估算：假设所有音符都在强拍（不可能，但作为分母参考），或者平均每个音符得1.5分
        # 这里用一种相对比例：得分 / (音符数 * 1.5) * 10
        # 或者简单点：计算平均得分
        
        avg_score = on_beat_score / len(melody.notes)
        # avg_score 范围大约在 0 到 2 之间
        # 映射到 0-10
        
        base_score = (avg_score / 2.0) * 10.0
        
        final_score = base_score - syncopation_penalty
        return max(0.0, min(10.0, final_score))


