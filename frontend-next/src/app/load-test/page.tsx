'use client'

import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  PlayCircle, 
  StopCircle, 
  BarChart3, 
  Database, 
  Clock, 
  TrendingUp, 
  AlertCircle, 
  CheckCircle, 
  Download,
  Settings,
  Activity,
  Users,
  Zap,
  Monitor,
  Server,
  Timer,
  Target,
  Globe,
  FileText,
  Pause,
  RotateCcw,
  Save,
  Trash2,
  Copy,
  History,
  Terminal,
  Gauge,
  Network,
  HardDrive,
  Cpu,
  MemoryStick,
  Layers,
  Filter,
  Search,
  ArrowUp,
  ArrowDown,
  Maximize2,
  Minimize2,
  X
} from 'lucide-react'
import axios from 'axios'
import toast from 'react-hot-toast'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell, AreaChart, Area } from 'recharts'

// Professional Load Testing Types
interface LoadTestConfig {
  name: string
  databases: string[]
  concurrent_users: number
  requests_per_user: number
  ramp_up_time: number
  test_duration: number
  scenarios: {
    products: boolean
    category: boolean
    search: boolean
    individual: boolean
    cart: boolean
  }
  custom_scenarios: Array<{
    name: string
    endpoint: string
    method: string
    weight: number
    params?: any
  }>
  think_time: number
  timeout: number
  retry_count: number
  environment: string
}

interface LoadTestProgress {
  test_id: string
  status: 'initializing' | 'running' | 'completed' | 'failed' | 'stopped'
  current_database: string
  progress_percentage: number
  elapsed_time: number
  estimated_remaining: number
  current_users: number
  requests_completed: number
  requests_total: number
  current_rps: number
  success_rate: number
  errors: number
  live_metrics: {
    response_time: number
    throughput: number
    error_rate: number
  }
}

interface LoadTestResults {
  test_id: string
  config: LoadTestConfig
  start_time: string
  end_time: string
  duration: number
  comparison_summary: {
    performance_ranking: Array<{
      database: string
      avg_response_time: number
      throughput: number
      success_rate: number
      score: number
    }>
    key_metrics: {
      fastest_avg_response: any
      highest_throughput: any
      most_reliable: any
    }
    recommendations: string[]
  }
  detailed_results: {
    [database: string]: {
      database: string
      test_config: any
      duration: number
      metrics: {
        overall: {
          total_requests: number
          successful_requests: number
          failed_requests: number
          success_rate: number
          requests_per_second: number
          avg_response_time: number
          min_response_time: number
          max_response_time: number
          median_response_time: number
          p95_response_time: number
          p99_response_time: number
        }
        by_scenario: any
        errors: any
      }
    }
  }
}

interface TestHistory {
  test_id: string
  name: string
  timestamp: string
  duration: number
  databases: string[]
  status: 'completed' | 'failed' | 'stopped'
  summary: {
    total_requests: number
    success_rate: number
    avg_response_time: number
  }
}

