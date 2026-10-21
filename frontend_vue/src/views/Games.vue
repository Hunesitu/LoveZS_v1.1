<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import dayjs from 'dayjs'
import {
  Bot,
  Check,
  Flame,
  Hourglass,
  Loader2,
  RotateCcw,
  Shuffle,
  Swords,
  Trophy,
  Users,
} from 'lucide-vue-next'
import {
  cancelRoom,
  getCurrentRoom,
  getGameStats,
  getRoom,
  matchPvp,
  startPve,
  submitGuess,
  submitSecret,
  type GameDifficulty,
  type GameRoomData,
  type GameStats,
} from '@/api/games'
import { useUiStore } from '@/stores/ui'

const uiStore = useUiStore()

const DIFFICULTY_OPTIONS: Array<{
  value: GameDifficulty
  label: string
  desc: string
}> = [
  { value: 'easy', label: '简单', desc: '电脑常常走神乱猜' },
  { value: 'normal', label: '普通', desc: '偶尔失手，通常 10 轮' },
  { value: 'hard', label: '困难', desc: '每步都算，约 9 轮' },
]

const DIFFICULTY_LABEL: Record<GameDifficulty, string> = {
  easy: '简单',
  normal: '普通',
  hard: '困难',
}

const room = ref<GameRoomData | null>(null)
const resumeRoom = ref<GameRoomData | null>(null)
const stats = ref<GameStats | null>(null)
const loading = ref(true)
const busy = ref(false)
const pveSetup = ref(false)
const difficulty = ref<GameDifficulty>('normal')
const secretInput = ref('')
const guessInput = ref('')
const tick = ref(Date.now())
const feedback = ref<{ hits: number; guess: string; key: number } | null>(null)
const oppFeedback = ref<{ hits: number; guess: string; hint: string; key: number } | null>(null)

let pollTimer: number | null = null
let clockTimer: number | null = null
let feedbackTimer: number | null = null
let oppFeedbackTimer: number | null = null

const screen = computed(() => {
  if (!room.value) return pveSetup.value ? 'pve-setup' : 'lobby'
  if (room.value.status === 'waiting') return 'waiting'
  if (room.value.status === 'setup') return 'setup'
  if (room.value.status === 'playing') return 'playing'
  if (room.value.status === 'finished') return 'finished'
  return 'lobby'
})

const isPve = computed(() => room.value?.mode === 'pve')
const opponentName = computed(() => room.value?.opponent?.username || '对手')

const myGuesses = computed(() => (room.value?.guesses || []).filter((item) => item.is_mine).slice().reverse())
const opponentGuesses = computed(() =>
  (room.value?.guesses || []).filter((item) => !item.is_mine).slice().reverse(),
)

const elapsed = computed(() => {
  if (!room.value?.started_at) return '0:00'
  const start = new Date(room.value.started_at).getTime()
  const end = room.value.finished_at ? new Date(room.value.finished_at).getTime() : tick.value
  const seconds = Math.max(0, Math.floor((end - start) / 1000))
  const minutes = Math.floor(seconds / 60)
  return `${minutes}:${String(seconds % 60).padStart(2, '0')}`
})

const canGuess = computed(() => room.value?.status === 'playing' && room.value?.my_turn)

const isValidSecret = (value: string) => /^\d{4}$/.test(value)

const formatDate = (value: string | null) => {
  if (!value) return ''
  const date = dayjs(value)
  if (!date.isValid()) return ''
  const today = dayjs()
  if (date.isSame(today, 'day')) return '今天'
  if (date.isSame(today.subtract(1, 'day'), 'day')) return '昨天'
  // 跨年时才带上年份，其余只显示日期
  return date.isSame(today, 'year') ? date.format('M月D日') : date.format('YYYY年M月D日')
}

// ========================================
// 轮询
// ========================================

const stopPolling = () => {
  if (pollTimer !== null) {
    window.clearInterval(pollTimer)
    pollTimer = null
  }
}

const showOppFeedback = (hits: number, guess: string, hint = '') => {
  oppFeedback.value = { hits, guess, hint, key: Date.now() }
  if (oppFeedbackTimer !== null) window.clearTimeout(oppFeedbackTimer)
  oppFeedbackTimer = window.setTimeout(() => {
    oppFeedback.value = null
  }, hint ? 3200 : 2600)
}

/**
 * 统一更新对局数据：如果是同一局、且对手新增了猜测，就弹一条「对方猜对几个」。
 */
const applyRoom = (next: GameRoomData) => {
  const previous = room.value
  const sameRoom = previous?.id === next.id
  const prevOppCount = previous?.opponent_guess_count ?? 0

  room.value = next

  if (sameRoom && next.opponent_guess_count > prevOppCount) {
    const latestOpp = [...next.guesses].reverse().find((item) => !item.is_mine)
    if (latestOpp) showOppFeedback(latestOpp.hits, latestOpp.guess, latestOpp.hint)
  }
}

const refreshRoom = async () => {
  if (!room.value) return
  try {
    const { room: latest } = await getRoom(room.value.id)
    applyRoom(latest)
    if (latest.status === 'finished' || latest.status === 'cancelled') {
      stopPolling()
      if (latest.status === 'cancelled') {
        room.value = null
        uiStore.showToast('对局已结束', 'info')
      } else {
        loadStats()
      }
    }
  } catch (error) {
    console.warn('刷新对局失败', error)
  }
}

const startPolling = () => {
  stopPolling()
  pollTimer = window.setInterval(refreshRoom, 2000)
}

// ========================================
// 数据
// ========================================

const loadStats = async () => {
  try {
    stats.value = await getGameStats()
  } catch (error) {
    console.warn('加载战绩失败', error)
  }
}

