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
