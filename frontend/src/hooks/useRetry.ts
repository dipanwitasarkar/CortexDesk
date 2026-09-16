import { useState, useCallback } from 'react'

interface RetryOptions {
  maxAttempts?: number
  delay?: number
  backoff?: boolean
  onRetry?: (attempt: number) => void
  onSuccess?: () => void
  onFailure?: (error: Error) => void
}

export const useRetry = () => {
  const [isRetrying, setIsRetrying] = useState(false)
  const [attempt, setAttempt] = useState(0)
  const [lastError, setLastError] = useState<Error | null>(null)

  const retry = useCallback(async <T>(
    fn: () => Promise<T>,
    options: RetryOptions = {}
  ): Promise<T | null> => {
    const {
      maxAttempts = 3,
      delay = 1000,
      backoff = true,
      onRetry,
      onSuccess,
      onFailure
    } = options

    setIsRetrying(true)
    setAttempt(0)
    setLastError(null)

    for (let i = 0; i < maxAttempts; i++) {
      try {
        setAttempt(i + 1)
        const result = await fn()
        setIsRetrying(false)
        onSuccess?.()
        return result
      } catch (error) {
        setLastError(error as Error)
        
        if (i < maxAttempts - 1) {
          onRetry?.(i + 1)
          const currentDelay = backoff ? delay * Math.pow(2, i) : delay
          await new Promise(resolve => setTimeout(resolve, currentDelay))
        }
      }
    }

    setIsRetrying(false)
    onFailure?.(lastError!)
    return null
  }, [])

  const reset = useCallback(() => {
    setIsRetrying(false)
    setAttempt(0)
    setLastError(null)
  }, [])

  return {
    retry,
    isRetrying,
    attempt,
    lastError,
    reset
  }
}