const boot = async () => {
  loading.value = true
  try {
    const { room: current } = await getCurrentRoom()
    // 默认停在选玩法的大厅；有未结束的对局时给一张「继续」卡片，而不是直接把人拽进对局
    resumeRoom.value = current && current.status !== 'finished' ? current : null
  } catch (error) {
    console.warn('加载对局失败', error)
  } finally {
    loading.value = false
    loadStats()
  }
}

const continueRoom = () => {
  if (!resumeRoom.value) return
  room.value = resumeRoom.value
  resumeRoom.value = null
  if (room.value.status === 'playing' || room.value.status === 'waiting' || room.value.status === 'setup') {
    startPolling()
  }
}

const abandonResumeRoom = async () => {
  if (!resumeRoom.value) return
  const target = resumeRoom.value
  const ok = target.status === 'playing'
    ? window.confirm('这局还没打完，放弃会判你认输，确定吗？')
    : true
  if (!ok) return
  busy.value = true
  try {
    await cancelRoom(target.id)
  } catch (error) {
    console.warn('放弃对局失败', error)
  } finally {
    busy.value = false
    resumeRoom.value = null
    loadStats()
  }
}

// ========================================
// 操作
// ========================================

const randomSecret = () => {
  secretInput.value = String(Math.floor(Math.random() * 10000)).padStart(4, '0')
}

const beginPve = async () => {
  if (busy.value) return
  const secret = secretInput.value.trim()
  if (!isValidSecret(secret)) {
    uiStore.showToast('请输入 4 位数字（0000-9999）', 'warning')
    return
  }
  busy.value = true
  try {
    const { room: created } = await startPve(secret, difficulty.value)
    room.value = created
    pveSetup.value = false
    secretInput.value = ''
    startPolling()
    uiStore.showToast(`开局！${DIFFICULTY_LABEL[difficulty.value]}难度，先猜电脑的数字`, 'success')
  } catch (error: any) {
    uiStore.showToast(error?.response?.data?.message || '开局失败，请重试', 'error')
  } finally {
    busy.value = false
  }
}

const findOpponent = async () => {
  if (busy.value) return
  busy.value = true
  try {
    const { room: matchedRoom, matched } = await matchPvp()
    room.value = matchedRoom
    startPolling()
    uiStore.showToast(matched ? '匹配成功，设置你的数字' : '已进入匹配队列，等待对手…', 'success')
  } catch (error: any) {
    uiStore.showToast(error?.response?.data?.message || '匹配失败，请重试', 'error')
  } finally {
    busy.value = false
  }
}

const confirmSecret = async () => {
  if (busy.value || !room.value) return
  const secret = secretInput.value.trim()
  if (!isValidSecret(secret)) {
    uiStore.showToast('请输入 4 位数字（0000-9999）', 'warning')
    return
  }
  busy.value = true
  try {
    const { room: updated } = await submitSecret(room.value.id, secret)
    room.value = updated
    secretInput.value = ''
    if (updated.status === 'playing') {
      uiStore.showToast('双方已就位，开始猜！', 'success')
      startPolling()
    } else {
      uiStore.showToast('已出题，等待对手设置数字…', 'success')
    }
  } catch (error: any) {
    uiStore.showToast(error?.response?.data?.message || '设置失败，请重试', 'error')
  } finally {
    busy.value = false
  }
}

const showFeedback = (hits: number, guess: string) => {
  feedback.value = { hits, guess, key: Date.now() }
  if (feedbackTimer !== null) window.clearTimeout(feedbackTimer)
  feedbackTimer = window.setTimeout(() => {
    feedback.value = null
  }, hits === 4 ? 1800 : 1400)
}

const sendGuess = async () => {
  if (busy.value || !room.value) return
  const guess = guessInput.value.trim()
  if (!isValidSecret(guess)) {
    uiStore.showToast('请输入 4 位数字（0000-9999）', 'warning')
    return
  }
  busy.value = true
  try {
    const { room: updated, results } = await submitGuess(room.value.id, guess)
    applyRoom(updated)
    guessInput.value = ''

    const mine = results.find((item) => item.side === updated.my_side) || { side: updated.my_side, guess, hits: 0 }
    showFeedback(mine.hits, mine.guess)

    if (updated.status === 'finished') {
      stopPolling()
      loadStats()
      uiStore.showToast(updated.result?.i_won ? '你赢了！' : '这局输了，再来一局？', updated.result?.i_won ? 'success' : 'warning')
    }
  } catch (error: any) {
    uiStore.showToast(error?.response?.data?.message || '出错了，请重试', 'error')
  } finally {
    busy.value = false
  }
}

const leaveRoom = async (resign = true) => {
  const current = room.value
  if (!current) return
  if (resign && current.status === 'playing') {
    const ok = window.confirm('对局还没结束，退出将视为认输，确定吗？')
    if (!ok) return
  }
  busy.value = true
  try {
    if (['waiting', 'setup', 'playing'].includes(current.status)) {
      await cancelRoom(current.id)
    }
  } catch (error) {
    console.warn('退出对局失败', error)
  } finally {
    busy.value = false
    stopPolling()
    room.value = null
    pveSetup.value = false
    secretInput.value = ''
    guessInput.value = ''
    loadStats()
  }
}

const backToLobby = () => {
  stopPolling()
  room.value = null
  pveSetup.value = false
  guessInput.value = ''
  loadStats()
}

const openPveSetup = () => {
  pveSetup.value = true
  secretInput.value = ''
}

