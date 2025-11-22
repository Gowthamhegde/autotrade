'use client'

import { useState, useEffect } from 'react'
import { AxiosInstance } from 'axios'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

interface PriceChartProps {
  api: AxiosInstance
}

export default function PriceChart({ api }: PriceChartProps) {
  const [tick, setTick] = useState<any>(null)
  const [history, setHistory] = useState<any[]>([])

  useEffect(() => {
    fetchTick()
    const interval = setInterval(fetchTick, 2000)
    return () => clearInterval(interval)
  }, [])

  const fetchTick = async () => {
    try {
      const res = await api.get('/api/v1/market/tick?symbol=NIFTY')
      setTick(res.data)
      
      // Add to history
      setHistory(prev => [...prev.slice(-50), {
        time: new Date(res.data.timestamp).toLocaleTimeString(),
        price: res.data.last
      }])
    } catch (err) {
      console.error('Failed to fetch tick', err)
    }
  }

  return (
    <div className="bg-gray-800 rounded-lg p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold">NIFTY</h2>
        {tick && (
          <div className="text-right">
            <div className="text-2xl font-bold">₹{tick.last.toFixed(2)}</div>
            <div className="text-sm text-gray-400">
              H: {tick.high.toFixed(2)} L: {tick.low.toFixed(2)}
            </div>
          </div>
        )}
      </div>
      
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={history}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis dataKey="time" stroke="#9CA3AF" />
          <YAxis stroke="#9CA3AF" domain={['auto', 'auto']} />
          <Tooltip 
            contentStyle={{ backgroundColor: '#1F2937', border: 'none' }}
            labelStyle={{ color: '#9CA3AF' }}
          />
          <Line type="monotone" dataKey="price" stroke="#3B82F6" dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
