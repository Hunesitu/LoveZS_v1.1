<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { ArrowRight, CalendarHeart, Film, Heart, Images, Plus, Sparkles } from 'lucide-vue-next'
import dayjs from 'dayjs'
import 'dayjs/locale/zh-cn'
import { useDiaries } from '@/composables/useDiaries'
import { useCountdowns } from '@/composables/useCountdowns'
import { getMediaUrl, isVideo } from '@/utils/media'
import { findNextMilestone, inclusiveDaysSince, type MilestoneCandidate } from '@/utils/milestones'
import type { Diary, Photo } from '@/types'

dayjs.locale('zh-cn')

const { diaries, isLoading, loadDiaries, totalCount } = useDiaries()
const { countdowns, loadCountdowns } = useCountdowns()

const LOVE_ANNIVERSARY = '2023-09-09'
const loveDays = ref(0)
const nextMilestone = ref<MilestoneCandidate | null>(null)

interface StoryFrame {
  id: string
  diary?: Diary
  media?: Photo | null
  title: string
  caption: string
  date?: string
}

const fallbackLines = [
  '把平凡的一天剪成只属于我们的电影。',
  '每一次回头，都有一束光落在你身上。',
  '今晚的星光，替我们保存所有心动。',
  '慢慢写，慢慢爱，镜头会记得。',
  '有你的日常，也值得被放在银幕中央。',
  '下一幕，仍然是我们。',
]

const getFallbackLine = (index: number) => fallbackLines[index % fallbackLines.length] || '下一幕，仍然是我们。'

const defaultFrame: StoryFrame = {
  id: 'fallback-default',
  title: '今晚的回忆放映中',
  caption: getFallbackLine(0),
}

const calculateLoveDays = () => {
  return inclusiveDaysSince(LOVE_ANNIVERSARY)
}

const getDiaryCover = (diary: Diary) => diary.cover_media || diary.attached_photos?.[0] || null