const playAgain = () => {
  const mode = room.value?.mode
  stopPolling()
  room.value = null
  guessInput.value = ''
  secretInput.value = ''
  loadStats()
  if (mode === 'pvp') {
    findOpponent()
  } else {
    pveSetup.value = true
  }
}

// ========================================
// 生命周期
// ========================================

onMounted(() => {
  boot()
  clockTimer = window.setInterval(() => {
    tick.value = Date.now()
  }, 1000)
})

onUnmounted(() => {
  stopPolling()
  if (clockTimer !== null) window.clearInterval(clockTimer)
  if (feedbackTimer !== null) window.clearTimeout(feedbackTimer)
  if (oppFeedbackTimer !== null) window.clearTimeout(oppFeedbackTimer)
})
</script>

<template>
  <div class="games-page">
    <div v-if="loading" class="loading-state">
      <Loader2 :size="26" class="spin" />
      <span>加载中…</span>
    </div>

    <!-- ================= 大厅 ================= -->
    <template v-else-if="screen === 'lobby'">
      <header class="hero">
        <p class="eyebrow"><Flame :size="14" /> MINI GAME</p>
        <h1>数字炸弹</h1>
        <p class="lede">
          各自想一个 4 位数，轮流猜对方的数字。每次只告诉你“位置和数字都对的有几个”，
          先猜中 4 个的人赢。
        </p>
      </header>

      <section v-if="resumeRoom" class="resume-card">
        <div class="resume-info">
          <span class="resume-tag">{{ resumeRoom.mode === 'pve' ? '人机对战' : '玩家对战' }}</span>
          <span class="resume-text">
            你有一局还没结束：对手 {{ resumeRoom.opponent?.username || '电脑' }}，已猜 {{ resumeRoom.my_guess_count }} 次
          </span>
        </div>
        <div class="resume-actions">
          <button class="primary-btn" type="button" :disabled="busy" @click="continueRoom">继续这局</button>
          <button class="link-btn" type="button" :disabled="busy" @click="abandonResumeRoom">放弃并重开</button>
        </div>
      </section>

      <div class="lobby-head">
        <h2>选择玩法</h2>
        <p>第一次玩？人机对战可以先熟悉规则，玩家对战需要另一个人同时在线。</p>
      </div>

      <div class="mode-grid">
        <button class="mode-card pve" type="button" :disabled="busy || !!resumeRoom" @click="openPveSetup">
          <span class="mode-icon"><Bot :size="22" /></span>
          <span class="mode-title">人机对战</span>
          <span class="mode-desc">你出一个数，电脑也出一个数，轮流猜，先猜中者胜。</span>
          <span class="mode-cta">开始 <Swords :size="14" /></span>
        </button>

        <button class="mode-card pvp" type="button" :disabled="busy || !!resumeRoom" @click="findOpponent">
          <span class="mode-icon"><Users :size="22" /></span>
          <span class="mode-title">玩家对战</span>
          <span class="mode-desc">匹配另一位在线玩家，各自出题互相猜，先猜中者胜。</span>
          <span class="mode-cta">匹配 <Loader2 v-if="busy" :size="14" class="spin" /><Users v-else :size="14" /></span>
        </button>
      </div>

      <p v-if="resumeRoom" class="resume-hint">先继续或放弃上面那局，才能开新的一局。</p>

      <section v-if="stats" class="stats-panel">
        <div class="stat-card">
          <span class="stat-label"><Bot :size="14" /> 人机</span>
          <span class="stat-value">{{ stats.pve.wins }}<em>胜</em> {{ stats.pve.losses }}<em>负</em></span>
          <span class="stat-sub">共 {{ stats.pve.total }} 局<template v-if="stats.pve.best_guesses"> · 最好 {{ stats.pve.best_guesses }} 次猜中</template></span>
        </div>
        <div class="stat-card">
          <span class="stat-label"><Users :size="14" /> 玩家对战</span>
          <span class="stat-value">{{ stats.pvp.wins }}<em>胜</em> {{ stats.pvp.losses }}<em>负</em></span>
          <span class="stat-sub">共 {{ stats.pvp.total }} 局<template v-if="stats.pvp.best_guesses"> · 最好 {{ stats.pvp.best_guesses }} 次猜中</template></span>
        </div>
      </section>

      <section v-if="stats && stats.recent.length" class="recent-panel">
        <h2><Trophy :size="16" /> 最近对局</h2>
        <ul>
          <li v-for="item in stats.recent" :key="item.id">
            <span class="recent-mode">{{ item.mode === 'pve' ? '人机' : '对战' }}</span>
            <span class="recent-opponent">vs {{ item.opponent }}</span>
            <span class="recent-date">{{ formatDate(item.finished_at) }}</span>
            <span class="recent-result" :class="item.i_won ? 'win' : 'lose'">{{ item.i_won ? '胜' : '负' }}</span>
            <span class="recent-guesses">{{ item.my_guesses }} 次</span>
          </li>
        </ul>
      </section>
    </template>

    <!-- ================= 人机：设置数字 ================= -->
    <template v-else-if="screen === 'pve-setup'">
      <div class="screen-bar">
        <button class="link-btn" type="button" @click="backToLobby">← 玩法选择</button>
        <span class="mode-tag">人机对战</span>
      </div>
      <section class="panel setup-panel">
        <h1>出个题</h1>
        <p class="panel-sub">想一个 4 位数字（0000–9999，可以以 0 开头），让电脑来猜。别告诉它。</p>

        <div class="difficulty-row" role="radiogroup" aria-label="电脑难度">
          <button
            v-for="item in DIFFICULTY_OPTIONS"
            :key="item.value"
            type="button"
            class="difficulty-option"
            :class="{ active: difficulty === item.value }"
            role="radio"
            :aria-checked="difficulty === item.value"
            @click="difficulty = item.value"
          >
            <span class="difficulty-name">{{ item.label }}</span>
            <span class="difficulty-desc">{{ item.desc }}</span>
          </button>
        </div>

        <div class="secret-row">
          <input
            v-model="secretInput"
            class="secret-input"
            type="text"
            inputmode="numeric"
            maxlength="4"
            placeholder="0000"
            @keyup.enter="beginPve"
          />
          <button class="ghost-btn" type="button" @click="randomSecret"><Shuffle :size="15" /> 随机一个</button>
        </div>

        <button class="primary-btn" type="button" :disabled="busy" @click="beginPve">
          <Loader2 v-if="busy" :size="16" class="spin" />
          <span>{{ busy ? '开局中…' : '开始对战' }}</span>
        </button>
        <button class="link-btn" type="button" @click="backToLobby">返回大厅</button>
      </section>
    </template>

    <!-- ================= 等待匹配 ================= -->
    <template v-else-if="screen === 'waiting'">
      <section class="panel waiting-panel">
        <div class="radar">
          <span class="pulse" />
          <Hourglass :size="30" />
        </div>
        <h1>正在寻找对手…</h1>
        <p class="panel-sub">另一位在线玩家点击“玩家对战”时就会和你匹配上。</p>
        <button class="ghost-btn" type="button" :disabled="busy" @click="leaveRoom(false)">取消匹配</button>
      </section>
    </template>

    <!-- ================= 玩家对战：设置数字 ================= -->
    <template v-else-if="screen === 'setup'">
      <div class="screen-bar">
        <button class="link-btn" type="button" @click="leaveRoom(false)">← 玩法选择</button>
        <span class="mode-tag">玩家对战</span>
      </div>

      <section class="panel setup-panel">
        <p class="match-badge"><Check :size="14" /> 已匹配到 {{ opponentName }}</p>
        <h1>想一个数字</h1>
        <p class="panel-sub">你和对手各想一个 4 位数，互相来猜。双方都出好题后自动开始。</p>

        <div v-if="room?.my_secret_set" class="waiting-hint">
          <Loader2 :size="16" class="spin" />
          你的数字是 <strong>{{ room.my_secret }}</strong>，等待 {{ opponentName }} 出题…
        </div>

        <template v-else>
          <div class="secret-row">
            <input
              v-model="secretInput"
              class="secret-input"
              type="text"
              inputmode="numeric"
              maxlength="4"
              placeholder="0000"
              @keyup.enter="confirmSecret"
            />
            <button class="ghost-btn" type="button" @click="randomSecret"><Shuffle :size="15" /> 随机一个</button>
          </div>
          <button class="primary-btn" type="button" :disabled="busy" @click="confirmSecret">
            <Loader2 v-if="busy" :size="16" class="spin" />
            <span>{{ busy ? '提交中…' : '就是这个数' }}</span>
          </button>
        </template>
      </section>
    </template>

    <!-- ================= 对局中 ================= -->
    <template v-else-if="screen === 'playing' && room">
      <div class="screen-bar">
        <button class="link-btn" type="button" @click="leaveRoom(true)">← 玩法选择</button>
        <span class="mode-tag">
          {{ isPve ? `人机对战 · ${DIFFICULTY_LABEL[room.difficulty]}` : '玩家对战' }}
        </span>
      </div>

      <section class="game-head">
        <div class="player-card me" :class="{ active: room.my_turn }">
          <span class="player-role">你</span>
          <span class="player-name">{{ room.me.username }}</span>
          <span class="player-count">{{ room.my_guess_count }} 次</span>
        </div>
        <div class="versus">
          <Swords :size="18" />
          <span>{{ elapsed }}</span>
        </div>
        <div class="player-card opponent" :class="{ active: !room.my_turn }">
          <span class="player-role">{{ isPve ? '电脑' : '对手' }}</span>
          <span class="player-name">{{ opponentName }}</span>
          <span class="player-count">{{ room.opponent_guess_count }} 次</span>
        </div>
      </section>

      <p class="turn-banner" :class="{ mine: room.my_turn }">
        <template v-if="room.my_turn">轮到你猜 {{ opponentName }} 的数字</template>
        <template v-else>等待 {{ opponentName }} 出招…</template>
      </p>

      <div class="secret-reminder">
        你的数字：<strong>{{ room.my_secret }}</strong>
      </div>

      <form class="guess-form" @submit.prevent="sendGuess">
        <input
          v-model="guessInput"
          class="guess-input"
          type="text"
          inputmode="numeric"
          maxlength="4"
          placeholder="输入 4 位数"
          :disabled="!canGuess || busy"
        />
        <button class="primary-btn" type="submit" :disabled="!canGuess || busy">
          <Loader2 v-if="busy" :size="16" class="spin" />
          <span v-else>猜</span>
        </button>
      </form>

      <div class="boards">
        <section class="board">
          <h2>我的猜测</h2>
          <p v-if="!myGuesses.length" class="empty">还没猜过</p>
          <ul v-else>
            <li v-for="(item, index) in myGuesses" :key="`mine-${index}`">
              <span class="digits">{{ item.guess }}</span>
              <span class="hits" :class="{ perfect: item.hits === 4 }">{{ item.hits }} / 4</span>
            </li>
          </ul>
        </section>

        <section class="board">
          <h2>{{ opponentName }} 的猜测</h2>
          <p v-if="!opponentGuesses.length" class="empty">还没出手</p>
          <ul v-else>
            <li v-for="(item, index) in opponentGuesses" :key="`opp-${index}`">
              <span class="digits">{{ item.guess }}</span>
              <span class="hits" :class="{ perfect: item.hits === 4 }">{{ item.hits }} / 4</span>
            </li>
          </ul>
        </section>
      </div>

      <p class="foot-hint">想换玩法？点右上角「玩法选择」，正在进行的对局会判你认输。</p>
    </template>

    <!-- ================= 结算 ================= -->
    <template v-else-if="screen === 'finished' && room">
      <section class="panel result-panel" :class="room.result?.i_won ? 'win' : 'lose'">
        <span class="result-icon">
          <Trophy v-if="room.result?.i_won" :size="34" />
          <Flame v-else :size="34" />
        </span>
        <h1>{{ room.result?.i_won ? '你赢了' : '这局输了' }}</h1>
        <p class="panel-sub">
          {{ room.result?.winner_name }} 先猜中。
          你一共猜了 {{ room.my_guess_count }} 次，用时 {{ elapsed }}。
        </p>

        <div class="result-secret">
          对方的数字：<strong>{{ room.opponent_secret || '—' }}</strong>
        </div>

        <div class="result-actions">
          <button class="primary-btn" type="button" @click="playAgain"><RotateCcw :size="16" /> 再来一局</button>
          <button class="ghost-btn" type="button" @click="backToLobby">返回大厅</button>
        </div>
      </section>
    </template>

    <!-- ================= 猜测结果动画 ================= -->
    <Transition name="feedback">
      <div v-if="feedback" :key="feedback.key" class="feedback-overlay" aria-live="polite">
        <div
          class="feedback-card"
          :class="{ zero: feedback.hits === 0, perfect: feedback.hits === 4 }"
        >
          <span class="feedback-num">{{ feedback.hits }}</span>
          <span class="feedback-label">
            <template v-if="feedback.hits === 0">一个都没对</template>
            <template v-else-if="feedback.hits === 4">全中！</template>
            <template v-else>猜对 {{ feedback.hits }} 个</template>
          </span>
          <span class="feedback-guess">{{ feedback.guess }}</span>
        </div>
      </div>
    </Transition>
    <!-- ================= 对手猜测提示 ================= -->
    <Transition name="opp">
      <div v-if="oppFeedback" :key="oppFeedback.key" class="opp-feedback">
        <div class="opp-line">
          <span class="opp-who">{{ opponentName }} 猜了 {{ oppFeedback.guess }}</span>
          <span
            class="opp-hits"
            :class="{ zero: oppFeedback.hits === 0, perfect: oppFeedback.hits === 4 }"
          >
            {{ oppFeedback.hits === 0 ? '一个都没对' : `猜对 ${oppFeedback.hits} 个` }}
          </span>
        </div>
        <p v-if="oppFeedback.hint" class="opp-hint">{{ oppFeedback.hint }}</p>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.games-page {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  max-width: 1080px;
  margin: 0 auto;
  padding: clamp(1rem, 3vw, 2rem) 0 3rem;
}

