"""
数字炸弹 - API 视图

接口一览（均需登录）：
- GET  /api/games/stats/                     战绩统计
- POST /api/games/pve/                        开始人机对战
- POST /api/games/match/                      匹配玩家对战（或加入等待队列）
- GET  /api/games/room/                       取当前进行中的对局（供轮询）
- GET  /api/games/room/<id>/                  取指定对局
- POST /api/games/room/<id>/secret/           设置自己的秘密数字
- POST /api/games/room/<id>/guess/            猜一次
- POST /api/games/room/<id>/cancel/           取消匹配 / 认输退出

说明：秘密数字只在服务端保存，任何接口都不会把它返回给对手。
"""

from datetime import timedelta

from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .game_engine import ComputerBrain, count_hits, is_valid_number, random_number
from .game_hints import get_opponent_hint
from .models import GameGuess, GameRoom
from .views import error_response, success_response

PVE = GameRoom.Mode.PVE
PVP = GameRoom.Mode.PVP

# 等待匹配的房间超过这个时间就视为过期
MATCH_TTL = timedelta(minutes=15)
# 一局对局里任何一方最多猜这么多次（防止恶意刷接口）
MAX_GUESSES_PER_SIDE = 200

ACTIVE_STATUSES = (GameRoom.Status.WAITING, GameRoom.Status.SETUP, GameRoom.Status.PLAYING)


# ========================================
# 序列化
# ========================================

def _username(user):
    if not user:
        return ''
    return getattr(user, 'username', '') or getattr(user, 'email', '') or f'用户{user.id}'


def serialize_room(room, user):
    """把对局序列化成前端需要的结构（绝不包含秘密数字）。"""
    my_side = room.side_of(user)
    opponent_side = 3 - my_side if my_side else None

    if room.is_pve:
        opponent = {'computer': True, 'username': '电脑'}
    else:
        opponent_user = room.player2 if my_side == 1 else room.player1
        opponent = (
            {'computer': False, 'id': opponent_user.id, 'username': _username(opponent_user)}
            if opponent_user else None
        )

    guesses = [
        {
            'side': guess.side,
            'guess': guess.guess,
            'hits': guess.hits,
            'is_mine': guess.side == my_side,
            'created_at': guess.created_at.isoformat(),
            # 只给对手的猜测配提示语；用记录 id 做种子，轮询时同一手始终同一句
            'hint': '' if guess.side == my_side else get_opponent_hint(guess.hits, guess.id),
        }
        for guess in room.guesses.all()
    ]

    my_guesses = [g for g in guesses if g['side'] == my_side]
    opponent_guesses = [g for g in guesses if g['side'] == opponent_side]

    duration = 0
    if room.started_at:
        finished = room.finished_at or timezone.now()
        duration = max(0, int((finished - room.started_at).total_seconds()))

    result = None
    if room.status == GameRoom.Status.FINISHED and room.winner_side:
        if room.is_pve:
            winner_name = '电脑' if room.winner_side == 2 else _username(room.player1)
        else:
            winner_user = room.player1 if room.winner_side == 1 else room.player2
            winner_name = _username(winner_user)
        result = {
            'winner_side': room.winner_side,
            'i_won': room.winner_side == my_side,
            'winner_name': winner_name,
        }

    return {
        'id': room.id,
        'mode': room.mode,
        'status': room.status,
        'my_side': my_side,
        'turn_side': room.turn,
        'my_turn': room.status == GameRoom.Status.PLAYING and room.turn == my_side,
        'me': {'id': user.id, 'username': _username(user)},
        'opponent': opponent,
        'my_secret': (room.p1_secret if my_side == 1 else room.p2_secret) or '',
        'opponent_secret': (
            (room.p2_secret if my_side == 1 else room.p1_secret) or ''
        ) if room.status == GameRoom.Status.FINISHED else '',
        'my_secret_set': bool(room.p1_secret if my_side == 1 else room.p2_secret),
        'opponent_secret_set': bool(room.p2_secret if my_side == 1 else room.p1_secret),
        'guesses': guesses,
        'my_guess_count': len(my_guesses),
        'opponent_guess_count': len(opponent_guesses),
        'result': result,
        'created_at': room.created_at.isoformat(),
        'started_at': room.started_at.isoformat() if room.started_at else None,
        'finished_at': room.finished_at.isoformat() if room.finished_at else None,
        'duration_seconds': duration,
    }


# ========================================
# 内部工具
# ========================================

def _active_room_of(user):
    """该用户当前未结束的对局。"""
    return (
        GameRoom.objects
        .filter(status__in=ACTIVE_STATUSES)
        .filter(Q(player1=user) | Q(player2=user))
        .order_by('-created_at')
        .first()
    )


def _get_room_for(user, room_id):
    """取对局并校验当前用户确实是参与者。"""
    room = GameRoom.objects.filter(pk=room_id).first()
    if room is None:
        return None, error_response('对局不存在', status.HTTP_404_NOT_FOUND)
    if room.side_of(user) is None:
        return None, error_response('无权访问该对局', status.HTTP_403_FORBIDDEN)
    return room, None


