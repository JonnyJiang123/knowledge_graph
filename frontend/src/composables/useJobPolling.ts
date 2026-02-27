import { ref, onMounted, onUnmounted } from 'vue'

export interface JobStatus {
  job_id: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  progress?: {
    percentage: number
    processed: number
    total: number
    estimatedRemaining?: number
  }
  stages?: Array<{
    name: string
    status: string
  }>
  error?: string
}

export function useJobPolling(jobId: string, options?: {
  interval?: number
  onComplete?: (result: JobStatus) => void
  onError?: (error: string) => void
}) {
  const { interval = 2000, onComplete, onError } = options || {}

  const status = ref<JobStatus | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  let timer: number | null = null
  let isActive = false

  const fetchStatus = async () => {
    if (!isActive) return

    try {
      loading.value = true
      // 调用API获取任务状态
      // const response = await fetch(`/api/jobs/${jobId}`)
      // const data = await response.json()

      // 模拟数据
      const data: JobStatus = {
        job_id: jobId,
        status: 'running',
        progress: {
          percentage: 45,
          processed: 450,
          total: 1000,
          estimatedRemaining: 120
        },
        stages: [
          { name: '预处理', status: 'completed' },
          { name: '实体抽取', status: 'running' },
          { name: '关系抽取', status: 'pending' }
        ]
      }

      status.value = data

      // 任务完成
      if (data.status === 'completed') {
        stopPolling()
        onComplete?.(data)
      }

      // 任务失败
      if (data.status === 'failed') {
        stopPolling()
        error.value = data.error || '任务执行失败'
        onError?.(error.value)
      }
    } catch (e) {
      error.value = e instanceof Error ? e.message : '获取任务状态失败'
    } finally {
      loading.value = false
    }
  }

  const startPolling = () => {
    isActive = true
    fetchStatus()
    timer = window.setInterval(fetchStatus, interval)
  }

  const stopPolling = () => {
    isActive = false
    if (timer) {
      clearInterval(timer)
      timer = null
    }
  }

  const refresh = () => {
    fetchStatus()
  }

  onMounted(() => {
    if (jobId) {
      startPolling()
    }
  })

  onUnmounted(() => {
    stopPolling()
  })

  return {
    status,
    loading,
    error,
    startPolling,
    stopPolling,
    refresh
  }
}