.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.6rem;
  padding: 4rem 0;
  color: var(--ink-muted);
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* ---------- 大厅 ---------- */
.hero {
  padding: 0.5rem 0 0.25rem;
}

.eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  margin: 0 0 0.65rem;
  color: var(--gold);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.22em;
}

.hero h1 {
  margin: 0 0 0.5rem;
  font-family: var(--font-serif);
  font-size: clamp(1.9rem, 4vw, 2.6rem);
  font-weight: 600;
  color: var(--ink);
  letter-spacing: 0.02em;
}

.lede {
  max-width: 46rem;
  margin: 0;
  color: var(--ink-soft);
  font-size: 0.92rem;
  line-height: 1.75;
}

.mode-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 1rem;
}

.lobby-head {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  margin-top: 0.35rem;
}

.lobby-head h2 {
  margin: 0;
  color: var(--ink);
  font-size: 1rem;
  font-weight: 700;
}

.lobby-head p {
  margin: 0;
  color: var(--ink-muted);
  font-size: 0.82rem;
}

.screen-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  padding: 0 0.1rem;
}

.resume-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
  padding: 1rem 1.25rem;
  border: 1px solid var(--line-strong);
  border-radius: var(--radius-lg);
  background: linear-gradient(135deg, rgba(239, 111, 169, 0.14), rgba(139, 104, 255, 0.1));
}

