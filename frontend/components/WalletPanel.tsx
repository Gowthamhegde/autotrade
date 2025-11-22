'use client'

import { useState, useEffect } from 'react'
import { AxiosInstance } from 'axios'

interface WalletPanelProps {
  api: AxiosInstance
}

export default function WalletPanel({ api }: WalletPanelProps) {
  const [wallet, setWallet] = useState<any>(null)

  useEffect(() => {
    fetchWallet()
    const interval = setInterval(fetchWallet, 5000)
    return () => clearInterval(interval)
  }, [])

  const fetchWallet = async () => {
    try {
      const res = await api.get('/api/v1/wallet')
      setWallet(res.data)
    } catch (err) {
      console.error('Failed to fetch wallet', err)
    }
  }

  if (!wallet) return <div className="bg-gray-800 rounded-lg p-6">Loading...</div>

  return (
    <div className="bg-gray-800 rounded-lg p-6">
      <h2 className="text-xl font-bold mb-4">Wallet</h2>
      <div className="space-y-3">
        <div className="flex justify-between">
          <span className="text-gray-400">Total Balance</span>
          <span className="font-bold">₹{wallet.total_balance.toFixed(2)}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-400">Reserved</span>
          <span className="text-yellow-500">₹{wallet.reserved_balance.toFixed(2)}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-400">Available</span>
          <span className="text-green-500">₹{wallet.available_balance.toFixed(2)}</span>
        </div>
      </div>
    </div>
  )
}