const diaryFrames = computed<StoryFrame[]>(() =>
  diaries.value.map((diary, index) => ({
    id: `diary-${diary.id}`,
    diary,
    media: getDiaryCover(diary),
    title: diary.title || `第 ${index + 1} 幕`,
    caption: diary.content?.replace(/[#*`_[\]]/g, '').slice(0, 42) || getFallbackLine(index),
    date: diary.date || diary.created_at,
  }))
)

const storyFrames = computed<StoryFrame[]>(() => {
  const frames = [...diaryFrames.value]
  let index = 0
  while (frames.length < 6) {
    frames.push({
      id: `fallback-${index}`,
      title: `浪漫片段 ${index + 1}`,
      caption: getFallbackLine(index),
    })
    index += 1
  }
  return frames.slice(0, 6)
})

const heroFrame = computed<StoryFrame>(() => storyFrames.value[0] || defaultFrame)
const snippetFrames = computed(() => storyFrames.value.slice(1, 5))
const recentDiaries = computed(() => diaries.value.slice(0, 3))

const posterStyle = (index: number) => ({
  '--poster-hue': `${320 + index * 18}deg`,
  '--poster-delay': `${index * 70}ms`,
})

onMounted(async () => {
  await Promise.all([
    loadDiaries({ limit: 8 }),
    loadCountdowns(),
  ])
  const days = calculateLoveDays()
  loveDays.value = days
  nextMilestone.value = findNextMilestone(countdowns.value, {
    title: '恋爱纪念日',
    date: LOVE_ANNIVERSARY,
  })
})
</script>

<template>
  <div class="dashboard-page">
    <section class="cinema-hero reveal-in" aria-labelledby="welcome-title">
      <div class="hero-copy">
        <p class="romance-kicker">LoveZS Private Cinema</p>
        <h1 class="hero-title" id="welcome-title">
          把我们的故事，放在今晚最亮的银幕中央
        </h1>
        <p class="hero-subtitle">
          今天是 {{ dayjs().format('YYYY年M月D日') }}。每一张照片、每一篇日记，都在为下一幕温柔预告。
        </p>

        <div class="hero-metrics" aria-label="恋爱数据概览">
          <div class="metric-card love-days">
            <Heart :size="15" fill="currentColor" />
            <span class="metric-label">恋爱</span>
            <strong>{{ loveDays }}</strong>
            <span>天</span>
          </div>
          <div class="metric-card milestone">
            <CalendarHeart :size="15" />
            <span class="metric-label">下一座里程碑</span>
            <strong>{{ nextMilestone?.remaining ?? 0 }}</strong>
            <span>天后 · {{ nextMilestone ? dayjs(nextMilestone.targetDate).format('M月D日') : '待定' }}</span>
          </div>
          <div class="metric-card diary-total">
            <span class="metric-dot"></span>
            <span>日记 {{ totalCount }} 篇</span>
          </div>
        </div>

        <div class="hero-actions">
          <RouterLink to="/diaries/new" class="btn-primary">
            <Plus :size="16" />
            写下新一幕
          </RouterLink>
          <RouterLink to="/diaries" class="btn-secondary">
            <Images :size="16" />
            浏览胶片
          </RouterLink>
        </div>
      </div>

      <div class="poster-stage" aria-label="最近回忆影像">
        <RouterLink
          :to="heroFrame.diary ? `/diaries/${heroFrame.diary.id}` : '/diaries/new'"
          class="main-poster cinematic-frame"
          :style="posterStyle(0)"
        >
          <template v-if="heroFrame.media">
            <video
              v-if="isVideo(heroFrame.media)"
              :src="getMediaUrl(heroFrame.media, 'display')"
              class="poster-media"
              muted
              loop
              playsinline
              preload="metadata"
            />
            <img
              v-else
              :src="getMediaUrl(heroFrame.media, 'display')"
              :alt="heroFrame.media.original_name || heroFrame.title"
              class="poster-media"
              width="1600"
              height="980"
              fetchpriority="high"
              decoding="async"
            />
          </template>
          <div v-else class="poster-fallback">
            <Film :size="44" />
          </div>
          <div class="poster-badge">
            <span>{{ nextMilestone?.title || `${loveDays} 天` }}</span>
          </div>
          <div class="poster-overlay">
            <span class="poster-label">Tonight's Feature</span>
            <h2>{{ heroFrame.title }}</h2>
            <p>{{ heroFrame.caption }}</p>
          </div>
        </RouterLink>
      </div>
    </section>

    <section class="snippet-section" aria-labelledby="snippet-title">
      <div class="section-head compact">
        <div>
          <p class="romance-kicker">Romantic Cuts</p>
          <h2 class="section-title" id="snippet-title">浪漫片段</h2>
        </div>
        <p class="section-note">那些没说出口的喜欢，都藏在一帧一帧的光里。</p>
      </div>

      <div class="snippet-grid">
        <RouterLink
          v-for="(frame, index) in snippetFrames"
          :key="frame.id"
          :to="frame.diary ? `/diaries/${frame.diary.id}` : '/diaries/new'"
          class="snippet-card cinematic-card"
          :style="posterStyle(index + 1)"
        >
          <template v-if="frame.media">
            <video
              v-if="isVideo(frame.media)"
              :src="getMediaUrl(frame.media, 'thumbnail')"
              class="poster-media"
              muted
              preload="metadata"
            />
            <img
              v-else
              :src="getMediaUrl(frame.media, 'thumbnail')"
              :alt="frame.media.original_name || frame.title"
              class="poster-media"
              loading="lazy"
              decoding="async"
            />
          </template>
          <div v-else class="poster-fallback small">
            <Sparkles :size="24" />
          </div>
          <div class="mini-caption">
            <strong>{{ frame.title }}</strong>
            <span>{{ frame.date ? dayjs(frame.date).format('M月D日') : '待记录' }}</span>
          </div>
        </RouterLink>
      </div>
    </section>

    <section class="recent-section">
      <div class="section-head">
        <div>
          <p class="romance-kicker">Recent Scenes</p>
          <h2 class="section-title">最近日记</h2>
        </div>
        <RouterLink to="/diaries" class="view-all">
          查看全部 <ArrowRight :size="14" />
        </RouterLink>
      </div>

      <div v-if="isLoading" class="loading-container glass-card">
        <div class="spinner"></div>
      </div>

      <div v-else-if="recentDiaries.length > 0" class="diary-grid">
        <RouterLink
          v-for="(diary, index) in recentDiaries"
          :key="diary.id"
          :to="`/diaries/${diary.id}`"
          class="diary-card cinematic-card"
          :style="posterStyle(index + 3)"
        >
          <div class="card-cover">
            <template v-if="getDiaryCover(diary)">
              <video
                v-if="isVideo(getDiaryCover(diary)!)"
                :src="getMediaUrl(getDiaryCover(diary), 'thumbnail')"
                class="cover-image"
                muted
                preload="metadata"
              />
              <img
                v-else
                :src="getMediaUrl(getDiaryCover(diary), 'thumbnail')"
                :alt="getDiaryCover(diary)!.original_name || diary.title"
                class="cover-image"
                loading="lazy"
                decoding="async"
              />
            </template>
            <div v-else class="cover-fallback">
              <Sparkles :size="30" />
            </div>
          </div>
          <div class="card-body">
            <h3 class="diary-title">
              <Heart :size="15" fill="currentColor" />
              {{ diary.title }}
            </h3>
            <p class="diary-line">
              {{ diary.content?.replace(/[#*`_[\]]/g, '').slice(0, 56) || '这一天，也值得被温柔收藏。' }}
            </p>
            <div class="diary-meta">
              <span class="tag">{{ diary.category || '生活' }}</span>
              <span>{{ dayjs(diary.date || diary.created_at).format('M月D日') }}</span>
            </div>
          </div>
        </RouterLink>
      </div>

      <div v-else class="empty-state glass-card">
        <Sparkles :size="38" />
        <h3>还没有日记</h3>
        <p>先写下第一幕，今晚的银幕就会亮起来。</p>
        <RouterLink to="/diaries/new" class="btn-primary">
          <Plus :size="16" />
          写第一篇日记
        </RouterLink>
      </div>
    </section>
  </div>
</template>

<style scoped>
.dashboard-page {
  width: 100%;
}

.cinema-hero {
  position: relative;
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  align-content: start;
  gap: clamp(1.35rem, 2.8vw, 2.6rem);
  min-height: auto;
  margin: calc(-1 * clamp(1rem, 2.5vw, 2rem)) calc(-1 * var(--page-px)) 1.5rem;
  padding: clamp(1.8rem, 4.2vw, 3.6rem) var(--page-px) clamp(1.8rem, 4vw, 3.2rem);
  overflow: hidden;
  isolation: isolate;
}

.cinema-hero::before {
  content: '';
  position: absolute;
  inset: 0;
  z-index: -2;
  background:
    linear-gradient(90deg, rgba(5, 5, 11, 0.92), rgba(5, 5, 11, 0.34) 52%, rgba(5, 5, 11, 0.78)),
    radial-gradient(circle at 72% 18%, rgba(255, 154, 200, 0.24), transparent 26%),
    radial-gradient(circle at 45% 74%, rgba(245, 200, 143, 0.12), transparent 32%),
    linear-gradient(135deg, #07060d, #281329 56%, #080712);
}

.cinema-hero::after {
  content: '';
  position: absolute;
  inset: -5%;
  z-index: -1;
  pointer-events: none;
  background:
    radial-gradient(1px 1px at 18% 16%, rgba(255,255,255,.76), transparent 2px),
    radial-gradient(1px 1px at 48% 10%, rgba(245,200,143,.62), transparent 2px),
    radial-gradient(1.5px 1.5px at 88% 22%, rgba(255,154,200,.7), transparent 3px),
    linear-gradient(112deg, transparent 0 50%, rgba(255, 154, 200, 0.18) 61%, transparent 72%);
  opacity: 0.75;
  animation: filmDrift 8s ease-in-out infinite alternate;
}

.hero-copy {
  display: grid;
  justify-items: start;
  width: min(100%, 1280px);
  max-width: none;
  margin: 0 auto;
}

.hero-title {
  margin: 0;
  color: var(--ink);
  font-family: var(--font-serif);
  font-size: clamp(2.45rem, 4.3vw, 4.9rem);
  font-weight: 700;
  line-height: 1.08;
  text-wrap: balance;
  text-shadow: 0 18px 60px rgba(255, 154, 200, 0.22);
}

.hero-subtitle {
  margin: 1.2rem 0 0;
  color: var(--ink-soft);
  font-size: clamp(0.98rem, 1.3vw, 1.08rem);
  line-height: 1.85;
  max-width: 760px;
}

.hero-metrics {
  display: flex;
  flex-wrap: wrap;
  gap: 0.55rem;
  margin-top: 1.25rem;
}

.metric-card {
  display: inline-flex;
  align-items: center;
  gap: 0.38rem;
  min-height: 34px;
  padding: 0.38rem 0.68rem;
  border: 1px solid rgba(245, 200, 143, 0.14);
  border-radius: 999px;
  color: var(--ink-soft);
  background: rgba(255, 255, 255, 0.07);
  box-shadow: 0 12px 26px rgba(0, 0, 0, 0.18);
  backdrop-filter: blur(14px);
}

.metric-card svg {
  color: var(--gold);
  flex: 0 0 auto;
}

.metric-card strong {
  color: #fff;
  font-family: Georgia, var(--font-serif);
  font-size: 1.12rem;
  line-height: 1;
}

.metric-label {
  color: var(--ink-muted);
  font-size: 0.76rem;
  font-weight: 800;
}

.love-days {
  border-color: rgba(255, 154, 200, 0.28);
  color: #fff1f8;
}

.diary-total {
  padding-inline: 0.58rem;
  color: var(--ink-muted);
  font-size: 0.78rem;
  font-weight: 800;
}

.metric-dot {
  width: 6px;
  height: 6px;
  border-radius: 999px;
  background: var(--rose-bright);
  box-shadow: 0 0 14px rgba(255, 154, 200, 0.8);
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-top: 1.45rem;
}

.poster-stage {
  display: grid;
  justify-self: center;
  width: min(100%, 1040px);
  min-width: 0;
  perspective: 1200px;
}

.main-poster,
.snippet-card {
  animation: revealIn 620ms ease both;
  animation-delay: var(--poster-delay);
}

.main-poster {
  min-height: clamp(460px, 42vw, 680px);
  aspect-ratio: 16 / 9.8;
  transform: none;
  transition: transform var(--dur-slow) ease, box-shadow var(--dur-slow) ease;
}

.main-poster:hover {
  transform: translateY(-4px) scale(1.006);
  box-shadow: var(--shadow-lg), var(--shadow-glow);
}

.poster-media,
.poster-fallback {
  width: 100%;
  height: 100%;
}

.poster-media {
  position: absolute;
  inset: 0;
  object-fit: cover;
  filter: saturate(0.95) contrast(1.05);
  transition: transform 700ms ease, filter 700ms ease;
}

.main-poster:hover .poster-media,
.snippet-card:hover .poster-media {
  transform: scale(1.045);
  filter: saturate(1.08) contrast(1.08);
}

.poster-fallback {
  position: absolute;
  inset: 0;
  display: grid;
  place-items: center;
  color: rgba(245, 200, 143, 0.85);
  background:
    radial-gradient(circle at 42% 24%, hsl(var(--poster-hue) 78% 62% / 0.34), transparent 30%),
    radial-gradient(circle at 78% 72%, rgba(245, 200, 143, 0.2), transparent 30%),
    linear-gradient(145deg, #221329, #07070d 72%);
}

.poster-fallback.small {
  color: rgba(255, 154, 200, 0.86);
}

.poster-badge {
  position: absolute;
  top: 18px;
  right: 18px;
  z-index: 3;
  display: inline-flex;
  align-items: center;
  min-height: 30px;
  padding: 0 0.78rem;
  border: 1px solid rgba(245, 200, 143, 0.24);
  border-radius: 999px;
  color: #fff;
  background: rgba(7, 7, 13, 0.48);
  font-size: 0.78rem;
  font-weight: 900;
  backdrop-filter: blur(14px);
}

.poster-overlay {
  position: absolute;
  right: 0;
  bottom: 0;
  left: 0;
  z-index: 2;
  padding: clamp(1.25rem, 3vw, 2.4rem);
  background: linear-gradient(180deg, transparent, rgba(0, 0, 0, 0.72) 38%, rgba(0, 0, 0, 0.92));
}

.poster-label {
  color: var(--gold);
  font-size: 0.72rem;
  font-weight: 900;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.poster-overlay h2 {
  margin: 0.45rem 0 0.45rem;
  color: #fff;
  font-family: var(--font-serif);
  font-size: clamp(1.55rem, 3vw, 2.55rem);
}

.poster-overlay p {
  max-width: 540px;
  margin: 0;
  color: var(--ink-soft);
  line-height: 1.65;
}

.snippet-section,
.recent-section {
  padding-bottom: 1.5rem;
}

.snippet-section {
  margin-top: 0.35rem;
}

.section-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1rem;
}

.section-head.compact {
  align-items: center;
}

.section-note {
  max-width: 420px;
  margin: 0;
  color: var(--ink-muted);
  font-size: 0.86rem;
  line-height: 1.7;
}

.snippet-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: clamp(0.75rem, 1.4vw, 1.1rem);
}

.snippet-card {
  min-height: clamp(138px, 13vw, 188px);
  transition: transform var(--dur-slow) ease, border-color var(--dur-slow) ease, box-shadow var(--dur-slow) ease;
}

.snippet-card:hover {
  transform: translateY(-5px) scale(1.01);
  border-color: var(--line-strong);
}

.mini-caption {
  position: absolute;
  inset: auto 0 0;
  z-index: 2;
  display: grid;
  gap: 0.15rem;
  padding: 0.8rem;
  background: linear-gradient(180deg, transparent, rgba(0, 0, 0, 0.78));
}

.mini-caption strong {
  overflow: hidden;
  color: #fff;
  font-size: 0.9rem;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.mini-caption span {
  color: var(--gold);
  font-size: 0.74rem;
  font-weight: 800;
}

.view-all {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  color: var(--gold);
  font-size: 0.875rem;
  font-weight: 800;
}

.diary-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: clamp(0.85rem, 1.5vw, 1.2rem);
}

.diary-card {
  min-height: 310px;
  animation: revealIn 540ms ease both;
  animation-delay: var(--poster-delay);
  transition: transform var(--dur-slow) ease, border-color var(--dur-slow) ease, box-shadow var(--dur-slow) ease;
}

.diary-card:hover {
  transform: translateY(-5px);
}

.card-cover {
  position: relative;
  width: 100%;
  aspect-ratio: 16 / 10;
  overflow: hidden;
}

.cover-image,
.cover-fallback {
  width: 100%;
  height: 100%;
}

.cover-image {
  object-fit: cover;
  transition: transform 700ms ease;
}

.diary-card:hover .cover-image {
  transform: scale(1.05);
}

.cover-fallback {
  display: grid;
  place-items: center;
  color: rgba(245, 200, 143, 0.8);
  background:
    radial-gradient(circle at 48% 32%, hsl(var(--poster-hue) 72% 60% / 0.28), transparent 44%),
    linear-gradient(135deg, rgba(46, 28, 55, 0.95), rgba(8, 8, 14, 0.98));
}

.card-body {
  padding: 1rem;
}

.diary-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0 0 0.55rem;
  color: #fff8fc;
  font-size: 1rem;
  font-weight: 800;
  line-height: 1.3;
}

.diary-title svg {
  color: var(--rose-bright);
}

.diary-line {
  min-height: 3.2em;
  margin: 0 0 0.85rem;
  color: var(--ink-soft);
  font-size: 0.86rem;
  line-height: 1.6;
}

.diary-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  color: var(--ink-muted);
  font-size: 0.78rem;
  font-weight: 800;
}

.empty-state {
  gap: 0.8rem;
  padding: 3rem 1rem;
}

.empty-state h3,
.empty-state p {
  margin: 0;
}

.empty-state svg {
  color: var(--gold);
}

@media (max-width: 1180px) {
  .hero-copy {
    width: min(100%, 860px);
  }

  .main-poster {
    min-height: 520px;
  }
}

@media (max-width: 1024px) {
  .snippet-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 900px) {
  .diary-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 767px) {
  .cinema-hero {
    margin: -1rem -1rem 1.25rem;
    padding: 1.25rem 1rem 1.5rem;
  }

  .hero-actions {
    flex-direction: column;
    width: 100%;
  }

  .hero-metrics {
    gap: 0.45rem;
  }

  .metric-card {
    max-width: 100%;
  }

  .main-poster {
    min-height: clamp(340px, 104vw, 500px);
    aspect-ratio: 4 / 5;
  }

  .poster-badge {
    top: 14px;
    right: 14px;
  }

  .snippet-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .snippet-card {
    min-height: 136px;
  }

  .section-head,
  .section-head.compact {
    align-items: stretch;
    flex-direction: column;
  }
}

@media (max-width: 430px) {
  .hero-title {
    font-size: clamp(2rem, 11vw, 2.5rem);
  }

  .snippet-grid {
    grid-template-columns: 1fr;
  }
}
</style>