.resume-info {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  flex-wrap: wrap;
}

.resume-tag {
  padding: 0.18rem 0.6rem;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.1);
  color: var(--ink);
  font-size: 0.72rem;
}

.resume-text {
  color: var(--ink-soft);
  font-size: 0.85rem;
}

.resume-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.resume-actions .primary-btn {
  min-width: auto;
  padding: 0.55rem 1rem;
  font-size: 0.82rem;
}

.resume-hint {
  margin: -0.35rem 0 0;
  color: var(--ink-dim);
  font-size: 0.78rem;
}

.mode-tag {
  padding: 0.2rem 0.65rem;
  border: 1px solid var(--line);
  border-radius: 999px;
  color: var(--ink-muted);
  font-size: 0.72rem;
  letter-spacing: 0.06em;
}

.foot-hint {
  margin: 0.2rem 0 0;
  color: var(--ink-dim);
  font-size: 0.76rem;
  text-align: center;
}

.mode-card {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.5rem;
  padding: 1.4rem;
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  background: linear-gradient(160deg, rgba(35, 22, 45, 0.9), rgba(14, 10, 20, 0.94));
  color: var(--ink);
  text-align: left;
  cursor: pointer;
  transition: transform var(--dur-base) ease, border-color var(--dur-base) ease, box-shadow var(--dur-base) ease;
}

