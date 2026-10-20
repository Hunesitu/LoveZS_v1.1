/**
 * 数字炸弹小游戏 API
 */

import { api } from './client'

export interface GameGuessItem {
  side: number
  guess: string
  hits: number
  is_mine: boolean
  created_at: string
}

export interface GameResult {
  winner_side: number
  i_won: boolean
  winner_name: string
}

export interface GameOpponent {
  computer: boolean
  id?: number
  username: string
}

export interface GameRoomData {
  id: number
  mode: 'pve' | 'pvp'
  status: 'waiting' | 'setup' | 'playing' | 'finished' | 'cancelled'
  my_side: number
  turn_side: number
  my_turn: boolean
  me: { id: number; username: string }
  opponent: GameOpponent | null
  my_secret: string
  opponent_secret: string
  my_secret_set: boolean
  opponent_secret_set: boolean
  guesses: GameGuessItem[]
  my_guess_count: number
  opponent_guess_count: number
  result: GameResult | null
  created_at: string
  started_at: string | null
  finished_at: string | null
  duration_seconds: number
}

export interface GameRecordItem {
  id: number
  mode: 'pve' | 'pvp'
  i_won: boolean
  opponent: string
  my_guesses: number
  finished_at: string | null
}

export interface GameStats {
  pve: { wins: number; losses: number; total: number; best_guesses: number | null }
  pvp: { wins: number; losses: number; total: number; best_guesses: number | null }
  recent: GameRecordItem[]
}

export const getCurrentRoom = async (): Promise<{ room: GameRoomData | null }> => {
  const response = await api.get<{ room: GameRoomData | null }>('/games/room/')
  return response.data
}

export const getRoom = async (roomId: number): Promise<{ room: GameRoomData }> => {
  const response = await api.get<{ room: GameRoomData }>(`/games/room/${roomId}/`)
  return response.data
}

export const startPve = async (secret: string): Promise<{ room: GameRoomData }> => {
  const response = await api.post<{ room: GameRoomData }>('/games/pve/', { secret })
  return response.data
}

export const matchPvp = async (): Promise<{ room: GameRoomData; matched: boolean }> => {
  const response = await api.post<{ room: GameRoomData; matched: boolean }>('/games/match/', {})
  return response.data
}

export const submitSecret = async (roomId: number, secret: string): Promise<{ room: GameRoomData }> => {
  const response = await api.post<{ room: GameRoomData }>(`/games/room/${roomId}/secret/`, { secret })
  return response.data
}

export const submitGuess = async (
  roomId: number,
  guess: string,
): Promise<{ room: GameRoomData; results: Array<{ side: number; guess: string; hits: number }> }> => {
  const response = await api.post<{
    room: GameRoomData
    results: Array<{ side: number; guess: string; hits: number }>
  }>(`/games/room/${roomId}/guess/`, { guess })
  return response.data
}

export const cancelRoom = async (roomId: number): Promise<{ room: GameRoomData }> => {
  const response = await api.post<{ room: GameRoomData }>(`/games/room/${roomId}/cancel/`, {})
  return response.data
}

export const getGameStats = async (): Promise<GameStats> => {
  const response = await api.get<GameStats>('/games/stats/')
  return response.data
}
