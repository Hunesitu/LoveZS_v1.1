import dayjs from 'dayjs'
import type { Countdown } from '@/types'

export interface MilestoneCandidate {
  kind: 'century' | 'event'
  title: string
  targetDate: string
  remaining: number
  currentDays?: number
  targetDays?: number
  progress: number
}

export const inclusiveDaysSince = (date: string) => {
  const start = dayjs(date).startOf('day')
  const today = dayjs().startOf('day')
  return Math.max(today.diff(start, 'day') + 1, 0)
}

export const getNextRecurringDate = (month?: number | null, day?: number | null) => {
  if (!month || !day) return null

  const today = dayjs().startOf('day')
  const buildDate = (year: number) => {
    const date = dayjs(`${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`)
    return date.isValid() ? date.startOf('day') : dayjs(`${year}-${String(month).padStart(2, '0')}-28`).startOf('day')
  }

  const thisYear = buildDate(today.year())
  return thisYear.isBefore(today, 'day') ? buildDate(today.year() + 1) : thisYear
}

export const createCenturyMilestone = (title: string, date: string): MilestoneCandidate | null => {
  const currentDays = inclusiveDaysSince(date)
  if (currentDays <= 0) return null

  const targetDays = (Math.floor(currentDays / 100) + 1) * 100
  const targetDate = dayjs(date).startOf('day').add(targetDays - 1, 'day')
  const remaining = Math.max(targetDate.diff(dayjs().startOf('day'), 'day'), 0)

  return {
    kind: 'century',
    title: `第 ${targetDays} 天`,
    targetDate: targetDate.format('YYYY-MM-DD'),
    remaining,
    currentDays,
    targetDays,
    progress: Math.min((currentDays / targetDays) * 100, 100),
  }
}

const createEventMilestone = (countdown: Countdown): MilestoneCandidate | null => {
  const today = dayjs().startOf('day')
  const target = countdown.is_recurring
    ? getNextRecurringDate(countdown.recurring_month, countdown.recurring_day)
    : dayjs(countdown.target_date).startOf('day')

  if (!target || !target.isValid() || target.isBefore(today, 'day')) return null

  return {
    kind: 'event',
    title: countdown.title,
    targetDate: target.format('YYYY-MM-DD'),
    remaining: target.diff(today, 'day'),
    progress: countdown.days > 0 ? 0 : 100,
  }
}

export const findNextMilestone = (
  countdowns: Countdown[],
  base?: { title: string; date: string }
) => {
  const candidates: MilestoneCandidate[] = []

  if (base) {
    const baseMilestone = createCenturyMilestone(base.title, base.date)
    if (baseMilestone) candidates.push(baseMilestone)
  }

  countdowns.forEach((countdown) => {
    const eventMilestone = createEventMilestone(countdown)
    if (eventMilestone) candidates.push(eventMilestone)

    if ((countdown.days || 0) < 0 || countdown.direction === 'countup') {
      const centuryMilestone = createCenturyMilestone(countdown.title, countdown.target_date)
      if (centuryMilestone) candidates.push(centuryMilestone)
    }
  })

  return candidates.sort((a, b) => {
    if (a.remaining !== b.remaining) return a.remaining - b.remaining
    if (a.kind !== b.kind) return a.kind === 'event' ? -1 : 1
    return a.targetDate.localeCompare(b.targetDate)
  })[0] || null
}