.mode-card:hover:not(:disabled) {
  transform: translateY(-2px);
  border-color: var(--line-strong);
  box-shadow: var(--shadow-glow);
}

.mode-card:disabled {
  opacity: 0.6;
  cursor: progress;
}

.mode-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 42px;
  height: 42px;
  border-radius: 12px;
  color: var(--rose-bright);
  background: var(--rose-soft);
}

.mode-card.pvp .mode-icon {
  color: var(--gold);
  background: var(--gold-soft);
}

.mode-title {
  font-size: 1.1rem;
  font-weight: 700;
}

.mode-desc {
  color: var(--ink-muted);
  font-size: 0.85rem;
  line-height: 1.6;
}

.mode-cta {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  margin-top: 0.4rem;
  color: var(--rose-bright);
  font-size: 0.82rem;
  font-weight: 700;
}

.stats-panel {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 0.85rem;
}

.stat-card {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  padding: 1rem 1.15rem;
  border: 1px solid var(--line);
  border-radius: var(--radius-md);
  background: var(--panel-soft);
}

.stat-label {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  color: var(--ink-muted);
  font-size: 0.78rem;
}

.stat-value {
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--ink);
}

.stat-value em {
  margin: 0 0.2rem 0 0.1rem;
  color: var(--ink-muted);
  font-size: 0.75rem;
  font-style: normal;
  font-weight: 500;
}

.stat-sub {
  color: var(--ink-dim);
  font-size: 0.76rem;
}

.recent-panel {
  padding: 1.1rem 1.25rem;
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  background: var(--panel-soft);
}

.recent-panel h2 {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  margin: 0 0 0.75rem;
  color: var(--ink-soft);
  font-size: 0.9rem;
  font-weight: 600;
}

.recent-panel ul {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
  margin: 0;
  padding: 0;
  list-style: none;
}

.recent-panel li {
  display: grid;
  grid-template-columns: 3rem minmax(0, 1fr) auto 1.5rem 3rem;
  align-items: center;
  gap: 0.5rem;
  padding: 0.45rem 0.6rem;
  border-radius: var(--radius-sm);
  background: rgba(255, 255, 255, 0.03);
  font-size: 0.82rem;
  color: var(--ink-soft);
}

.recent-date {
  color: var(--ink-dim);
  font-size: 0.72rem;
  white-space: nowrap;
  font-variant-numeric: tabular-nums;
}

.recent-mode {
  color: var(--ink-muted);
  font-size: 0.75rem;
}

.recent-result.win {
  color: var(--success);
  font-weight: 700;
}

.recent-result.lose {
  color: var(--danger);
  font-weight: 700;
}

.recent-guesses {
  color: var(--ink-dim);
  text-align: right;
  font-size: 0.75rem;
}

/* ---------- 通用面板 ---------- */
.panel {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.9rem;
  padding: clamp(1.6rem, 4vw, 2.6rem);
  border: 1px solid var(--line);
  border-radius: var(--radius-xl);
  background: radial-gradient(circle at 50% 0%, rgba(239, 111, 169, 0.12), transparent 58%), var(--panel);
  text-align: center;
}

.panel h1 {
  margin: 0;
  font-family: var(--font-serif);
  font-size: 1.6rem;
  font-weight: 600;
}

.panel-sub {
  max-width: 32rem;
  margin: 0;
  color: var(--ink-muted);
  font-size: 0.86rem;
  line-height: 1.7;
}

.match-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  margin: 0;
  padding: 0.3rem 0.75rem;
  border-radius: 999px;
  background: rgba(139, 230, 189, 0.12);
  color: var(--success);
  font-size: 0.78rem;
}

.secret-row {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  flex-wrap: wrap;
  justify-content: center;
}

.difficulty-row {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.5rem;
  width: min(26rem, 100%);
}

.difficulty-option {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.2rem;
  padding: 0.6rem 0.5rem;
  border: 1px solid var(--line);
  border-radius: var(--radius-md);
  background: rgba(255, 255, 255, 0.03);
  color: var(--ink-soft);
  cursor: pointer;
  transition: border-color var(--dur-fast) ease, background var(--dur-fast) ease, color var(--dur-fast) ease;
}

.difficulty-option:hover {
  border-color: var(--line-strong);
  color: var(--ink);
}

.difficulty-option.active {
  border-color: var(--rose);
  background: rgba(239, 111, 169, 0.14);
  color: var(--ink);
  box-shadow: 0 0 0 1px rgba(239, 111, 169, 0.25) inset;
}

.difficulty-name {
  font-size: 0.88rem;
  font-weight: 700;
}

.difficulty-desc {
  color: var(--ink-dim);
  font-size: 0.7rem;
  line-height: 1.4;
  text-align: center;
}

.difficulty-option.active .difficulty-desc {
  color: var(--ink-muted);
}

.secret-input,
.guess-input {
  width: 9.5rem;
  padding: 0.85rem 1rem;
  border: 1px solid var(--line-strong);
  border-radius: var(--radius-md);
  background: rgba(8, 6, 12, 0.85);
  color: var(--ink);
  font-family: var(--font-serif);
  font-size: 1.6rem;
  font-weight: 600;
  letter-spacing: 0.35em;
  text-align: center;
  outline: none;
  transition: border-color var(--dur-fast) ease, box-shadow var(--dur-fast) ease;
}

.secret-input:focus,
.guess-input:focus {
  border-color: var(--rose);
  box-shadow: 0 0 0 3px rgba(239, 111, 169, 0.16);
}

.secret-input::placeholder,
.guess-input::placeholder {
  color: var(--ink-dim);
  letter-spacing: 0.2em;
}

