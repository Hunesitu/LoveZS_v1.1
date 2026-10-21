"""
数字炸弹 - 核心规则与电脑推理

规则：
- 秘密数字是 4 位数字（0000-9999），允许首位是 0，数字可以重复
- 每次猜测后，只回报“位置和数字都对的有几个”（0-4）
- 先得到 4 的一方获胜

电脑有三种难度：
- easy   ：从候选集里随机猜，不做推理，最容易赢
- normal ：候选集过滤 + 采样极小化极大（默认）
- hard   ：候选集过滤 + 更大范围/精确的极小化极大，候选不多时精确搜索

实现说明：候选集对外仍是字符串（接口和测试都用字符串），内部比较时压成
16 位整数（每个数字占 4 bit），并查一张 65536 长的命中表，把「逐位比较」
变成一次异或 + 一次查表，这样困难难度也只需要几十到几百毫秒。
"""

import random

# 全部合法的 4 位数字（0000-9999，允许首位为 0）
ALL_NUMBERS = tuple(f"{n:04d}" for n in range(10000))

DIFFICULTY_EASY = 'easy'
DIFFICULTY_NORMAL = 'normal'
DIFFICULTY_HARD = 'hard'
DIFFICULTIES = (DIFFICULTY_EASY, DIFFICULTY_NORMAL, DIFFICULTY_HARD)
DEFAULT_DIFFICULTY = DIFFICULTY_NORMAL

# normal：候选集大于这个数时只采样评估
_NORMAL_SAMPLE = 400
# hard：候选集不超过这个数时做精确评估，否则用更大的采样
_HARD_EXACT_LIMIT = 1200
_HARD_SAMPLE = 900
# 各难度的“走神”概率：这一手不推理、随便乱猜，用来拉开体感差距
WASTE_CHANCE = {
    DIFFICULTY_EASY: 0.40,
    DIFFICULTY_NORMAL: 0.15,
    DIFFICULTY_HARD: 0.0,
}


def _build_hits_table():
    """table[x] = x 的 4 个 nibble 里等于 0 的个数（即两个 4 位数字的命中数）。"""
    table = bytearray(65536)
    for x in range(65536):
        table[x] = (
            (1 if (x & 0xF) == 0 else 0)
            + (1 if (x & 0xF0) == 0 else 0)
            + (1 if (x & 0xF00) == 0 else 0)
            + (1 if (x & 0xF000) == 0 else 0)
        )
    return table


_HITS_TABLE = _build_hits_table()


def pack(number):
    """'0123' -> 0x0123"""
    return int(number, 16)


def unpack(value):
    """0x0123 -> '0123'（每个 nibble 都是 0-9，十六进制格式化正好 4 位）"""
    return f'{value:04x}'


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
    return None


def count_hits(secret, guess):
    """位置和数字都对的个数（仅公牛数，不含错位）。"""
    return _HITS_TABLE[pack(secret) ^ pack(guess)]


def random_number(rng=None):
    """生成一个随机的 4 位数字（0000-9999）。"""
    generator = rng or random
    return f"{generator.randint(0, 9999):04d}"


class ComputerBrain:
    """电脑猜数：维护候选集并挑选下一次猜测。"""

    def __init__(self, candidates=None, rng=None, difficulty=DEFAULT_DIFFICULTY):
        self.candidates = list(candidates if candidates is not None else ALL_NUMBERS)
        self.rng = rng or random
        self.difficulty = difficulty if difficulty in DIFFICULTIES else DEFAULT_DIFFICULTY

    def observe(self, guess, hits):
        """用一次真实反馈收窄候选集。"""
        packed_guess = pack(guess)
        self.candidates = [
            c for c in self.candidates if _HITS_TABLE[pack(c) ^ packed_guess] == hits
        ]
        if not self.candidates:
            # 理论上不会发生；兜底避免后续猜测抛异常
            self.candidates = list(ALL_NUMBERS)
        return self.candidates

    @staticmethod
    def _evaluate(guesses, pool):
        """对每个候选猜测统计反馈分布，返回最坏分支最小的那个。"""
        best_guess = guesses[0]
        best_score = None
        for guess in guesses:
            counts = [0, 0, 0, 0, 0]
            for candidate in pool:
                counts[_HITS_TABLE[guess ^ candidate]] += 1
            # 先比最坏分支大小，再比能否直接命中
            score = (max(counts), -counts[4])
            if best_score is None or score < best_score:
                best_guess, best_score = guess, score
        return best_guess

    def choose(self):
        """按难度挑下一猜。"""
        if not self.candidates:
            self.candidates = list(ALL_NUMBERS)
        if len(self.candidates) == 1:
            return self.candidates[0]

        # 走神：按难度概率直接乱猜一手（不推理），用来拉开三档的体感差距
        if self.rng.random() < WASTE_CHANCE[self.difficulty]:
            return self.rng.choice(ALL_NUMBERS)

        packed = [pack(c) for c in self.candidates]

        if self.difficulty == DIFFICULTY_HARD:
            if len(packed) <= _HARD_EXACT_LIMIT:
                choice = self._evaluate(packed, packed)          # 精确搜索
            else:
                guesses = self.rng.sample(packed, _HARD_SAMPLE)
                pool = self.rng.sample(packed, _HARD_SAMPLE)
                choice = self._evaluate(guesses, pool)           # 大范围采样
            return unpack(choice)

        # 普通
        if len(packed) <= _NORMAL_SAMPLE:
            choice = self._evaluate(packed, packed)
        else:
            guesses = self.rng.sample(packed, _NORMAL_SAMPLE)
            pool = self.rng.sample(packed, _NORMAL_SAMPLE)
            choice = self._evaluate(guesses, pool)
        return unpack(choice)

    def guess_for(self, history):
        """根据历史猜测（[(guess, hits), ...]）重建状态并给出下一猜。"""
        for guess, hits in history:
            self.observe(guess, hits)
        return self.choose()
