'use client'

import { useState, useEffect } from 'react'
import { AxiosInstance } from 'axios'

interface SignalsPanelProps {
  api: AxiosInstance
}

export default function SignalsPanel({ api }: SignalsPanelProps) {
  const [signals, setSignals] = useState<any[]>([])

  useEffect(() => {
    fetchSignals()
    const interval = setInterval(fetchSignals, 5000)
    return () => clearInterval(interval)
  }, [])

  const fetchSignals = async () => {
    try {
      const res = await api.get('/api/v1/trading/signals')
      setSignals(res.data.signals || [])
    } catch (err) {
      console.error('Failed to fetch signals', err)
    }
  }

  return (
    <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl p-6 shadow-2xl border border-gray-700">
      <h2 className="text-xl font-bold text-white mb-4">Recent Signals</h2>
      {signals.length === 0 ? (
        <div className="text-center py-8">
          <div className="text-gray-500 text-5xl mb-3">📡</div>
          <p className="text-gray-400">No signals yet</p>
          <p className="text-gray-500 text-sm mt-1">Start trading to see real-time signals</p>
        </div>
      ) : (
        <div className="space-y-3">
          {signals.map((signal, idx) => (
            <div
              key={idx}
              className="p-4 bg-gray-800/50 rounded-lg border border-gray-700 hover:border-gray-600 transition-colors"
            >
              <div className="flex justify-between items-start">
                <div>
                  <div className="flex items-center gap-2">
                    <span className={`font-bold ${
                      signal.action === 'BUY' ? 'text-green-400' : 'text-red-400'
                    }`}>
                      {signal.action}
                    </span>
                    <span className="text-white font-semibold">{signal.symbol}</span>
                  </div>
                  <p className="text-gray-400 text-sm mt-1">{signal.pattern_name}</p>
                  <p className="text-gray-500 text-xs mt-1">{signal.reason}</p>
                </div>
                <div className="text-right">
                  <div className="text-white font-bold">₹{signal.price?.toFixed(2)}</div>
                  <div className={`text-sm font-semibold ${
                    signal.confidence >= 0.9 ? 'text-green-400' : 'text-yellow-400'
                  }`}>
                    {(signal.confidence * 100).toFixed(0)}% confidence
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