.primary-btn,
.ghost-btn,
.link-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  border-radius: var(--radius-md);
  font-size: 0.88rem;
  font-weight: 600;
  cursor: pointer;
  transition: transform var(--dur-fast) ease, opacity var(--dur-fast) ease, border-color var(--dur-fast) ease;
}

.primary-btn {
  min-width: 9rem;
  padding: 0.75rem 1.3rem;
  border: none;
  background: linear-gradient(135deg, #ff8cc0, #c465ff);
  color: #1a0b18;
  box-shadow: 0 12px 30px rgba(196, 101, 255, 0.28);
}

.primary-btn:hover:not(:disabled) {
  transform: translateY(-1px);
}

.primary-btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.ghost-btn {
  padding: 0.65rem 1rem;
  border: 1px solid var(--line);
  background: rgba(255, 255, 255, 0.04);
  color: var(--ink-soft);
}

.ghost-btn:hover:not(:disabled) {
  border-color: var(--line-strong);
  color: var(--ink);
}

.link-btn {
  padding: 0.4rem 0.6rem;
  border: none;
  background: none;
  color: var(--ink-muted);
  font-size: 0.8rem;
}

.link-btn:hover {
  color: var(--ink-soft);
}

.link-btn.danger {
  color: rgba(255, 127, 154, 0.8);
}

.link-btn.danger:hover {
  color: var(--danger);
}

/* ---------- 等待匹配 ---------- */
.radar {
  position: relative;
  display: grid;
  place-items: center;
  width: 84px;
  height: 84px;
  border-radius: 50%;
  color: var(--rose-bright);
  background: rgba(239, 111, 169, 0.1);
}

.pulse {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  border: 1px solid rgba(239, 111, 169, 0.5);
  animation: pulse 1.8s ease-out infinite;
}

@keyframes pulse {
  0% {
    transform: scale(0.9);
    opacity: 0.9;
  }
  100% {
    transform: scale(1.6);
    opacity: 0;
  }
}

.waiting-hint {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.6rem 1rem;
  border-radius: var(--radius-md);
  background: rgba(239, 111, 169, 0.08);
  color: var(--ink-soft);
  font-size: 0.85rem;
}

.waiting-hint strong {
  color: var(--rose-bright);
  letter-spacing: 0.18em;
}

/* ---------- 对局 ---------- */
.game-head {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  gap: 0.75rem;
}

.player-card {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  padding: 0.85rem 1rem;
  border: 1px solid var(--line);
  border-radius: var(--radius-md);
  background: var(--panel-soft);
  transition: border-color var(--dur-base) ease, box-shadow var(--dur-base) ease;
}

.player-card.opponent {
  align-items: flex-end;
  text-align: right;
}

.player-card.active {
  border-color: var(--line-strong);
  box-shadow: var(--shadow-glow);
}

.player-role {
  color: var(--ink-muted);
  font-size: 0.7rem;
  letter-spacing: 0.16em;
}

.player-name {
  color: var(--ink);
  font-size: 0.95rem;
  font-weight: 600;
}

.player-count {
  color: var(--ink-dim);
  font-size: 0.72rem;
}

.versus {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.2rem;
  color: var(--gold);
  font-size: 0.72rem;
  font-variant-numeric: tabular-nums;
}

.turn-banner {
  margin: 0;
  padding: 0.6rem 1rem;
  border-radius: var(--radius-md);
  background: rgba(255, 255, 255, 0.03);
  color: var(--ink-muted);
  font-size: 0.85rem;
  text-align: center;
}

.turn-banner.mine {
  background: rgba(239, 111, 169, 0.12);
  color: var(--rose-bright);
  font-weight: 600;
}

.secret-reminder {
  color: var(--ink-dim);
  font-size: 0.78rem;
  text-align: center;
}

.secret-reminder strong {
  margin-left: 0.25rem;
  color: var(--ink-soft);
  letter-spacing: 0.22em;
  font-weight: 600;
}

.guess-form {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.7rem;
}

.boards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 1rem;
}

.board {
  padding: 1rem 1.1rem;
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  background: var(--panel-soft);
  min-height: 9rem;
}

.board h2 {
  margin: 0 0 0.7rem;
  color: var(--ink-soft);
  font-size: 0.85rem;
  font-weight: 600;
}

.board ul {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  margin: 0;
  padding: 0;
  list-style: none;
  max-height: 15rem;
  overflow-y: auto;
}

.board li {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  padding: 0.45rem 0.65rem;
  border-radius: var(--radius-sm);
  background: rgba(255, 255, 255, 0.035);
}

.digits {
  color: var(--ink);
  font-family: var(--font-serif);
  font-size: 1.05rem;
  letter-spacing: 0.28em;
}

.hits {
  padding: 0.15rem 0.5rem;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.06);
  color: var(--ink-muted);
  font-size: 0.74rem;
  font-variant-numeric: tabular-nums;
}

.hits.perfect {
  background: rgba(139, 230, 189, 0.16);
  color: var(--success);
  font-weight: 700;
}

.empty {
  margin: 0;
  color: var(--ink-dim);
  font-size: 0.8rem;
}

/* ---------- 结算 ---------- */
.result-panel.win {
  background: radial-gradient(circle at 50% 0%, rgba(245, 200, 143, 0.16), transparent 60%), var(--panel);
}

.result-panel.lose {
  background: radial-gradient(circle at 50% 0%, rgba(255, 127, 154, 0.12), transparent 60%), var(--panel);
}

.result-icon {
  display: grid;
  place-items: center;
  width: 74px;
  height: 74px;
  border-radius: 50%;
  background: rgba(245, 200, 143, 0.12);
  color: var(--gold);
}