export default function LoadTestPage() {
  // Configuration State
  const [config, setConfig] = useState<LoadTestConfig>({
    name: '',
    databases: ['aerospike'],
    concurrent_users: 10,
    requests_per_user: 50,
    ramp_up_time: 5,
    test_duration: 60,
    scenarios: {
      products: true,
      category: true,
      search: true,
      individual: true,
      cart: false
    },
    custom_scenarios: [],
    think_time: 0.1,
    timeout: 30,
    retry_count: 3,
    environment: 'development'
  })

  // State Management
  const [capabilities, setCapabilities] = useState<any>(null)
  const [isRunning, setIsRunning] = useState(false)
  const [isPaused, setIsPaused] = useState(false)
  const [results, setResults] = useState<LoadTestResults | null>(null)
  const [progress, setProgress] = useState<LoadTestProgress | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [testHistory, setTestHistory] = useState<TestHistory[]>([])
  const [activeTab, setActiveTab] = useState<'config' | 'progress' | 'results' | 'history'>('config')
  const [savedConfigs, setSavedConfigs] = useState<LoadTestConfig[]>([])
  const [showAdvanced, setShowAdvanced] = useState(false)
  const [liveMetrics, setLiveMetrics] = useState<any[]>([])
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [filterResults, setFilterResults] = useState('')
  const [sortBy, setSortBy] = useState<'name' | 'timestamp' | 'duration'>('timestamp')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc')
  const [selectedHistoryTest, setSelectedHistoryTest] = useState<TestHistory | null>(null)
  const [showHistoryDetails, setShowHistoryDetails] = useState(false)
  const [selectedHistoryResults, setSelectedHistoryResults] = useState<LoadTestResults | null>(null)
  const [loadingHistoryDetails, setLoadingHistoryDetails] = useState(false)
  const [selectedDb, setSelectedDb] = useState<string>('')

  // Refs
  const progressPollingRef = useRef<NodeJS.Timeout | null>(null)
  const liveMetricsRef = useRef<NodeJS.Timeout | null>(null)

  // New: Restore ongoing test on page refresh
  const checkActiveTest = async () => {
    try {
      const response = await axios.get('http://localhost:5001/api/load-test/status')
      if (response.data.status === 'running' && response.data.current_test) {
        // Ensure we are not already polling for this test
        if (!progressPollingRef.current) {
          setIsRunning(true)
          setIsPaused(response.data.is_paused)
          setActiveTab('progress')
          startProgressPolling(response.data.current_test)
        }
      }
    } catch (err) {
      console.error('Failed to check active load test:', err)
    }
  }

  // Load capabilities and history on mount
  useEffect(() => {
    fetchCapabilities()
    loadTestHistory()
    loadSavedConfigs()
    checkActiveTest()  // <- Added to restore active test progress on refresh
  }, [])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (progressPollingRef.current) {
        clearInterval(progressPollingRef.current)
      }
      if (liveMetricsRef.current) {
        clearInterval(liveMetricsRef.current)
      }
    }
  }, [])

  const fetchCapabilities = async () => {
    try {
      const response = await axios.get('http://localhost:5001/api/load-test')
      setCapabilities(response.data)
    } catch (err) {
      console.error('Failed to fetch capabilities:', err)
      toast.error('Failed to load test capabilities')
    }
  }

  const loadTestHistory = () => {
    const history = localStorage.getItem('loadTestHistory')
    if (history) {
      setTestHistory(JSON.parse(history))
    }
  }

  const loadSavedConfigs = () => {
    const configs = localStorage.getItem('savedLoadTestConfigs')
    if (configs) {
      setSavedConfigs(JSON.parse(configs))
    }
  }

  const saveTestHistory = (testResult: LoadTestResults) => {
    const historyItem: TestHistory = {
      test_id: testResult.test_id,
      name: testResult.config.name || `Test ${new Date(testResult.start_time).toLocaleDateString()}`,
      timestamp: testResult.start_time,
      duration: testResult.duration,
      databases: testResult.config.databases,
      status: 'completed',
      summary: {
        total_requests: Object.values(testResult.detailed_results).reduce((sum, db) => sum + db.metrics.overall.total_requests, 0),
        success_rate: Object.values(testResult.detailed_results).reduce((sum, db) => sum + db.metrics.overall.success_rate, 0) / Object.keys(testResult.detailed_results).length,
        avg_response_time: Object.values(testResult.detailed_results).reduce((sum, db) => sum + db.metrics.overall.avg_response_time, 0) / Object.keys(testResult.detailed_results).length
      }
    }
    
    const updatedHistory = [historyItem, ...testHistory].slice(0, 50) // Keep last 50 tests
    setTestHistory(updatedHistory)
    localStorage.setItem('loadTestHistory', JSON.stringify(updatedHistory))
  }

  const saveConfig = () => {
    const configName = config.name.trim() || `Config ${new Date().toLocaleString()}`
    const newConfig = { ...config, name: configName }
    const updatedConfigs = [...savedConfigs, newConfig]
    setSavedConfigs(updatedConfigs)
    localStorage.setItem('savedLoadTestConfigs', JSON.stringify(updatedConfigs))
    toast.success('Configuration saved')
  }

  const loadConfig = (savedConfig: LoadTestConfig) => {
    setConfig(savedConfig)
    toast.success('Configuration loaded')
  }

  const deleteConfig = (index: number) => {
    const updatedConfigs = savedConfigs.filter((_, i) => i !== index)
    setSavedConfigs(updatedConfigs)
    localStorage.setItem('savedLoadTestConfigs', JSON.stringify(updatedConfigs))
    toast.success('Configuration deleted')
  }

  const clearTestHistory = () => {
    if (testHistory.length === 0) {
      toast('No test history to clear')
      return
    }
    
    if (window.confirm(`Are you sure you want to clear all test history? This will delete ${testHistory.length} test records permanently.`)) {
      setTestHistory([])
      localStorage.removeItem('loadTestHistory')
      toast.success('Test history cleared successfully')
    }
  }

  const clearSavedConfigs = () => {
    if (savedConfigs.length === 0) {
      toast('No saved configurations to clear')
      return
    }
    
    if (window.confirm(`Are you sure you want to clear all saved configurations? This will delete ${savedConfigs.length} saved configs permanently.`)) {
      setSavedConfigs([])
      localStorage.removeItem('savedLoadTestConfigs')
      toast.success('Saved configurations cleared successfully')
    }
  }

  const clearAllData = () => {
    const totalItems = testHistory.length + savedConfigs.length
    if (totalItems === 0) {
      toast('No data to clear')
      return
    }
    
    if (window.confirm(`Are you sure you want to clear ALL load test data? This will delete:\n• ${testHistory.length} test history records\n• ${savedConfigs.length} saved configurations\n\nThis action cannot be undone.`)) {
      setTestHistory([])
      setSavedConfigs([])
      localStorage.removeItem('loadTestHistory')
      localStorage.removeItem('savedLoadTestConfigs')
      toast.success('All load test data cleared successfully')
    }
  }

  const startLoadTest = async () => {
    if (config.databases.length === 0) {
      toast.error('Please select at least one database')
      return
    }

    // Ensure test has a name
    const testName = config.name.trim() || `Load Test ${new Date().toLocaleString()}`
    const testConfig = { ...config, name: testName }
    setConfig(testConfig)

    setIsRunning(true)
    setIsPaused(false)
    setError(null)
    setResults(null)
    setProgress(null)
    setActiveTab('progress')
    setLiveMetrics([])

    try {
      const response = await axios.post('http://localhost:5001/api/load-test', {
        ...testConfig,
        databases: testConfig.databases,
        concurrent_users: testConfig.concurrent_users,
        requests_per_user: testConfig.requests_per_user
      })

      if (response.data.status === 'started') {
        toast.success('Load test started')
        startProgressPolling(response.data.test_id)
      } else if (response.data.status === 'completed') {
        // Handle synchronous completion
        setResults(response.data.results)
        setActiveTab('results')
        saveTestHistory(response.data.results)
        toast.success('Load test completed')
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.error || 'Failed to start load test'
      setError(errorMessage)
      toast.error(errorMessage)
    } finally {
      setIsRunning(false)
    }
  }

  const startProgressPolling = (testId: string) => {
    // Prevent multiple polling intervals for the same or different tests
    if (progressPollingRef.current) {
      clearInterval(progressPollingRef.current)
    }
    progressPollingRef.current = setInterval(async () => {
      try {
        const response = await axios.get(`http://localhost:5001/api/load-test/status/${testId}`)
        const progressData = response.data
        
        setProgress(progressData)
        
        // Update live metrics
        if (progressData.live_metrics) {
          setLiveMetrics(prev => [...prev, {
            timestamp: Date.now(),
            ...progressData.live_metrics
          }].slice(-50)) // Keep last 50 data points
        }

        if (progressData.status === 'completed') {
          clearInterval(progressPollingRef.current!)
          
          // Fetch final results
          const resultsResponse = await axios.get(`http://localhost:5001/api/load-test/results/${testId}`)
          setResults(resultsResponse.data)
          setActiveTab('results')
          saveTestHistory(resultsResponse.data)
          toast.success('Load test completed')
          setIsRunning(false)
        } else if (progressData.status === 'failed') {
          clearInterval(progressPollingRef.current!)
          setError(progressData.error || 'Load test failed')
          toast.error('Load test failed')
          setIsRunning(false)
        }
      } catch (err) {
        console.error('Failed to fetch progress:', err)
      }
    }, 1000)
  }

  const stopLoadTest = async () => {
    try {
      await axios.post('http://localhost:5001/api/load-test/stop')
      setIsRunning(false)
      setIsPaused(false)
      if (progressPollingRef.current) {
        clearInterval(progressPollingRef.current)
      }
      toast.success('Load test stopped')
    } catch (err) {
      toast.error('Failed to stop load test')
    }
  }

  const pauseLoadTest = async () => {
    try {
      await axios.post('http://localhost:5001/api/load-test/pause')
      setIsPaused(true)
      toast.success('Load test paused')
    } catch (err) {
      toast.error('Failed to pause load test')
    }
  }

  const resumeLoadTest = async () => {
    try {
      await axios.post('http://localhost:5001/api/load-test/resume')
      setIsPaused(false)
      toast.success('Load test resumed')
    } catch (err) {
      toast.error('Failed to resume load test')
    }
  }

  const exportResults = async (format: 'json' | 'csv' | 'pdf') => {
    if (!results) return
    
    try {
      const response = await axios.get(`http://localhost:5001/api/load-test/export/${results.test_id}?format=${format}`)
      
      if (format === 'json') {
        const dataStr = JSON.stringify(response.data, null, 2)
        const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr)
        const exportFileDefaultName = `load-test-${results.test_id}.json`
        
        const linkElement = document.createElement('a')
        linkElement.setAttribute('href', dataUri)
        linkElement.setAttribute('download', exportFileDefaultName)
        linkElement.click()
        
        toast.success('Results exported as JSON')
      } else if (format === 'csv') {
        // Handle CSV export
        const csvContent = response.data
        const dataUri = 'data:text/csv;charset=utf-8,' + encodeURIComponent(csvContent)
        const exportFileDefaultName = `load-test-${results.test_id}.csv`
        
        const linkElement = document.createElement('a')
        linkElement.setAttribute('href', dataUri)
        linkElement.setAttribute('download', exportFileDefaultName)
        linkElement.click()
        
        toast.success('Results exported as CSV')
      } else if (format === 'pdf') {
        // Handle PDF export
        toast.success('PDF export completed')
      }
    } catch (err) {
      toast.error('Failed to export results')
    }
  }

  const formatTime = (seconds: number) => {
    if (seconds === undefined || seconds === null || isNaN(seconds)) {
      return '0.00ms'
    }
    return `${(seconds * 1000).toFixed(2)}ms`
  }

  const formatDuration = (seconds: number) => {
    if (seconds === undefined || seconds === null || isNaN(seconds)) {
      return '0h 0m 0s'
    }
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    const secs = Math.floor(seconds % 60)
    return `${hours}h ${minutes}m ${secs}s`
  }

  const formatRate = (rate: number) => {
    if (rate === undefined || rate === null || isNaN(rate)) {
      return '0.00 req/s'
    }
    return `${rate.toFixed(2)} req/s`
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'initializing': return 'text-yellow-400'
      case 'running': return 'text-green-400'
      case 'completed': return 'text-blue-400'
      case 'failed': return 'text-red-400'
      case 'stopped': return 'text-gray-400'
      default: return 'text-gray-400'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'initializing': return <Timer className="w-4 h-4" />
      case 'running': return <Activity className="w-4 h-4 animate-pulse" />
      case 'completed': return <CheckCircle className="w-4 h-4" />
      case 'failed': return <AlertCircle className="w-4 h-4" />
      case 'stopped': return <StopCircle className="w-4 h-4" />
      default: return <Clock className="w-4 h-4" />
    }
  }

  const viewHistoryDetails = async (test: TestHistory) => {
    setSelectedHistoryTest(test)
    setShowHistoryDetails(true)
    setLoadingHistoryDetails(true)
    
    try {
      // Try to fetch full results from backend
      const response = await axios.get(`http://localhost:5001/api/load-test/results/${test.test_id}`)
      setSelectedHistoryResults(response.data)
    } catch (err) {
      console.error('Failed to fetch full test results:', err)
      // If backend doesn't have the results, we'll just show basic info
      setSelectedHistoryResults(null)
      toast('Full test results not available from backend')
    } finally {
      setLoadingHistoryDetails(false)
    }
  }

  const closeHistoryDetails = () => {
    setSelectedHistoryTest(null)
    setSelectedHistoryResults(null)
    setShowHistoryDetails(false)
    setLoadingHistoryDetails(false)
  }

  const filteredHistory = testHistory
    .filter(test => test.name.toLowerCase().includes(filterResults.toLowerCase()))
    .sort((a, b) => {
      const aVal = a[sortBy]
      const bVal = b[sortBy]
      if (sortOrder === 'asc') {
        return aVal > bVal ? 1 : -1
      } else {
        return aVal < bVal ? 1 : -1
      }
    })

  // After setting results (when results get set) we'll default selectedDb
  useEffect(() => {
    if (results) {
      const firstDb = Object.keys(results.detailed_results)[0]
      setSelectedDb(firstDb)
    }
  }, [results])

  return (
    <div className={`min-h-screen ${isFullscreen ? 'fixed inset-0 z-50' : ''} bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900`}>
      <div className="container mx-auto px-4 py-6">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-blue-600 rounded-lg">
                <Monitor className="w-8 h-8 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-white">
                  AdminConsole
                </h1>
                {/* <p className="text-slate-400">
                  Professional Database Performance Testing Suite
                </p> */}
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setIsFullscreen(!isFullscreen)}
                className="p-2 bg-slate-700 text-slate-300 rounded-lg hover:bg-slate-600 transition-colors"
              >
                {isFullscreen ? <Minimize2 className="w-5 h-5" /> : <Maximize2 className="w-5 h-5" />}
              </button>
              <div className="flex items-center gap-2 text-sm text-slate-400">
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                System Online
              </div>
            </div>
          </div>

          {/* Navigation Tabs */}
          <div className="flex items-center gap-1 mb-6 p-1 bg-slate-800 rounded-lg">
            {[
              { id: 'config', label: 'Configuration', icon: Settings },
              { id: 'progress', label: 'Progress', icon: Activity },
              { id: 'results', label: 'Results', icon: BarChart3 },
              { id: 'history', label: 'History', icon: History }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  activeTab === tab.id
                    ? 'bg-blue-600 text-white shadow-lg'
                    : 'text-slate-400 hover:text-white hover:bg-slate-700'
                }`}
              >
                <tab.icon className="w-4 h-4" />
                {tab.label}
              </button>
            ))}
          </div>

          {/* Configuration Panel */}
          {activeTab === 'config' && (
            <div className="space-y-6">
              <div className="bg-slate-800 rounded-xl border border-slate-700 p-6">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-xl font-semibold text-white">Test Configuration</h2>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={saveConfig}
                      className="flex items-center gap-2 px-3 py-1.5 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm"
                    >
                      <Save className="w-4 h-4" />
                      Save
                    </button>
                    <button
                      onClick={() => setShowAdvanced(!showAdvanced)}
                      className="flex items-center gap-2 px-3 py-1.5 bg-slate-700 text-slate-300 rounded-lg hover:bg-slate-600 transition-colors text-sm"
                    >
                      <Settings className="w-4 h-4" />
                      Advanced
                    </button>
                  </div>
                </div>

                {/* Basic Configuration */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {/* Test Name */}
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Test Name
                    </label>
                    <input
                      type="text"
                      value={config.name}
                      onChange={(e) => setConfig(prev => ({ ...prev, name: e.target.value }))}
                      className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                      placeholder={`Load Test ${new Date().toLocaleString()}`}
                    />
                  </div>

                  {/* Database Selection */}
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Target Databases
                    </label>
                    <div className="space-y-2">
                      {capabilities?.available_databases.map((db: string) => (
                        <label key={db} className="flex items-center">
                          <input
                            type="checkbox"
                            checked={config.databases.includes(db)}
                            onChange={(e) => {
                              if (e.target.checked) {
                                setConfig(prev => ({
                                  ...prev,
                                  databases: [...prev.databases, db]
                                }))
                              } else {
                                setConfig(prev => ({
                                  ...prev,
                                  databases: prev.databases.filter(d => d !== db)
                                }))
                              }
                            }}
                            className="rounded border-slate-500 text-blue-600 focus:ring-blue-500 bg-slate-700"
                          />
                          <span className="ml-2 text-sm text-slate-300 capitalize flex items-center gap-2">
                            <Database className="w-4 h-4" />
                            {db}
                          </span>
                        </label>
                      ))}
                    </div>
                  </div>

                  {/* Concurrent Users */}
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Concurrent Users
                    </label>
                    <input
                      type="number"
                      value={config.concurrent_users}
                      onChange={(e) => setConfig(prev => ({
                        ...prev,
                        concurrent_users: parseInt(e.target.value) || 1
                      }))}
                      className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                      min="1"
                      max="1000"
                    />
                  </div>

                  {/* Requests per User */}
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Requests per User
                    </label>
                    <input
                      type="number"
                      value={config.requests_per_user}
                      onChange={(e) => setConfig(prev => ({
                        ...prev,
                        requests_per_user: parseInt(e.target.value) || 1
                      }))}
                      className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                      min="1"
                      max="10000"
                    />
                  </div>

                  {/* Environment */}
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Environment
                    </label>
                    <select
                      value={config.environment}
                      onChange={(e) => setConfig(prev => ({ ...prev, environment: e.target.value }))}
                      className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                    >
                      <option value="development">Development</option>
                      <option value="staging">Staging</option>
                      <option value="production">Production</option>
                    </select>
                  </div>
                </div>

                {/* Advanced Configuration */}
                <AnimatePresence>
                  {showAdvanced && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      exit={{ opacity: 0, height: 0 }}
                      className="mt-6 pt-6 border-t border-slate-700"
                    >
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                        {/* Ramp Up Time */}
                        <div>
                          <label className="block text-sm font-medium text-slate-300 mb-2">
                            Ramp Up Time (s)
                          </label>
                          <input
                            type="number"
                            value={config.ramp_up_time}
                            onChange={(e) => setConfig(prev => ({
                              ...prev,
                              ramp_up_time: parseInt(e.target.value) || 0
                            }))}
                            className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                            min="0"
                            max="300"
                          />
                        </div>

                        {/* Test Duration */}
                        <div>
                          <label className="block text-sm font-medium text-slate-300 mb-2">
                            Test Duration (s)
                          </label>
                          <input
                            type="number"
                            value={config.test_duration}
                            onChange={(e) => setConfig(prev => ({
                              ...prev,
                              test_duration: parseInt(e.target.value) || 60
                            }))}
                            className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                            min="10"
                            max="3600"
                          />
                        </div>

                        {/* Think Time */}
                        <div>
                          <label className="block text-sm font-medium text-slate-300 mb-2">
                            Think Time (s)
                          </label>
                          <input
                            type="number"
                            step="0.1"
                            value={config.think_time}
                            onChange={(e) => setConfig(prev => ({
                              ...prev,
                              think_time: parseFloat(e.target.value) || 0
                            }))}
                            className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                            min="0"
                            max="60"
                          />
                        </div>

                        {/* Timeout */}
                        <div>
                          <label className="block text-sm font-medium text-slate-300 mb-2">
                            Timeout (s)
                          </label>
                          <input
                            type="number"
                            value={config.timeout}
                            onChange={(e) => setConfig(prev => ({
                              ...prev,
                              timeout: parseInt(e.target.value) || 30
                            }))}
                            className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                            min="5"
                            max="300"
                          />
                        </div>

                        {/* Retry Count */}
                        <div>
                          <label className="block text-sm font-medium text-slate-300 mb-2">
                            Retry Count
                          </label>
                          <input
                            type="number"
                            value={config.retry_count}
                            onChange={(e) => setConfig(prev => ({
                              ...prev,
                              retry_count: parseInt(e.target.value) || 3
                            }))}
                            className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                            min="0"
                            max="10"
                          />
                        </div>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>

                {/* Control Buttons */}
                <div className="flex items-center justify-between mt-6">
                  <div className="flex items-center gap-4">
                    <button
                      onClick={startLoadTest}
                      disabled={isRunning || config.databases.length === 0}
                      className="flex items-center gap-2 px-6 py-3 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      <PlayCircle className="w-5 h-5" />
                      Start Load Test
                    </button>
                    
                    <button
                      onClick={stopLoadTest}
                      disabled={!isRunning}
                      className="flex items-center gap-2 px-6 py-3 bg-red-600 text-white rounded-lg font-medium hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      <StopCircle className="w-5 h-5" />
                      Stop Test
                    </button>
                  </div>

                  <div className="text-sm text-slate-400">
                    Total Requests: {config.concurrent_users * config.requests_per_user * config.databases.length}
                  </div>
                </div>
              </div>

              {/* Saved Configurations */}
              {savedConfigs.length > 0 && (
                <div className="bg-slate-800 rounded-xl border border-slate-700 p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-white">Saved Configurations</h3>
                    <button
                      onClick={clearSavedConfigs}
                      className="flex items-center gap-2 px-3 py-1.5 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors text-sm"
                    >
                      <Trash2 className="w-4 h-4" />
                      Clear All
                    </button>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {savedConfigs.map((savedConfig, index) => (
                      <div key={index} className="p-4 bg-slate-700 rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-medium text-white">{savedConfig.name}</h4>
                          <button
                            onClick={() => deleteConfig(index)}
                            className="text-red-400 hover:text-red-300"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                        <p className="text-sm text-slate-400 mb-3">
                          {savedConfig.databases.join(', ')} • {savedConfig.concurrent_users} users
                        </p>
                        <div className="flex items-center gap-2">
                          <button
                            onClick={() => loadConfig(savedConfig)}
                            className="flex items-center gap-1 px-3 py-1.5 bg-blue-600 text-white rounded text-sm hover:bg-blue-700 transition-colors"
                          >
                            <Copy className="w-3 h-3" />
                            Load
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Progress Panel */}
          {activeTab === 'progress' && (
            <div className="space-y-6">
              {/* Current Test Status */}
              <div className="bg-slate-800 rounded-xl border border-slate-700 p-6">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-xl font-semibold text-white">Test Progress</h2>
                  <div className="flex items-center gap-2">
                    {progress && (
                      <div className={`flex items-center gap-2 ${getStatusColor(progress.status)}`}>
                        {getStatusIcon(progress.status)}
                        <span className="text-sm font-medium capitalize">{progress.status}</span>
                      </div>
                    )}
                  </div>
                </div>

                {!isRunning && !progress && (
                  <div className="text-center py-12">
                    <Terminal className="w-16 h-16 text-slate-500 mx-auto mb-4" />
                    <p className="text-slate-400">No active load test</p>
                    <p className="text-sm text-slate-500 mt-2">Start a test from the Configuration tab</p>
                  </div>
                )}

                {(isRunning || progress) && (
                  <div className="space-y-6">
                    {/* Progress Bar */}
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm text-slate-400">Overall Progress</span>
                        <span className="text-sm font-medium text-white">
                          {progress?.progress_percentage.toFixed(1)}%
                        </span>
                      </div>
                      <div className="w-full bg-slate-700 rounded-full h-2">
                        <div
                          className="bg-gradient-to-r from-blue-500 to-green-500 h-2 rounded-full transition-all duration-500"
                          style={{ width: `${progress?.progress_percentage || 0}%` }}
                        />
                      </div>
                    </div>

                    {/* Live Metrics */}
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                      <div className="bg-slate-700 rounded-lg p-4">
                        <div className="flex items-center gap-2 mb-2">
                          <Users className="w-5 h-5 text-blue-400" />
                          <span className="text-sm text-slate-400">Active Users</span>
                        </div>
                        <p className="text-2xl font-bold text-white">
                          {progress?.current_users || 0}
                        </p>
                      </div>

                      <div className="bg-slate-700 rounded-lg p-4">
                        <div className="flex items-center gap-2 mb-2">
                          <Zap className="w-5 h-5 text-green-400" />
                          <span className="text-sm text-slate-400">Requests/sec</span>
                        </div>
                        <p className="text-2xl font-bold text-white">
                          {progress?.current_rps.toFixed(1) || '0.0'}
                        </p>
                      </div>

                      <div className="bg-slate-700 rounded-lg p-4">
                        <div className="flex items-center gap-2 mb-2">
                          <Clock className="w-5 h-5 text-yellow-400" />
                          <span className="text-sm text-slate-400">Avg Response</span>
                        </div>
                        <p className="text-2xl font-bold text-white">
                          {progress?.live_metrics.response_time.toFixed(0)}ms
                        </p>
                      </div>

                      <div className="bg-slate-700 rounded-lg p-4">
                        <div className="flex items-center gap-2 mb-2">
                          <CheckCircle className="w-5 h-5 text-green-400" />
                          <span className="text-sm text-slate-400">Success Rate</span>
                        </div>
                        <p className="text-2xl font-bold text-white">
                          {progress?.success_rate.toFixed(1)}%
                        </p>
                      </div>
                    </div>

                    {/* Real-time Chart */}
                    {liveMetrics.length > 0 && (
                      <div className="bg-slate-700 rounded-lg p-4">
                        <h3 className="text-lg font-semibold text-white mb-4">Live Performance</h3>
                        <div className="h-64">
                          <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={liveMetrics}>
                              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                              <XAxis 
                                dataKey="timestamp" 
                                tickFormatter={(value) => new Date(value).toLocaleTimeString()}
                                stroke="#9CA3AF"
                              />
                              <YAxis stroke="#9CA3AF" />
                              <Tooltip 
                                contentStyle={{ 
                                  backgroundColor: '#1F2937', 
                                  border: '1px solid #374151',
                                  borderRadius: '8px',
                                  color: '#F3F4F6'
                                }}
                                labelFormatter={(value) => new Date(value).toLocaleTimeString()}
                              />
                              <Line 
                                type="monotone" 
                                dataKey="response_time" 
                                stroke="#3B82F6" 
                                strokeWidth={2}
                                dot={false}
                                name="Response Time (ms)"
                              />
                              <Line 
                                type="monotone" 
                                dataKey="throughput" 
                                stroke="#10B981" 
                                strokeWidth={2}
                                dot={false}
                                name="Throughput (req/s)"
                              />
                            </LineChart>
                          </ResponsiveContainer>
                        </div>
                      </div>
                    )}

                    {/* Test Details */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div className="bg-slate-700 rounded-lg p-4">
                        <h3 className="text-lg font-semibold text-white mb-4">Test Details</h3>
                        <div className="space-y-3">
                          <div className="flex justify-between">
                            <span className="text-slate-400">Current Database:</span>
                            <span className="text-white font-medium">{progress?.current_database}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-slate-400">Elapsed Time:</span>
                            <span className="text-white font-medium">{formatDuration(progress?.elapsed_time || 0)}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-slate-400">Est. Remaining:</span>
                            <span className="text-white font-medium">{formatDuration(progress?.estimated_remaining || 0)}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-slate-400">Requests Completed:</span>
                            <span className="text-white font-medium">{progress?.requests_completed}/{progress?.requests_total}</span>
                          </div>
                        </div>
                      </div>

                      <div className="bg-slate-700 rounded-lg p-4">
                        <h3 className="text-lg font-semibold text-white mb-4">Error Summary</h3>
                        <div className="space-y-3">
                          <div className="flex justify-between">
                            <span className="text-slate-400">Total Errors:</span>
                            <span className="text-red-400 font-medium">{progress?.errors || 0}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-slate-400">Error Rate:</span>
                            <span className="text-red-400 font-medium">{progress?.live_metrics.error_rate.toFixed(2)}%</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Results Panel */}
          {activeTab === 'results' && (
            <div className="space-y-6">
              {!results && (
                <div className="bg-slate-800 rounded-xl border border-slate-700 p-6">
                  <div className="text-center py-12">
                    <BarChart3 className="w-16 h-16 text-slate-500 mx-auto mb-4" />
                    <p className="text-slate-400">No test results available</p>
                    <p className="text-sm text-slate-500 mt-2">Complete a load test to view results</p>
                  </div>
                </div>
              )}

              {results && (
                <div className="space-y-6">
                  {/* Results Header */}
                  <div className="bg-slate-800 rounded-xl border border-slate-700 p-6">
                    <div className="flex items-center justify-between mb-6">
                      <div>
                        <h2 className="text-xl font-semibold text-white">Test Results</h2>
                        <p className="text-slate-400 text-sm mt-1">
                          {results.config.name} • {new Date(results.start_time).toLocaleString()}
                        </p>
                      </div>
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => exportResults('json')}
                          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                        >
                          <Download className="w-4 h-4" />
                          JSON
                        </button>
                        <button
                          onClick={() => exportResults('csv')}
                          className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                        >
                          <Download className="w-4 h-4" />
                          CSV
                        </button>
                        {/* <button
                          onClick={() => exportResults('pdf')}
                          className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                        >
                          <Download className="w-4 h-4" />
                          PDF
                        </button> */}
                      </div>
                    </div>

                    {/* Performance Ranking */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      {results.comparison_summary.performance_ranking.map((rank, index) => (
                        <div key={rank.database} className="bg-slate-700 rounded-lg p-4">
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-2xl font-bold text-slate-400">#{index + 1}</span>
                            <Database className="w-6 h-6 text-slate-400" />
                          </div>
                          <h4 className="font-semibold text-white capitalize mb-1">{rank.database}</h4>
                          <div className="space-y-1">
                            <p className="text-sm text-slate-400">
                              {formatTime(rank.avg_response_time)} avg response
                            </p>
                            <p className="text-sm text-slate-400">
                              {formatRate(rank.throughput)} throughput
                            </p>
                            <p className="text-sm text-slate-400">
                              {rank.success_rate.toFixed(1)}% success rate
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Key Metrics */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="bg-gradient-to-r from-green-600 to-green-700 rounded-lg p-6">
                      <div className="flex items-center gap-2 mb-2">
                        <Zap className="w-6 h-6 text-white" />
                        <h4 className="font-semibold text-white">Fastest Response</h4>
                      </div>
                      <p className="text-3xl font-bold text-white">
                        {formatTime(results.comparison_summary.key_metrics.fastest_avg_response.avg_response_time)}
                      </p>
                      <p className="text-green-100 text-sm mt-1">
                        {results.comparison_summary.key_metrics.fastest_avg_response.database}
                      </p>
                    </div>
                    
                    <div className="bg-gradient-to-r from-blue-600 to-blue-700 rounded-lg p-6">
                      <div className="flex items-center gap-2 mb-2">
                        <TrendingUp className="w-6 h-6 text-white" />
                        <h4 className="font-semibold text-white">Highest Throughput</h4>
                      </div>
                      <p className="text-3xl font-bold text-white">
                        {formatRate(results.comparison_summary.key_metrics.highest_throughput.requests_per_second)}
                      </p>
                      <p className="text-blue-100 text-sm mt-1">
                        {results.comparison_summary.key_metrics.highest_throughput.database}
                      </p>
                    </div>
                    
                    <div className="bg-gradient-to-r from-purple-600 to-purple-700 rounded-lg p-6">
                      <div className="flex items-center gap-2 mb-2">
                        <CheckCircle className="w-6 h-6 text-white" />
                        <h4 className="font-semibold text-white">Most Reliable</h4>
                      </div>
                      <p className="text-3xl font-bold text-white">
                        {results.comparison_summary.key_metrics.most_reliable.success_rate.toFixed(1)}%
                      </p>
                      <p className="text-purple-100 text-sm mt-1">
                        {results.comparison_summary.key_metrics.most_reliable.database}
                      </p>
                    </div>
                  </div>

                  {/* Database Selector */}
                  <div className="flex items-center gap-2 mb-6">
                    <span className="text-sm text-slate-400">Select Database:</span>
                    <select
                      value={selectedDb}
                      onChange={(e) => setSelectedDb(e.target.value)}
                      className="px-3 py-1.5 bg-slate-700 border border-slate-600 rounded-lg text-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                    >
                      {Object.keys(results.detailed_results).map(db => (
                        <option key={db} value={db}>{db}</option>
                      ))}
                    </select>
                  </div>

                  {/* Detailed Results by Database */}
                  {selectedDb && (
                    (() => {
                      const database = selectedDb
                      const dbResults = results.detailed_results[database]
                      const errorDetails = dbResults.metrics.errors?.details || dbResults.metrics.errors || {}
                      return (
                      <div key={database} className="bg-slate-800 rounded-xl border border-slate-700 p-6">
                        <h3 className="text-xl font-semibold text-white mb-6 capitalize flex items-center gap-2">
                          <Database className="w-6 h-6" />
                          {database} Database Results
                        </h3>

                        {/* Overall Metrics */}
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                          <div className="bg-slate-700 rounded-lg p-4">
                            <div className="flex items-center gap-2 mb-2">
                              <Target className="w-5 h-5 text-blue-400" />
                              <span className="text-sm text-slate-400">Total Requests</span>
                            </div>
                            <p className="text-2xl font-bold text-white">
                              {dbResults.metrics.overall.total_requests.toLocaleString()}
                            </p>
                            <p className="text-sm text-slate-400">
                              {dbResults.metrics.overall.successful_requests.toLocaleString()} successful
                            </p>
                          </div>

                          <div className="bg-slate-700 rounded-lg p-4">
                            <div className="flex items-center gap-2 mb-2">
                              <Clock className="w-5 h-5 text-green-400" />
                              <span className="text-sm text-slate-400">Response Time</span>
                            </div>
                            <p className="text-2xl font-bold text-white">
                              {formatTime(dbResults.metrics.overall.avg_response_time)}
                            </p>
                            <p className="text-sm text-slate-400">
                              P95: {formatTime(dbResults.metrics.overall.p95_response_time)}
                            </p>
                          </div>

                          <div className="bg-slate-700 rounded-lg p-4">
                            <div className="flex items-center gap-2 mb-2">
                              <Zap className="w-5 h-5 text-yellow-400" />
                              <span className="text-sm text-slate-400">Throughput</span>
                            </div>
                            <p className="text-2xl font-bold text-white">
                              {formatRate(dbResults.metrics.overall.requests_per_second)}
                            </p>
                            <p className="text-sm text-slate-400">
                              {dbResults.metrics.overall.success_rate.toFixed(1)}% success rate
                            </p>
                          </div>

                          <div className="bg-slate-700 rounded-lg p-4">
                            <div className="flex items-center gap-2 mb-2">
                              <AlertCircle className="w-5 h-5 text-red-400" />
                              <span className="text-sm text-slate-400">Errors</span>
                            </div>
                            <p className="text-2xl font-bold text-white">
                              {dbResults.metrics.overall.failed_requests.toLocaleString()}
                            </p>
                            <p className="text-sm text-slate-400">
                              {((dbResults.metrics.overall.failed_requests / dbResults.metrics.overall.total_requests) * 100).toFixed(1)}% failure rate
                            </p>
                          </div>
                        </div>

                        {/* Response Time Breakdown */}
                        <div className="mb-6">
                          <h4 className="text-lg font-semibold text-white mb-4">Response Time Distribution</h4>
                          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
                            <div className="bg-slate-700 rounded-lg p-3">
                              <div className="text-sm text-slate-400">Min</div>
                              <div className="text-lg font-bold text-white">{formatTime(dbResults.metrics.overall.min_response_time)}</div>
                            </div>
                            <div className="bg-slate-700 rounded-lg p-3">
                              <div className="text-sm text-slate-400">Median</div>
                              <div className="text-lg font-bold text-white">{formatTime(dbResults.metrics.overall.median_response_time)}</div>
                            </div>
                            <div className="bg-slate-700 rounded-lg p-3">
                              <div className="text-sm text-slate-400">Average</div>
                              <div className="text-lg font-bold text-white">{formatTime(dbResults.metrics.overall.avg_response_time)}</div>
                            </div>
                            <div className="bg-slate-700 rounded-lg p-3">
                              <div className="text-sm text-slate-400">P95</div>
                              <div className="text-lg font-bold text-white">{formatTime(dbResults.metrics.overall.p95_response_time)}</div>
                            </div>
                            <div className="bg-slate-700 rounded-lg p-3">
                              <div className="text-sm text-slate-400">Max</div>
                              <div className="text-lg font-bold text-white">{formatTime(dbResults.metrics.overall.max_response_time)}</div>
                            </div>
                          </div>
                        </div>

                        {/* Per-Scenario Metrics */}
                        {dbResults.metrics.by_scenario && Object.keys(dbResults.metrics.by_scenario).length > 0 && (
                          <div className="mb-6">
                            <h4 className="text-lg font-semibold text-white mb-4">Performance by API Endpoint</h4>
                            <div className="space-y-3">
                              {Object.entries(dbResults.metrics.by_scenario).map(([scenario, metrics]: [string, any]) => (
                                <div key={scenario} className="bg-slate-700 rounded-lg p-4">
                                  <div className="flex items-center justify-between mb-2">
                                    <h5 className="font-medium text-white">{scenario}</h5>
                                    <span className="text-sm text-slate-400">
                                      {metrics.total_requests} requests
                                    </span>
                                  </div>
                                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                                    <div>
                                      <span className="text-sm text-slate-400">Avg Response:</span>
                                      <span className="text-white ml-2">{formatTime(metrics.avg_response_time)}</span>
                                    </div>
                                    <div>
                                      <span className="text-sm text-slate-400">Success Rate:</span>
                                      <span className="text-white ml-2">{metrics.success_rate.toFixed(1)}%</span>
                                    </div>
                                    <div>
                                      <span className="text-sm text-slate-400">P95:</span>
                                      <span className="text-white ml-2">{formatTime(metrics.p95_response_time)}</span>
                                    </div>
                                    <div>
                                      <span className="text-sm text-slate-400">Errors:</span>
                                      <span className="text-white ml-2">{metrics.failed_requests}</span>
                                    </div>
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Error Analysis */}
                        {errorDetails && Object.keys(errorDetails).length > 0 && (
                          <div className="mb-6">
                            <h4 className="text-lg font-semibold text-white mb-4">Error Analysis</h4>
                            <div className="space-y-3">
                              {Object.entries(errorDetails).map(([errorType, errorData]: [string, any]) => (
                                <div key={errorType} className="bg-red-900/20 border border-red-800 rounded-lg p-4">
                                  <div className="flex items-center justify-between mb-2">
                                    <h5 className="font-medium text-red-300">{errorType}</h5>
                                    <span className="text-sm text-red-400">
                                      {errorData.count} occurrences
                                    </span>
                                  </div>
                                  <p className="text-sm text-red-100 mb-2">{errorData.message}</p>
                                  {errorData.endpoints && (
                                    <div>
                                      <span className="text-sm text-red-400">Affected endpoints:</span>
                                      <div className="flex flex-wrap gap-2 mt-1">
                                        {errorData.endpoints.map((endpoint: string, idx: number) => (
                                          <span key={idx} className="text-xs bg-red-800 text-red-200 px-2 py-1 rounded">
                                            {endpoint}
                                          </span>
                                        ))}
                                      </div>
                                    </div>
                                  )}
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                      )
                    })()
                  )}

                  {/* Recommendations */}
                  <div className="bg-slate-800 rounded-xl border border-slate-700 p-6">
                    <h3 className="text-lg font-semibold text-white mb-4">Performance Recommendations</h3>
                    <div className="space-y-3">
                      {results.comparison_summary.recommendations.map((rec, index) => (
                        <div key={index} className="flex items-start gap-3 p-3 bg-yellow-500/10 border border-yellow-500/20 rounded-lg">
                          <AlertCircle className="w-5 h-5 text-yellow-400 mt-0.5 flex-shrink-0" />
                          <p className="text-yellow-100 text-sm">{rec}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* History Panel */}
          {activeTab === 'history' && (
            <div className="space-y-6">
              <div className="bg-slate-800 rounded-xl border border-slate-700 p-6">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-xl font-semibold text-white">Test History</h2>
                  <div className="flex items-center gap-4">
                    {testHistory.length > 0 && (
                      <div className="flex items-center gap-2">
                        <button
                          onClick={clearTestHistory}
                          className="flex items-center gap-2 px-3 py-1.5 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors text-sm"
                        >
                          <Trash2 className="w-4 h-4" />
                          Clear History
                        </button>
                        <button
                          onClick={clearAllData}
                          className="flex items-center gap-2 px-3 py-1.5 bg-red-800 text-white rounded-lg hover:bg-red-900 transition-colors text-sm"
                        >
                          <Trash2 className="w-4 h-4" />
                          Clear All Data
                        </button>
                      </div>
                    )}
                    <div className="flex items-center gap-2">
                      <Search className="w-4 h-4 text-slate-400" />
                      <input
                        type="text"
                        placeholder="Search tests..."
                        value={filterResults}
                        onChange={(e) => setFilterResults(e.target.value)}
                        className="px-3 py-1.5 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                      />
                    </div>
                    <div className="flex items-center gap-2">
                      <Filter className="w-4 h-4 text-slate-400" />
                      <select
                        value={sortBy}
                        onChange={(e) => setSortBy(e.target.value as any)}
                        className="px-3 py-1.5 bg-slate-700 border border-slate-600 rounded-lg text-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                      >
                        <option value="timestamp">Date</option>
                        <option value="name">Name</option>
                        <option value="duration">Duration</option>
                      </select>
                      <button
                        onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
                        className="p-1.5 bg-slate-700 text-slate-300 rounded-lg hover:bg-slate-600 transition-colors"
                      >
                        {sortOrder === 'asc' ? <ArrowUp className="w-4 h-4" /> : <ArrowDown className="w-4 h-4" />}
                      </button>
                    </div>
                  </div>
                </div>

                {filteredHistory.length === 0 && (
                  <div className="text-center py-12">
                    <History className="w-16 h-16 text-slate-500 mx-auto mb-4" />
                    <p className="text-slate-400">No test history available</p>
                    <p className="text-sm text-slate-500 mt-2">Your completed tests will appear here</p>
                  </div>
                )}

                {filteredHistory.length > 0 && (
                  <div className="space-y-4">
                    {filteredHistory.map((test, index) => (
                      <div key={test.test_id} className="bg-slate-700 rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center gap-3">
                            <div className={`w-3 h-3 rounded-full ${
                              test.status === 'completed' ? 'bg-green-400' : 
                              test.status === 'failed' ? 'bg-red-400' : 'bg-gray-400'
                            }`} />
                            <h4 className="font-medium text-white">{test.name}</h4>
                          </div>
                          <div className="flex items-center gap-2">
                            <span className="text-sm text-slate-400">
                              {new Date(test.timestamp).toLocaleString()}
                            </span>
                            <button 
                              onClick={() => viewHistoryDetails(test)}
                              className="text-blue-400 hover:text-blue-300 transition-colors"
                              title="View Details"
                            >
                              <FileText className="w-4 h-4" />
                            </button>
                          </div>
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
                          <div>
                            <span className="text-slate-400">Duration:</span>
                            <span className="text-white ml-2">{formatDuration(test.duration)}</span>
                          </div>
                          <div>
                            <span className="text-slate-400">Databases:</span>
                            <span className="text-white ml-2">{test.databases.join(', ')}</span>
                          </div>
                          <div>
                            <span className="text-slate-400">Requests:</span>
                            <span className="text-white ml-2">{test.summary.total_requests.toLocaleString()}</span>
                          </div>
                          <div>
                            <span className="text-slate-400">Success Rate:</span>
                            <span className="text-white ml-2">{test.summary.success_rate.toFixed(1)}%</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Error Panel */}
          <AnimatePresence>
            {error && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="fixed bottom-4 right-4 max-w-md bg-red-600 border border-red-500 rounded-lg p-4 shadow-lg"
              >
                <div className="flex items-center gap-2 mb-2">
                  <AlertCircle className="w-5 h-5 text-white" />
                  <h3 className="font-semibold text-white">Error</h3>
                </div>
                <p className="text-red-100 text-sm">{error}</p>
                <button
                  onClick={() => setError(null)}
                  className="absolute top-2 right-2 text-red-200 hover:text-white"
                >
                  ×
                </button>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* History Details Modal */}
      {showHistoryDetails && selectedHistoryTest && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-slate-800 rounded-xl border border-slate-700 p-6 max-w-6xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-semibold text-white">Test Details - {selectedHistoryTest.name}</h3>
              <button
                onClick={closeHistoryDetails}
                className="text-slate-400 hover:text-white transition-colors"
              >
                <X className="w-6 h-6" />
              </button>
            </div>
            
            {loadingHistoryDetails ? (
              <div className="text-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
                <p className="text-slate-400">Loading detailed results...</p>
              </div>
            ) : (
              <div className="space-y-6">
                {/* Test Information */}
                <div className="bg-slate-700 rounded-lg p-4">
                  <h4 className="text-lg font-semibold text-white mb-4">Test Information</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <span className="text-slate-400">Test Name:</span>
                      <span className="text-white ml-2">{selectedHistoryTest.name}</span>
                    </div>
                    <div>
                      <span className="text-slate-400">Test ID:</span>
                      <span className="text-white ml-2 font-mono text-sm">{selectedHistoryTest.test_id}</span>
                    </div>
                    <div>
                      <span className="text-slate-400">Start Time:</span>
                      <span className="text-white ml-2">{new Date(selectedHistoryTest.timestamp).toLocaleString()}</span>
                    </div>
                    <div>
                      <span className="text-slate-400">Duration:</span>
                      <span className="text-white ml-2">{formatDuration(selectedHistoryTest.duration)}</span>
                    </div>
                    <div>
                      <span className="text-slate-400">Status:</span>
                      <span className={`ml-2 font-medium ${
                        selectedHistoryTest.status === 'completed' ? 'text-green-400' :
                        selectedHistoryTest.status === 'failed' ? 'text-red-400' : 'text-yellow-400'
                      }`}>
                        {selectedHistoryTest.status.toUpperCase()}
                      </span>
                    </div>
                    <div>
                      <span className="text-slate-400">Databases:</span>
                      <span className="text-white ml-2">{selectedHistoryTest.databases.join(', ')}</span>
                    </div>
                  </div>
                </div>

                {/* Summary Metrics */}
                <div className="bg-slate-700 rounded-lg p-4">
                  <h4 className="text-lg font-semibold text-white mb-4">Summary Metrics</h4>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-blue-400">{selectedHistoryTest.summary.total_requests.toLocaleString()}</div>
                      <div className="text-sm text-slate-400">Total Requests</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-green-400">{selectedHistoryTest.summary.success_rate.toFixed(1)}%</div>
                      <div className="text-sm text-slate-400">Success Rate</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-yellow-400">{formatTime(selectedHistoryTest.summary.avg_response_time)}</div>
                      <div className="text-sm text-slate-400">Avg Response Time</div>
                    </div>
                  </div>
                </div>

                {/* Full Detailed Results - Only show if we have the full results */}
                {selectedHistoryResults ? (
                  <>
                    {/* Performance Ranking */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      {selectedHistoryResults.comparison_summary.performance_ranking.map((rank, index) => (
                        <div key={rank.database} className="bg-slate-700 rounded-lg p-4">
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-2xl font-bold text-slate-400">#{index + 1}</span>
                            <Database className="w-6 h-6 text-slate-400" />
                          </div>
                          <h4 className="font-semibold text-white capitalize mb-1">{rank.database}</h4>
                          <div className="space-y-1">
                            <p className="text-sm text-slate-400">
                              {formatTime(rank.avg_response_time)} avg response
                            </p>
                            <p className="text-sm text-slate-400">
                              {formatRate(rank.throughput)} throughput
                            </p>
                            <p className="text-sm text-slate-400">
                              {rank.success_rate.toFixed(1)}% success rate
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>

                    {/* Key Metrics */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                      <div className="bg-gradient-to-r from-green-600 to-green-700 rounded-lg p-6">
                        <div className="flex items-center gap-2 mb-2">
                          <Zap className="w-6 h-6 text-white" />
                          <h4 className="font-semibold text-white">Fastest Response</h4>
                        </div>
                        <p className="text-3xl font-bold text-white">
                          {formatTime(selectedHistoryResults.comparison_summary.key_metrics.fastest_avg_response.avg_response_time)}
                        </p>
                        <p className="text-green-100 text-sm mt-1">
                          {selectedHistoryResults.comparison_summary.key_metrics.fastest_avg_response.database}
                        </p>
                      </div>
                      
                      <div className="bg-gradient-to-r from-blue-600 to-blue-700 rounded-lg p-6">
                        <div className="flex items-center gap-2 mb-2">
                          <TrendingUp className="w-6 h-6 text-white" />
                          <h4 className="font-semibold text-white">Highest Throughput</h4>
                        </div>
                        <p className="text-3xl font-bold text-white">
                          {formatRate(selectedHistoryResults.comparison_summary.key_metrics.highest_throughput.requests_per_second)}
                        </p>
                        <p className="text-blue-100 text-sm mt-1">
                          {selectedHistoryResults.comparison_summary.key_metrics.highest_throughput.database}
                        </p>
                      </div>
                      
                      <div className="bg-gradient-to-r from-purple-600 to-purple-700 rounded-lg p-6">
                        <div className="flex items-center gap-2 mb-2">
                          <CheckCircle className="w-6 h-6 text-white" />
                          <h4 className="font-semibold text-white">Most Reliable</h4>
                        </div>
                        <p className="text-3xl font-bold text-white">
                          {selectedHistoryResults.comparison_summary.key_metrics.most_reliable.success_rate.toFixed(1)}%
                        </p>
                        <p className="text-purple-100 text-sm mt-1">
                          {selectedHistoryResults.comparison_summary.key_metrics.most_reliable.database}
                        </p>
                      </div>
                    </div>

                    {/* Detailed Results by Database */}
                    {Object.entries(selectedHistoryResults.detailed_results).map(([database, dbResults]) => {
                      const errorDetails = dbResults.metrics.errors?.details || dbResults.metrics.errors || {}
                      return (
                      <div key={database} className="bg-slate-700 rounded-lg p-6">
                        <h4 className="text-xl font-semibold text-white mb-6 capitalize flex items-center gap-2">
                          <Database className="w-6 h-6" />
                          {database} Database Results
                        </h4>

                        {/* Overall Metrics */}
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                          <div className="bg-slate-600 rounded-lg p-4">
                            <div className="flex items-center gap-2 mb-2">
                              <Target className="w-5 h-5 text-blue-400" />
                              <span className="text-sm text-slate-400">Total Requests</span>
                            </div>
                            <p className="text-2xl font-bold text-white">
                              {dbResults.metrics.overall.total_requests.toLocaleString()}
                            </p>
                            <p className="text-sm text-slate-400">
                              {dbResults.metrics.overall.successful_requests.toLocaleString()} successful
                            </p>
                          </div>

                          <div className="bg-slate-600 rounded-lg p-4">
                            <div className="flex items-center gap-2 mb-2">
                              <Clock className="w-5 h-5 text-green-400" />
                              <span className="text-sm text-slate-400">Response Time</span>
                            </div>
                            <p className="text-2xl font-bold text-white">
                              {formatTime(dbResults.metrics.overall.avg_response_time)}
                            </p>
                            <p className="text-sm text-slate-400">
                              P95: {formatTime(dbResults.metrics.overall.p95_response_time)}
                            </p>
                          </div>

                          <div className="bg-slate-600 rounded-lg p-4">
                            <div className="flex items-center gap-2 mb-2">
                              <Zap className="w-5 h-5 text-yellow-400" />
                              <span className="text-sm text-slate-400">Throughput</span>
                            </div>
                            <p className="text-2xl font-bold text-white">
                              {formatRate(dbResults.metrics.overall.requests_per_second)}
                            </p>
                            <p className="text-sm text-slate-400">
                              {dbResults.metrics.overall.success_rate.toFixed(1)}% success rate
                            </p>
                          </div>

                          <div className="bg-slate-600 rounded-lg p-4">
                            <div className="flex items-center gap-2 mb-2">
                              <AlertCircle className="w-5 h-5 text-red-400" />
                              <span className="text-sm text-slate-400">Errors</span>
                            </div>
                            <p className="text-2xl font-bold text-white">
                              {dbResults.metrics.overall.failed_requests.toLocaleString()}
                            </p>
                            <p className="text-sm text-slate-400">
                              {((dbResults.metrics.overall.failed_requests / dbResults.metrics.overall.total_requests) * 100).toFixed(1)}% failure rate
                            </p>
                          </div>
                        </div>

                        {/* Response Time Breakdown */}
                        <div className="mb-6">
                          <h5 className="text-lg font-semibold text-white mb-4">Response Time Distribution</h5>
                          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
                            <div className="bg-slate-600 rounded-lg p-3">
                              <div className="text-sm text-slate-400">Min</div>
                              <div className="text-lg font-bold text-white">{formatTime(dbResults.metrics.overall.min_response_time)}</div>
                            </div>
                            <div className="bg-slate-600 rounded-lg p-3">
                              <div className="text-sm text-slate-400">Median</div>
                              <div className="text-lg font-bold text-white">{formatTime(dbResults.metrics.overall.median_response_time)}</div>
                            </div>
                            <div className="bg-slate-600 rounded-lg p-3">
                              <div className="text-sm text-slate-400">Average</div>
                              <div className="text-lg font-bold text-white">{formatTime(dbResults.metrics.overall.avg_response_time)}</div>
                            </div>
                            <div className="bg-slate-600 rounded-lg p-3">
                              <div className="text-sm text-slate-400">P95</div>
                              <div className="text-lg font-bold text-white">{formatTime(dbResults.metrics.overall.p95_response_time)}</div>
                            </div>
                            <div className="bg-slate-600 rounded-lg p-3">
                              <div className="text-sm text-slate-400">Max</div>
                              <div className="text-lg font-bold text-white">{formatTime(dbResults.metrics.overall.max_response_time)}</div>
                            </div>
                          </div>
                        </div>

                        {/* Per-Scenario Metrics */}
                        {dbResults.metrics.by_scenario && Object.keys(dbResults.metrics.by_scenario).length > 0 && (
                          <div className="mb-6">
                            <h5 className="text-lg font-semibold text-white mb-4">Performance by API Endpoint</h5>
                            <div className="space-y-3">
                              {Object.entries(dbResults.metrics.by_scenario).map(([scenario, metrics]: [string, any]) => (
                                <div key={scenario} className="bg-slate-600 rounded-lg p-4">
                                  <div className="flex items-center justify-between mb-2">
                                    <h6 className="font-medium text-white">{scenario}</h6>
                                    <span className="text-sm text-slate-400">
                                      {metrics.total_requests} requests
                                    </span>
                                  </div>
                                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                                    <div>
                                      <span className="text-sm text-slate-400">Avg Response:</span>
                                      <span className="text-white ml-2">{formatTime(metrics.avg_response_time)}</span>
                                    </div>
                                    <div>
                                      <span className="text-sm text-slate-400">Success Rate:</span>
                                      <span className="text-white ml-2">{metrics.success_rate.toFixed(1)}%</span>
                                    </div>
                                    <div>
                                      <span className="text-sm text-slate-400">P95:</span>
                                      <span className="text-white ml-2">{formatTime(metrics.p95_response_time)}</span>
                                    </div>
                                    <div>
                                      <span className="text-sm text-slate-400">Errors:</span>
                                      <span className="text-white ml-2">{metrics.failed_requests}</span>
                                    </div>
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Error Analysis */}
                        {errorDetails && Object.keys(errorDetails).length > 0 && (
                          <div className="mb-6">
                            <h5 className="text-lg font-semibold text-white mb-4">Error Analysis</h5>
                            <div className="space-y-3">
                              {Object.entries(errorDetails).map(([errorType, errorData]: [string, any]) => (
                                <div key={errorType} className="bg-red-900/20 border border-red-800 rounded-lg p-4">
                                  <div className="flex items-center justify-between mb-2">
                                    <h6 className="font-medium text-red-300">{errorType}</h6>
                                    <span className="text-sm text-red-400">
                                      {errorData.count} occurrences
                                    </span>
                                  </div>
                                  <p className="text-sm text-red-100 mb-2">{errorData.message}</p>
                                  {errorData.endpoints && (
                                    <div>
                                      <span className="text-sm text-red-400">Affected endpoints:</span>
                                      <div className="flex flex-wrap gap-2 mt-1">
                                        {errorData.endpoints.map((endpoint: string, idx: number) => (
                                          <span key={idx} className="text-xs bg-red-800 text-red-200 px-2 py-1 rounded">
                                            {endpoint}
                                          </span>
                                        ))}
                                      </div>
                                    </div>
                                  )}
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                      )
                    })}

                    {/* Recommendations */}
                    <div className="bg-slate-700 rounded-lg p-4">
                      <h4 className="text-lg font-semibold text-white mb-4">Performance Recommendations</h4>
                      <div className="space-y-3">
                        {selectedHistoryResults.comparison_summary.recommendations.map((rec, index) => (
                          <div key={index} className="flex items-start gap-3 p-3 bg-yellow-500/10 border border-yellow-500/20 rounded-lg">
                            <AlertCircle className="w-5 h-5 text-yellow-400 mt-0.5 flex-shrink-0" />
                            <p className="text-yellow-100 text-sm">{rec}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  </>
                ) : (
                  <div className="bg-slate-700 rounded-lg p-6 text-center">
                    <AlertCircle className="w-12 h-12 text-yellow-400 mx-auto mb-4" />
                    <h4 className="text-lg font-semibold text-white mb-2">Detailed Results Not Available</h4>
                    <p className="text-slate-400 mb-4">
                      Full test results are not available from the backend. This could be because:
                    </p>
                    <ul className="text-sm text-slate-400 text-left max-w-md mx-auto">
                      <li>• The backend server was restarted after the test</li>
                      <li>• The test results have been cleared from memory</li>
                      <li>• The test was run with a different backend instance</li>
                    </ul>
                    <p className="text-slate-400 mt-4">Only summary metrics are shown above.</p>
                  </div>
                )}

                {/* Actions */}
                <div className="flex justify-end gap-3">
                  <button
                    onClick={closeHistoryDetails}
                    className="px-4 py-2 bg-slate-600 text-white rounded-lg hover:bg-slate-500 transition-colors"
                  >
                    Close
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
} 