const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

const getBackendBaseUrl = () => API_BASE_URL.replace(/\/api\/?$/, '')

const isAbsoluteUrl = (value: string) => /^https?:\/\//i.test(value)

const normalizeMediaPath = (value: string) => {
  const normalizedSlashes = value.replace(/\\/g, '/').trim()
  if (!normalizedSlashes) {
    return ''
  }

  if (isAbsoluteUrl(normalizedSlashes)) {
    return normalizedSlashes
  }

  const withLeadingSlash = normalizedSlashes.startsWith('/')
    ? normalizedSlashes
    : `/${normalizedSlashes}`

  if (withLeadingSlash === '/uploads' || withLeadingSlash.startsWith('/uploads/')) {
    return withLeadingSlash.replace(/^\/uploads(?=\/|$)/, '/media')
  }

  return withLeadingSlash
}

export const isVideo = (media: { mimetype?: string }) =>
  media.mimetype?.startsWith('video/') ?? false

export const resolveMediaUrl = (url?: string) => {
  if (!url) {
    return ''
  }

  const normalizedUrl = normalizeMediaPath(url)
  if (!normalizedUrl) {
    return ''
  }

  if (isAbsoluteUrl(normalizedUrl)) {
    return normalizedUrl
  }

  if (normalizedUrl === '/media' || normalizedUrl.startsWith('/media/')) {
    return `${getBackendBaseUrl()}${normalizedUrl}`
  }

  return normalizedUrl
}

type MediaVariant = 'thumbnail' | 'display' | 'original'

interface MediaLike {
  url?: string
  thumbnail_url?: string
  compressed_url?: string
  mimetype?: string
}

export const getMediaUrl = (media?: MediaLike | null, variant: MediaVariant = 'display') => {
  if (!media) {
    return ''
  }

  if (isVideo(media)) {
    return resolveMediaUrl(media.url || '')
  }

  if (variant === 'thumbnail') {
    return resolveMediaUrl(media.thumbnail_url || media.compressed_url || media.url || '')
  }

  if (variant === 'original') {
    return resolveMediaUrl(media.url || media.compressed_url || media.thumbnail_url || '')
  }

  return resolveMediaUrl(media.compressed_url || media.thumbnail_url || media.url || '')
}