.result-panel.lose .result-icon {
  background: rgba(255, 127, 154, 0.12);
  color: var(--danger);
}

.result-secret {
  color: var(--ink-muted);
  font-size: 0.82rem;
}

.result-secret strong {
  color: var(--ink);
  letter-spacing: 0.25em;
  font-family: var(--font-serif);
}

.result-actions {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  flex-wrap: wrap;
  justify-content: center;
}

/* ---------- 猜测结果动画 ---------- */
.feedback-overlay {
  position: fixed;
  inset: 0;
  z-index: 70;
  display: grid;
  place-items: center;
  pointer-events: none;
}

.feedback-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.3rem;
  min-width: 11rem;
  padding: 1.35rem 2.2rem 1.15rem;
  border: 1px solid var(--line-strong);
  border-radius: 22px;
  background: radial-gradient(circle at 50% 0%, rgba(239, 111, 169, 0.22), transparent 62%), rgba(16, 10, 22, 0.94);
  box-shadow: 0 26px 70px rgba(0, 0, 0, 0.6), var(--shadow-glow);
  backdrop-filter: blur(6px);
  animation: feedback-pop 420ms cubic-bezier(0.2, 1.35, 0.4, 1) both;
}

.feedback-num {
  font-family: var(--font-serif);
  font-size: 3.4rem;
  font-weight: 600;
  line-height: 1;
  color: var(--rose-bright);
  text-shadow: 0 0 26px rgba(255, 154, 200, 0.5);
}

.feedback-label {
  color: var(--ink);
  font-size: 0.98rem;
  font-weight: 600;
  letter-spacing: 0.04em;
}

.feedback-guess {
  color: var(--ink-dim);
  font-family: var(--font-serif);
  font-size: 0.8rem;
  letter-spacing: 0.34em;
}

.feedback-card.zero {
  border-color: rgba(255, 255, 255, 0.14);
  background: radial-gradient(circle at 50% 0%, rgba(255, 255, 255, 0.06), transparent 62%), rgba(16, 10, 22, 0.94);
  box-shadow: 0 26px 70px rgba(0, 0, 0, 0.6);
  animation: feedback-pop 300ms ease both, feedback-shake 460ms 160ms ease both;
}

.feedback-card.zero .feedback-num {
  color: var(--ink-muted);
  text-shadow: none;
}

.feedback-card.perfect {
  border-color: rgba(245, 200, 143, 0.55);
  background: radial-gradient(circle at 50% 0%, rgba(245, 200, 143, 0.24), transparent 62%), rgba(20, 14, 10, 0.94);
  box-shadow: 0 26px 70px rgba(0, 0, 0, 0.6), var(--shadow-gold);
}

.feedback-card.perfect .feedback-num {
  color: var(--gold);
  text-shadow: 0 0 30px rgba(245, 200, 143, 0.6);
}

.feedback-card.perfect .feedback-guess {
  color: var(--gold);
}

@keyframes feedback-pop {
  0% {
    opacity: 0;
    transform: scale(0.55) rotate(-7deg);
  }
  60% {
    opacity: 1;
    transform: scale(1.06) rotate(1.5deg);
  }
  100% {
    opacity: 1;
    transform: scale(1) rotate(0deg);
  }
}

@keyframes feedback-shake {
  0%,
  100% {
    transform: translateX(0);
  }
  20% {
    transform: translateX(-9px);
  }
  40% {
    transform: translateX(8px);
  }
  60% {
    transform: translateX(-5px);
  }
  80% {
    transform: translateX(3px);
  }
}

.feedback-leave-active {
  transition: opacity 220ms ease, transform 220ms ease;
}

.feedback-leave-to {
  opacity: 0;
  transform: translateY(-8px) scale(0.96);
}

@media (prefers-reduced-motion: reduce) {
  .feedback-card,
  .feedback-card.zero {
    animation: none;
  }
}

/* ---------- 对手猜测提示 ---------- */
.opp-feedback {
  position: fixed;
  top: 84px;
  left: 50%;
  z-index: 65;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  max-width: min(28rem, calc(100vw - 2rem));
  padding: 0.55rem 1rem 0.6rem;
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: 14px;
  background: rgba(16, 10, 22, 0.92);
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.45);
  backdrop-filter: blur(6px);
  pointer-events: none;
  animation: opp-in 260ms ease both;
}

.opp-line {
  display: flex;
  align-items: center;
  gap: 0.55rem;
}

.opp-hint {
  margin: 0;
  color: var(--ink-muted);
  font-size: 0.78rem;
  line-height: 1.5;
}

.opp-who {
  color: var(--ink-muted);
  font-size: 0.8rem;
}

.opp-hits {
  color: var(--ink);
  font-size: 0.88rem;
  font-weight: 700;
  white-space: nowrap;
}

.opp-hits.zero {
  color: var(--ink-muted);
}

.opp-hits.perfect {
  color: var(--gold);
}

@keyframes opp-in {
  from {
    opacity: 0;
    transform: translate(-50%, -8px);
  }
  to {
    opacity: 1;
    transform: translate(-50%, 0);
  }
}

.opp-leave-active {
  transition: opacity 200ms ease;
}

.opp-leave-to {
  opacity: 0;
}

@media (prefers-reduced-motion: reduce) {
  .opp-feedback {
    animation: none;
    transform: translate(-50%, 0);
  }
}

@media (max-width: 640px) {
  .game-head {
    grid-template-columns: 1fr;
    gap: 0.5rem;
  }

  .player-card.opponent {
    align-items: flex-start;
    text-align: left;
  }

  .versus {
    flex-direction: row;
    justify-content: center;
    gap: 0.5rem;
  }
}
</style>
