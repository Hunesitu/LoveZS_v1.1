"""
数字炸弹小游戏测试

覆盖：
- 规则引擎（命中数、合法性、电脑收敛）
- 人机对战完整流程
- 玩家对战匹配、轮流、非法操作
- 权限隔离与战绩统计
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from .game_engine import (
    DIFFICULTIES,
    ComputerBrain,
    count_hits,
    is_valid_number,
    random_number,
)
from .game_hints import HINTS_BY_HITS, get_opponent_hint
from .models import GameGuess, GameRoom

User = get_user_model()


class GameEngineTests(TestCase):
    """纯规则测试，不依赖数据库。"""

    def test_count_hits_only_counts_same_position(self):
        self.assertEqual(count_hits('9027', '9027'), 4)
        self.assertEqual(count_hits('9027', '9720'), 2)   # 9 和 0 位置对，7/2 错位不算
        self.assertEqual(count_hits('1123', '4567'), 0)
        self.assertEqual(count_hits('1234', '1294'), 3)

    def test_is_valid_number(self):
        self.assertTrue(is_valid_number('0000'))   # 允许首位是 0
        self.assertTrue(is_valid_number('0123'))
        self.assertTrue(is_valid_number('1000'))
        self.assertTrue(is_valid_number('9999'))
        self.assertFalse(is_valid_number('123'))    # 位数不够
        self.assertFalse(is_valid_number('12345'))
        self.assertFalse(is_valid_number('12a4'))
        self.assertFalse(is_valid_number(None))
        self.assertFalse(is_valid_number(1234))     # 必须是字符串

    def test_leading_zero_numbers_are_playable(self):
        """0000 这类首位是 0 的数字，猜中和出题都要正常。"""
        self.assertEqual(count_hits('0000', '0000'), 4)
        self.assertEqual(count_hits('0123', '0000'), 1)   # 只有第 1 位对上
        for _ in range(20):
            value = random_number()
            self.assertEqual(len(value), 4)
            self.assertTrue(value.isdigit())
            self.assertTrue(is_valid_number(value))

    def test_computer_converges_within_limit(self):
        secret = '9027'
        for difficulty in DIFFICULTIES:
            brain = ComputerBrain(difficulty=difficulty)
            for _ in range(25):
                guess = brain.choose()
                hits = count_hits(secret, guess)
                if hits == 4:
                    break
                brain.observe(guess, hits)
            else:
                self.fail(f'{difficulty} 难度在 25 次内没有猜中')

    def test_difficulty_controls_waste(self):
        """困难难度不会走神，简单难度会明显更常乱猜。"""
        from .game_engine import WASTE_CHANCE

        self.assertEqual(WASTE_CHANCE['hard'], 0.0)
        self.assertGreater(WASTE_CHANCE['easy'], WASTE_CHANCE['normal'])
        self.assertGreater(WASTE_CHANCE['normal'], WASTE_CHANCE['hard'])

    def test_unknown_difficulty_falls_back_to_normal(self):
        brain = ComputerBrain(difficulty='nightmare')
        self.assertEqual(brain.difficulty, 'normal')

    def test_hits_table_matches_naive_count(self):
        """快捷查表必须和逐位比较结果一致（含首位 0 的边界）。"""
        import random as _random

        rng = _random.Random(1)
        for _ in range(200):
            a = f'{rng.randint(0, 9999):04d}'
            b = f'{rng.randint(0, 9999):04d}'
            naive = sum(1 for x, y in zip(a, b) if x == y)
            self.assertEqual(count_hits(a, b), naive)

    def test_pack_unpack_roundtrip(self):
        from .game_engine import pack, unpack

        for value in ('0000', '0123', '9027', '9999'):
            self.assertEqual(unpack(pack(value)), value)

    def test_observe_filters_candidates(self):
        brain = ComputerBrain()
        brain.observe('9027', 2)
        self.assertTrue(all(count_hits(c, '9027') == 2 for c in brain.candidates))
        self.assertNotIn('9027', brain.candidates)


class GameHintTests(TestCase):
    """对手提示语：只依赖命中数，稳定可复现"""

    def test_hints_cover_zero_to_three(self):
        for hits in (0, 1, 2, 3):
            hint = get_opponent_hint(hits)
            self.assertTrue(hint)
            self.assertIn(hint, HINTS_BY_HITS[hits])

    def test_no_hint_when_all_four_hit(self):
        self.assertEqual(get_opponent_hint(4), '')

    def test_seeded_hint_is_stable(self):
        first = get_opponent_hint(2, seed=42)
        for _ in range(5):
            self.assertEqual(get_opponent_hint(2, seed=42), first)


class GameApiTestBase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.alice = User.objects.create_user(username='alice', password='pass-12345')
        self.bob = User.objects.create_user(username='bob', password='pass-12345')

    def auth(self, user):
        self.client.force_authenticate(user=user)

    @staticmethod
    def payload(response):
        return response.json()['data']


class PveFlowTests(GameApiTestBase):
    def test_requires_login(self):
        response = self.client.post('/api/games/pve/', {}, format='json')
        self.assertIn(response.status_code, (401, 403))

    def test_invalid_secret_rejected(self):
        self.auth(self.alice)
        response = self.client.post('/api/games/pve/', {'secret': '12a4'}, format='json')
        self.assertEqual(response.status_code, 400)

    def test_zero_leading_secret_accepted(self):
        self.auth(self.alice)
        response = self.client.post('/api/games/pve/', {'secret': '0000'}, format='json')
        self.assertEqual(response.status_code, 200)
        room_data = self.payload(response)['room']
        self.assertEqual(room_data['status'], 'playing')
        self.assertEqual(room_data['my_secret'], '0000')

    def test_difficulty_is_stored_and_returned(self):
        self.auth(self.alice)
        response = self.client.post(
            '/api/games/pve/', {'secret': '1234', 'difficulty': 'hard'}, format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.payload(response)['room']['difficulty'], 'hard')
        self.assertEqual(GameRoom.objects.get(player1=self.alice).difficulty, 'hard')

    def test_default_difficulty_is_normal(self):
        self.auth(self.alice)
        response = self.client.post('/api/games/pve/', {'secret': '1234'}, format='json')
        self.assertEqual(self.payload(response)['room']['difficulty'], 'normal')

    def test_illegal_difficulty_falls_back_to_normal(self):
        self.auth(self.alice)
        response = self.client.post(
            '/api/games/pve/', {'secret': '1234', 'difficulty': 'impossible'}, format='json'
        )
        self.assertEqual(self.payload(response)['room']['difficulty'], 'normal')

    def test_start_and_play_a_round(self):
        self.auth(self.alice)
        response = self.client.post('/api/games/pve/', {'secret': '1234'}, format='json')
        self.assertEqual(response.status_code, 200)

        room_data = self.payload(response)['room']
        self.assertEqual(room_data['mode'], 'pve')
        self.assertEqual(room_data['status'], 'playing')
        self.assertTrue(room_data['my_turn'])
        self.assertTrue(room_data['opponent']['computer'])

        room = GameRoom.objects.get(pk=room_data['id'])
        self.assertTrue(room.p2_secret)  # 电脑已经出好题

        response = self.client.post(
            f'/api/games/room/{room.id}/guess/', {'guess': '5678'}, format='json'
        )
        self.assertEqual(response.status_code, 200)
        data = self.payload(response)

        # 玩家一猜 + 电脑一反猜
        self.assertEqual(len(data['results']), 2)
        self.assertEqual(data['results'][0]['side'], 1)
        self.assertEqual(data['results'][1]['side'], 2)
        self.assertEqual(data['room']['my_guess_count'], 1)
        self.assertEqual(data['room']['opponent_guess_count'], 1)
        # 电脑的猜测必须是合法 4 位数，且反馈与秘密数字一致
        computer_guess = data['results'][1]['guess']
        self.assertTrue(is_valid_number(computer_guess))
        self.assertEqual(data['results'][1]['hits'], count_hits('1234', computer_guess))

    def test_winning_guess_finishes_game(self):
        self.auth(self.alice)
        self.client.post('/api/games/pve/', {'secret': '1234'}, format='json')
        room = GameRoom.objects.get(player1=self.alice)
        winning = room.p2_secret

        response = self.client.post(
            f'/api/games/room/{room.id}/guess/', {'guess': winning}, format='json'
        )
        data = self.payload(response)
        self.assertEqual(data['room']['status'], 'finished')
        self.assertTrue(data['room']['result']['i_won'])
        self.assertEqual(data['room']['result']['winner_name'], 'alice')

    def test_secret_never_exposed(self):
        self.auth(self.alice)
        self.client.post('/api/games/pve/', {'secret': '1234'}, format='json')
        room = GameRoom.objects.get(player1=self.alice)

        body = self.client.get(f'/api/games/room/{room.id}/').content.decode()
        # 自己的数字可以回显，对手（电脑）的数字绝不能下发
        self.assertIn('1234', body)
        self.assertNotIn(room.p2_secret, body)

    def test_opponent_guess_carries_hint(self):
        self.auth(self.alice)
        self.client.post('/api/games/pve/', {'secret': '1234'}, format='json')
        room = GameRoom.objects.get(player1=self.alice)

        response = self.client.post(
            f'/api/games/room/{room.id}/guess/', {'guess': '5678'}, format='json'
        )
        guesses = self.payload(response)['room']['guesses']
        mine = [item for item in guesses if item['is_mine']]
        theirs = [item for item in guesses if not item['is_mine']]

        self.assertEqual(mine[0]['hint'], '')      # 自己的猜测不带提示
        self.assertTrue(theirs[0]['hint'])          # 对手的猜测带提示

    def test_cannot_open_second_game(self):
        self.auth(self.alice)
        self.client.post('/api/games/pve/', {'secret': '1234'}, format='json')
        response = self.client.post('/api/games/pve/', {'secret': '5678'}, format='json')
        self.assertEqual(response.status_code, 409)


class PvpFlowTests(GameApiTestBase):
    def _match(self, user):
        self.auth(user)
        response = self.client.post('/api/games/match/', {}, format='json')
        self.assertEqual(response.status_code, 200)
        return self.payload(response)

    def test_matchmaking_pairs_two_players(self):
        first = self._match(self.alice)
        self.assertFalse(first['matched'])
        self.assertEqual(first['room']['status'], 'waiting')

        second = self._match(self.bob)
        self.assertTrue(second['matched'])
        self.assertEqual(second['room']['status'], 'setup')

        # alice 轮询能拿到同一个房间，并看到对手信息
        self.auth(self.alice)
        current = self.payload(self.client.get('/api/games/room/'))['room']
        self.assertEqual(current['id'], second['room']['id'])
        self.assertEqual(current['opponent']['username'], 'bob')

    def test_both_secrets_start_game_and_turns_alternate(self):
        self._match(self.alice)
        room_id = self._match(self.bob)['room']['id']

        self.auth(self.alice)
        response = self.client.post(
            f'/api/games/room/{room_id}/secret/', {'secret': '1111'}, format='json'
        )
        self.assertEqual(self.payload(response)['room']['status'], 'setup')

        self.auth(self.bob)
        response = self.client.post(
            f'/api/games/room/{room_id}/secret/', {'secret': '2222'}, format='json'
        )
        room_data = self.payload(response)['room']
        self.assertEqual(room_data['status'], 'playing')
        self.assertEqual(room_data['turn_side'], 1)   # 房主先手

        # 轮到 alice；bob 抢猜要被拒绝
        self.auth(self.bob)
        response = self.client.post(
            f'/api/games/room/{room_id}/guess/', {'guess': '3333'}, format='json'
        )
        self.assertEqual(response.status_code, 409)

        # alice 猜错 -> 换 bob
        self.auth(self.alice)
        response = self.client.post(
            f'/api/games/room/{room_id}/guess/', {'guess': '3333'}, format='json'
        )
        room_data = self.payload(response)['room']
        self.assertEqual(room_data['turn_side'], 2)
        self.assertFalse(room_data['my_turn'])

        # alice 再次抢猜依然被拒绝
        response = self.client.post(
            f'/api/games/room/{room_id}/guess/', {'guess': '4444'}, format='json'
        )
        self.assertEqual(response.status_code, 409)

    def test_win_and_stats(self):
        self._match(self.alice)
        room_id = self._match(self.bob)['room']['id']

        self.auth(self.alice)
        self.client.post(f'/api/games/room/{room_id}/secret/', {'secret': '1234'}, format='json')
        self.auth(self.bob)
        self.client.post(f'/api/games/room/{room_id}/secret/', {'secret': '5678'}, format='json')

        # alice 猜 bob 的 5678 -> 直接命中
        self.auth(self.alice)
        response = self.client.post(
            f'/api/games/room/{room_id}/guess/', {'guess': '5678'}, format='json'
        )
        room_data = self.payload(response)['room']
        self.assertEqual(room_data['status'], 'finished')
        self.assertTrue(room_data['result']['i_won'])

        stats = self.payload(self.client.get('/api/games/stats/'))
        self.assertEqual(stats['pvp']['wins'], 1)
        self.assertEqual(stats['pvp']['losses'], 0)
        self.assertEqual(stats['recent'][0]['opponent'], 'bob')

        self.auth(self.bob)
        stats = self.payload(self.client.get('/api/games/stats/'))
        self.assertEqual(stats['pvp']['wins'], 0)
        self.assertEqual(stats['pvp']['losses'], 1)

    def test_cancel_while_waiting(self):
        room_id = self._match(self.alice)['room']['id']
        response = self.client.post(f'/api/games/room/{room_id}/cancel/', {}, format='json')
        room_data = self.payload(response)['room']
        self.assertEqual(room_data['status'], 'cancelled')
        self.assertIsNone(self.payload(self.client.get('/api/games/room/'))['room'])

    def test_resign_gives_win_to_opponent(self):
        self._match(self.alice)
        room_id = self._match(self.bob)['room']['id']
        self.auth(self.alice)
        self.client.post(f'/api/games/room/{room_id}/secret/', {'secret': '1234'}, format='json')
        self.auth(self.bob)
        self.client.post(f'/api/games/room/{room_id}/secret/', {'secret': '5678'}, format='json')

        self.auth(self.alice)
        response = self.client.post(f'/api/games/room/{room_id}/cancel/', {}, format='json')
        room_data = self.payload(response)['room']
        self.assertEqual(room_data['status'], 'finished')
        self.assertFalse(room_data['result']['i_won'])

    def test_cancel_before_start_is_not_a_loss(self):
        self._match(self.alice)
        room_id = self._match(self.bob)['room']['id']

        self.auth(self.alice)
        response = self.client.post(f'/api/games/room/{room_id}/cancel/', {}, format='json')
        room_data = self.payload(response)['room']
        self.assertEqual(room_data['status'], 'cancelled')
        self.assertIsNone(room_data['result'])

        stats = self.payload(self.client.get('/api/games/stats/'))
        self.assertEqual(stats['pvp']['losses'], 0)
        self.assertEqual(stats['pvp']['wins'], 0)

    def test_third_user_cannot_join_or_read(self):
        self._match(self.alice)
        room_id = self._match(self.bob)['room']['id']

        carol = User.objects.create_user(username='carol', password='pass-12345')
        self.auth(carol)
        self.assertEqual(self.client.get(f'/api/games/room/{room_id}/').status_code, 403)
        self.assertEqual(
            self.client.post(f'/api/games/room/{room_id}/guess/', {'guess': '1234'}, format='json').status_code,
            403,
        )

    def test_guess_record_keeps_history(self):
        self._match(self.alice)
        room_id = self._match(self.bob)['room']['id']
        self.auth(self.alice)
        self.client.post(f'/api/games/room/{room_id}/secret/', {'secret': '1234'}, format='json')
        self.auth(self.bob)
        self.client.post(f'/api/games/room/{room_id}/secret/', {'secret': '5678'}, format='json')
        self.auth(self.alice)
        self.client.post(f'/api/games/room/{room_id}/guess/', {'guess': '1234'}, format='json')

        room = GameRoom.objects.get(pk=room_id)
        self.assertEqual(GameGuess.objects.filter(room=room).count(), 1)
        self.assertEqual(room.guesses.first().hits, 0)   # alice 猜 1234，bob 的秘密是 5678

    def test_invalid_guess_rejected(self):
        self.auth(self.alice)
        room_id = self.payload(self.client.post('/api/games/pve/', {'secret': '1234'}, format='json'))['room']['id']
        response = self.client.post(f'/api/games/room/{room_id}/guess/', {'guess': 'ab12'}, format='json')
        self.assertEqual(response.status_code, 400)
