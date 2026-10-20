"""
数字炸弹 - 核心规则与电脑推理

规则：
- 秘密数字是 4 位数字（0000-9999），允许首位是 0，数字可以重复
- 每次猜测后，只回报“位置和数字都对的有几个”（0-4）
- 先得到 4 的一方获胜

电脑采用“候选集过滤 + 极小化极大采样”策略：
1. 把所有可能与历史反馈一致的 4 位数字作为候选集
2. 每次猜完，用真实反馈过滤候选集
3. 选择能让最坏情况候选数最少的那一个
"""

import random

# 全部合法的 4 位数字（0000-9999，允许首位为 0）
ALL_NUMBERS = tuple(f"{n:04d}" for n in range(10000))

# 采样上限：候选集太大时只评估一部分，保证单次请求的耗时可控
_SAMPLE_LIMIT = 400


def is_valid_number(value):
    """校验是否为合法的 4 位数字（0000-9999，首位允许是 0）。"""
    if not isinstance(value, str):
        return False
    return len(value) == 4 and value.isdigit()


def normalize_number(value):
    """把输入规整成 4 位字符串；非法返回 None。"""
    if value is None:
        return None
    text = str(value).strip()
    if is_valid_number(text):
        return text
    # 允许前端传数字类型，例如 9027
    return None


def count_hits(secret, guess):
    """位置和数字都对的个数（仅公牛数，不含错位）。"""
    return sum(1 for a, b in zip(secret, guess) if a == b)


def random_number(rng=None):
    """生成一个随机的 4 位数字（0000-9999）。"""
    generator = rng or random
    return f"{generator.randint(0, 9999):04d}"


class ComputerBrain:
    """电脑猜数：维护候选集并挑选下一次猜测。"""

    def __init__(self, candidates=None, rng=None):
        self.candidates = list(candidates if candidates is not None else ALL_NUMBERS)
        self.rng = rng or random

    def observe(self, guess, hits):
        """用一次真实反馈收窄候选集。"""
        self.candidates = [c for c in self.candidates if count_hits(c, guess) == hits]
        if not self.candidates:
            # 理论上不会发生；兜底避免后续猜测抛异常
            self.candidates = list(ALL_NUMBERS)
        return self.candidates

    def choose(self):
        """挑一个候选；候选很少时直接猜，否则用采样 minimax 挑信息量最大的。"""
        if not self.candidates:
            self.candidates = list(ALL_NUMBERS)
        if len(self.candidates) == 1:
            return self.candidates[0]

        candidates = self.candidates
        guesses = (
            candidates
            if len(candidates) <= _SAMPLE_LIMIT
            else self.rng.sample(candidates, _SAMPLE_LIMIT)
        )
        pool = (
            candidates
            if len(candidates) <= _SAMPLE_LIMIT
            else self.rng.sample(candidates, _SAMPLE_LIMIT)
        )

        best_guess = guesses[0]
        best_score = None
        for guess in guesses:
            buckets = {}
            for candidate in pool:
                hits = count_hits(candidate, guess)
                buckets[hits] = buckets.get(hits, 0) + 1
            # 猜中（4 个全对）是最理想的结果，单独压低评分
            worst = max(buckets.values())
            score = (worst, -buckets.get(4, 0))
            if best_score is None or score < best_score:
                best_guess, best_score = guess, score
        return best_guess

    def guess_for(self, history):
        """根据历史猜测（[(guess, hits), ...]）重建状态并给出下一猜。"""
        for guess, hits in history:
            self.observe(guess, hits)
        return self.choose()
