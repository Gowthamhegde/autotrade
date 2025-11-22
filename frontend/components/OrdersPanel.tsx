'use client'

import { useState, useEffect } from 'react'
import { AxiosInstance } from 'axios'

interface OrdersPanelProps {
  api: AxiosInstance
}

export default function OrdersPanel({ api }: OrdersPanelProps) {
  const [orders, setOrders] = useState<any[]>([])

  useEffect(() => {
    fetchOrders()
    const interval = setInterval(fetchOrders, 3000)
    return () => clearInterval(interval)
  }, [])

  const fetchOrders = async () => {
    try {
      const res = await api.get('/api/v1/orders')
      setOrders(res.data)
    } catch (err) {
      console.error('Failed to fetch orders', err)
    }
  }

  return (
    <div className="bg-gray-800 rounded-lg p-6">
      <h2 className="text-xl font-bold mb-4">Orders</h2>
      {orders.length === 0 ? (
        <p className="text-gray-400">No orders</p>
      ) : (
        <table className="w-full">
          <thead>
            <tr className="text-left text-gray-400 border-b border-gray-700">
              <th className="pb-2">Time</th>
              <th className="pb-2">Symbol</th>
              <th className="pb-2">Side</th>
              <th className="pb-2">Type</th>
              <th className="pb-2">Qty</th>
              <th className="pb-2">Price</th>
              <th className="pb-2">Status</th>
            </tr>
          </thead>
          <tbody>
            {orders.map((order) => (
              <tr key={order.id} className="border-b border-gray-700">
                <td className="py-3">{new Date(order.created_at).toLocaleTimeString()}</td>
                <td>{order.symbol}</td>
                <td className={order.side === 'buy' ? 'text-green-500' : 'text-red-500'}>
                  {order.side.toUpperCase()}
                </td>
                <td>{order.type.toUpperCase()}</td>
                <td>{order.qty}</td>
                <td>₹{order.price?.toFixed(2) || 'MKT'}</td>
                <td>
                  <span className={`px-2 py-1 rounded text-xs ${
                    order.status === 'filled' ? 'bg-green-600' :
                    order.status === 'pending' ? 'bg-yellow-600' :
                    'bg-gray-600'
                  }`}>
                    {order.status.toUpperCase()}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}