def _finish(room, winner_side):
    room.status = GameRoom.Status.FINISHED
    room.winner_side = winner_side
    room.finished_at = timezone.now()
    room.save(update_fields=['status', 'winner_side', 'finished_at', 'updated_at'])


def _computer_turn(room):
    """电脑走一步：推理 -> 记录 -> 判断是否获胜，返回本次猜测记录。"""
    brain = ComputerBrain()
    history = list(room.guesses.filter(side=2).values_list('guess', 'hits'))
    guess = brain.guess_for(history)
    hits = count_hits(room.p1_secret, guess)
    record = GameGuess.objects.create(room=room, side=2, player=None, guess=guess, hits=hits)
    if hits == 4:
        _finish(room, winner_side=2)
    return record


# ========================================
# 接口
# ========================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_pve(request):
    """开始人机对战。可同时带上自己的秘密数字直接开局。"""
    active = _active_room_of(request.user)
    if active:
        return error_response('你还有一局未结束，请先结束或取消', status.HTTP_409_CONFLICT)

    secret = request.data.get('secret')
    if secret is not None:
        secret = str(secret).strip()
        if not is_valid_number(secret):
            return error_response('秘密数字必须是 4 位数字（0000-9999）')

    room = GameRoom.objects.create(
        mode=PVE,
        status=GameRoom.Status.SETUP,
        player1=request.user,
        p2_secret=random_number(),
    )

    if secret:
        room.p1_secret = secret
        room.status = GameRoom.Status.PLAYING
        room.started_at = timezone.now()
        room.turn = 1
        room.save(update_fields=['p1_secret', 'status', 'started_at', 'turn', 'updated_at'])

    room.refresh_from_db()
    return success_response({'room': serialize_room(room, request.user)}, message='人机对战已开始')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def match_pvp(request):
    """匹配一名在线玩家；没有可匹配对象时进入等待队列。"""
    active = _active_room_of(request.user)
    if active:
        return success_response(
            {'room': serialize_room(active, request.user), 'matched': active.status != GameRoom.Status.WAITING},
            message='你已有一局进行中的对局',
        )

    cutoff = timezone.now() - MATCH_TTL
    with transaction.atomic():
        # 过期未配对的等待房间先作废，避免配到“幽灵”对手
        GameRoom.objects.filter(
            mode=PVP, status=GameRoom.Status.WAITING, updated_at__lt=cutoff
        ).update(status=GameRoom.Status.CANCELLED, finished_at=timezone.now())

        waiting = (
            GameRoom.objects
            .select_for_update()
            .filter(mode=PVP, status=GameRoom.Status.WAITING, updated_at__gte=cutoff)
            .exclude(player1=request.user)
            .order_by('created_at')
            .first()
        )

        if waiting:
            waiting.player2 = request.user
            waiting.status = GameRoom.Status.SETUP
            waiting.save(update_fields=['player2', 'status', 'updated_at'])
            return success_response(
                {'room': serialize_room(waiting, request.user), 'matched': True},
                message='匹配成功，开始设置数字',
            )

        room = GameRoom.objects.create(
            mode=PVP, status=GameRoom.Status.WAITING, player1=request.user
        )

    return success_response(
        {'room': serialize_room(room, request.user), 'matched': False},
        message='正在等待对手加入',
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_room(request):
    """当前进行中的对局（前端每 2 秒轮询一次）。"""
    room = _active_room_of(request.user)
    if room is None:
        return success_response({'room': None})
    return success_response({'room': serialize_room(room, request.user)})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def room_detail(request, room_id):
    room, error = _get_room_for(request.user, room_id)
    if error:
        return error
    return success_response({'room': serialize_room(room, request.user)})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def set_secret(request, room_id):
    """设置自己的秘密数字；双方都设置好后自动开局。"""
    secret = str(request.data.get('secret', '')).strip()
    if not is_valid_number(secret):
        return error_response('秘密数字必须是 4 位数字（0000-9999）')

    with transaction.atomic():
        room = GameRoom.objects.select_for_update().filter(pk=room_id).first()
        if room is None:
            return error_response('对局不存在', status.HTTP_404_NOT_FOUND)

        side = room.side_of(request.user)
        if side is None:
            return error_response('无权访问该对局', status.HTTP_403_FORBIDDEN)
        if room.status not in (GameRoom.Status.SETUP, GameRoom.Status.WAITING):
            return error_response('当前状态不能设置数字', status.HTTP_409_CONFLICT)

        if side == 1:
            room.p1_secret = secret
        else:
            room.p2_secret = secret

        update_fields = ['p1_secret', 'p2_secret', 'status', 'started_at', 'turn', 'updated_at']
        if room.p1_secret and room.p2_secret:
            room.status = GameRoom.Status.PLAYING
            room.started_at = timezone.now()
            room.turn = 1
        room.save(update_fields=update_fields)

    room.refresh_from_db()
    return success_response({'room': serialize_room(room, request.user)}, message='数字已设置')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def make_guess(request, room_id):
    """猜一次；人机对战时电脑会在同一次请求里立刻反猜。"""
    guess = str(request.data.get('guess', '')).strip()
    if not is_valid_number(guess):
        return error_response('请输入 4 位数字（0000-9999）')

    new_guesses = []
    with transaction.atomic():
        room = GameRoom.objects.select_for_update().filter(pk=room_id).first()
        if room is None:
            return error_response('对局不存在', status.HTTP_404_NOT_FOUND)

        my_side = room.side_of(request.user)
        if my_side is None:
            return error_response('无权访问该对局', status.HTTP_403_FORBIDDEN)
        if room.status != GameRoom.Status.PLAYING:
            return error_response('对局不在进行中', status.HTTP_409_CONFLICT)
        if room.turn != my_side:
            return error_response('还没轮到你猜', status.HTTP_409_CONFLICT)

        if room.guesses.filter(side=my_side).count() >= MAX_GUESSES_PER_SIDE:
            return error_response('猜测次数过多，本局已结束', status.HTTP_429_TOO_MANY_REQUESTS)

        opponent_secret = room.opponent_secret(my_side)
        if not opponent_secret:
            return error_response('对局数据异常：对手还没有设置数字', status.HTTP_409_CONFLICT)

        hits = count_hits(opponent_secret, guess)
        record = GameGuess.objects.create(
            room=room, side=my_side, player=request.user, guess=guess, hits=hits
        )
        new_guesses.append(record)

        if hits == 4:
            _finish(room, winner_side=my_side)
        elif room.is_pve:
            # 人机：玩家猜完，电脑立刻反猜
            new_guesses.append(_computer_turn(room))
        else:
            room.turn = 3 - my_side
            room.save(update_fields=['turn', 'updated_at'])

    room.refresh_from_db()
    return success_response(
        {
            'room': serialize_room(room, request.user),
            'results': [
                {'side': item.side, 'guess': item.guess, 'hits': item.hits} for item in new_guesses if item
            ],
        },
        message='猜中啦！' if room.status == GameRoom.Status.FINISHED else '继续猜',
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_room(request, room_id):
    """取消匹配；对局中调用则视为认输。"""
    with transaction.atomic():
        room = GameRoom.objects.select_for_update().filter(pk=room_id).first()
        if room is None:
            return error_response('对局不存在', status.HTTP_404_NOT_FOUND)

        my_side = room.side_of(request.user)
        if my_side is None:
            return error_response('无权访问该对局', status.HTTP_403_FORBIDDEN)
        if room.status in (GameRoom.Status.FINISHED, GameRoom.Status.CANCELLED):
            return error_response('对局已经结束了', status.HTTP_409_CONFLICT)

        was_waiting = room.status == GameRoom.Status.WAITING
        if was_waiting or (room.status == GameRoom.Status.SETUP and room.started_at is None):
            # 还没真正开打，直接作废，不判胜负
            room.status = GameRoom.Status.CANCELLED
            room.finished_at = timezone.now()
            room.save(update_fields=['status', 'finished_at', 'updated_at'])
            message = '已取消匹配' if was_waiting else '已退出对局'
        else:
            # 认输：对手获胜
            room.status = GameRoom.Status.FINISHED
            room.winner_side = 3 - my_side
            room.finished_at = timezone.now()
            room.save(update_fields=['status', 'winner_side', 'finished_at', 'updated_at'])
            message = '你已认输，本局结束'

    room.refresh_from_db()
    return success_response({'room': serialize_room(room, request.user)}, message=message)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def game_stats(request):
    """战绩统计：人机 / 玩家对战分开统计，并给出最近几局。"""
    user = request.user

    def summarize(rooms):
        wins = losses = 0
        best = None
        for room in rooms:
            my_side = room.side_of(user)
            if not my_side or not room.winner_side:
                continue
            if room.winner_side == my_side:
                wins += 1
                count = room.guesses.filter(side=my_side).count()
                best = count if best is None else min(best, count)
            else:
                losses += 1
        return {'wins': wins, 'losses': losses, 'total': wins + losses, 'best_guesses': best}

    pve_rooms = list(GameRoom.objects.filter(mode=PVE, player1=user, status=GameRoom.Status.FINISHED))
    pvp_rooms = list(
        GameRoom.objects.filter(mode=PVP, status=GameRoom.Status.FINISHED)
        .filter(Q(player1=user) | Q(player2=user))
    )

    recent = []
    for room in sorted(pve_rooms + pvp_rooms, key=lambda r: r.created_at, reverse=True)[:8]:
        my_side = room.side_of(user)
        opponent_user = room.player2 if my_side == 1 else room.player1
        recent.append({
            'id': room.id,
            'mode': room.mode,
            'i_won': room.winner_side == my_side,
            'opponent': '电脑' if room.is_pve else _username(opponent_user),
            'my_guesses': room.guesses.filter(side=my_side).count(),
            'finished_at': room.finished_at.isoformat() if room.finished_at else None,
        })

    return success_response({
        'pve': summarize(pve_rooms),
        'pvp': summarize(pvp_rooms),
        'recent': recent,
    })
