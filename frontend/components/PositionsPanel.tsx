'use client'

import { useState, useEffect } from 'react'
import { AxiosInstance } from 'axios'

interface PositionsPanelProps {
  api: AxiosInstance
}

export default function PositionsPanel({ api }: PositionsPanelProps) {
  const [positions, setPositions] = useState<any[]>([])

  useEffect(() => {
    fetchPositions()
    const interval = setInterval(fetchPositions, 3000)
    return () => clearInterval(interval)
  }, [])

  const fetchPositions = async () => {
    try {
      const res = await api.get('/api/v1/positions')
      setPositions(res.data)
    } catch (err) {
      console.error('Failed to fetch positions', err)
    }
  }

  return (
    <div className="bg-gray-800 rounded-lg p-6">
      <h2 className="text-xl font-bold mb-4">Positions</h2>
      {positions.length === 0 ? (
        <p className="text-gray-400">No open positions</p>
      ) : (
        <table className="w-full">
          <thead>
            <tr className="text-left text-gray-400 border-b border-gray-700">
              <th className="pb-2">Symbol</th>
              <th className="pb-2">Side</th>
              <th className="pb-2">Qty</th>
              <th className="pb-2">Avg Price</th>
              <th className="pb-2">Current</th>
              <th className="pb-2">P&L</th>
            </tr>
          </thead>
          <tbody>
            {positions.map((pos) => (
              <tr key={pos.id} className="border-b border-gray-700">
                <td className="py-3">{pos.symbol}</td>
                <td className={pos.side === 'buy' ? 'text-green-500' : 'text-red-500'}>
                  {pos.side.toUpperCase()}
                </td>
                <td>{pos.qty}</td>
                <td>₹{pos.avg_price.toFixed(2)}</td>
                <td>₹{pos.current_price?.toFixed(2) || '-'}</td>
                <td className={pos.unrealized_pnl >= 0 ? 'text-green-500' : 'text-red-500'}>
                  ₹{pos.unrealized_pnl.toFixed(2)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}
