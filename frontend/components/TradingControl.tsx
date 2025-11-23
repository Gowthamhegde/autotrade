'use client'

import { useState, useEffect } from 'react'
import { AxiosInstance } from 'axios'

interface TradingControlProps {
  api: AxiosInstance
}

export default function TradingControl({ api }: TradingControlProps) {
  const [isActive, setIsActive] = useState(false)
  const [selectedIndices, setSelectedIndices] = useState<string[]>(['NIFTY'])
  const [indices, setIndices] = useState<any[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchIndices()
    checkStatus()
  }, [])

  const fetchIndices = async () => {
    try {
      const res = await api.get('/api/v1/indices')
      setIndices(res.data.indices)
    } catch (err) {
      console.error('Failed to fetch indices', err)
    }
  }

  const checkStatus = async () => {
    try {
      const res = await api.get('/api/v1/trading/status')
      setIsActive(res.data.is_active)
      if (res.data.symbols.length > 0) {
        setSelectedIndices(res.data.symbols)
      }
    } catch (err) {
      console.error('Failed to check status', err)
    }
  }

  const handleStart = async () => {
    if (selectedIndices.length === 0) {
      alert('Please select at least one index')
      return
    }

    setLoading(true)
    try {
      await api.post('/api/v1/trading/start', { symbols: selectedIndices })
      setIsActive(true)
      alert('Auto-trading started! System will execute trades when patterns match with 90%+ confidence.')
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to start trading')
    } finally {
      setLoading(false)
    }
  }

  const handleStop = async () => {
    setLoading(true)
    try {
      await api.post('/api/v1/trading/stop')
      setIsActive(false)
      alert('Auto-trading stopped')
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to stop trading')
    } finally {
      setLoading(false)
    }
  }

  const toggleIndex = (symbol: string) => {
    if (isActive) return // Can't change while trading
    
    setSelectedIndices(prev =>
      prev.includes(symbol)
        ? prev.filter(s => s !== symbol)
        : [...prev, symbol]
    )
  }

  return (
    <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl p-6 shadow-2xl border border-gray-700">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-white">Auto Trading</h2>
          <p className="text-gray-400 text-sm mt-1">
            AI-powered pattern recognition with 90%+ confidence
          </p>
        </div>
        <div className={`px-4 py-2 rounded-full font-semibold ${
          isActive 
            ? 'bg-green-500/20 text-green-400 animate-pulse' 
            : 'bg-gray-700 text-gray-400'
        }`}>
          {isActive ? '● ACTIVE' : '○ INACTIVE'}
        </div>
      </div>

      {/* Index Selection */}
      <div className="mb-6">
        <label className="block text-gray-300 font-medium mb-3">Select Indices</label>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          {indices.map((index) => (
            <button
              key={index.symbol}
              onClick={() => toggleIndex(index.symbol)}
              disabled={isActive}
              className={`p-4 rounded-lg border-2 transition-all ${
                selectedIndices.includes(index.symbol)
                  ? 'border-blue-500 bg-blue-500/20 text-white'
                  : 'border-gray-600 bg-gray-800/50 text-gray-400 hover:border-gray-500'
              } ${isActive ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
            >
              <div className="font-bold">{index.symbol}</div>
              <div className="text-xs mt-1 opacity-75">{index.name}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Control Buttons */}
      <div className="flex gap-4">
        {!isActive ? (
          <button
            onClick={handleStart}
            disabled={loading || selectedIndices.length === 0}
            className="flex-1 bg-gradient-to-r from-green-600 to-green-500 hover:from-green-500 hover:to-green-400 text-white font-bold py-4 px-6 rounded-lg transition-all transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg"
          >
            {loading ? 'Starting...' : '▶ START TRADING'}
          </button>
        ) : (
          <button
            onClick={handleStop}
            disabled={loading}
            className="flex-1 bg-gradient-to-r from-red-600 to-red-500 hover:from-red-500 hover:to-red-400 text-white font-bold py-4 px-6 rounded-lg transition-all transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg"
          >
            {loading ? 'Stopping...' : '■ STOP TRADING'}
          </button>
        )}
      </div>

      {/* Info */}
      <div className="mt-6 p-4 bg-blue-500/10 border border-blue-500/30 rounded-lg">
        <div className="flex items-start gap-3">
          <span className="text-blue-400 text-xl">ℹ</span>
          <div className="text-sm text-gray-300">
            <p className="font-semibold text-blue-400 mb-1">How it works:</p>
            <ul className="space-y-1 text-gray-400">
              <li>• System analyzes market in real-time</li>
              <li>• Detects patterns: Golden Cross, Breakouts, etc.</li>
              <li>• Executes trades only when confidence ≥ 90%</li>
              <li>• Automatic position management</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}
