'use client'

import { useState, useEffect } from 'react'
import axios from 'axios'
import TradingControl from './TradingControl'
import PositionsPanel from './PositionsPanel'
import OrdersPanel from './OrdersPanel'
import PriceChart from './PriceChart'
import SignalsPanel from './SignalsPanel'
import WalletV2 from './WalletV2'

interface DashboardProps {
  token: string
  onLogout: () => void
}

export default function DashboardV2({ token, onLogout }: DashboardProps) {
  const [activeTab, setActiveTab] = useState('trading')

  const api = axios.create({
    baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    headers: { Authorization: `Bearer ${token}` }
  })

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      {/* Header */}
      <header className="bg-gray-900/80 backdrop-blur-sm border-b border-gray-700 px-6 py-4 sticky top-0 z-50">
        <div className="flex justify-between items-center">
          <div className="flex items-center gap-4">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-xl">AI</span>
            </div>
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
                AutoTrader Pro
              </h1>
              <p className="text-gray-400 text-sm">AI-Powered Trading System</p>
            </div>
          </div>
          <button
            onClick={onLogout}
            className="px-4 py-2 bg-gray-800 hover:bg-gray-700 text-gray-300 rounded-lg transition-colors border border-gray-700"
          >
            Logout
          </button>
        </div>
      </header>

      {/* Tabs */}
      <div className="bg-gray-900/50 backdrop-blur-sm border-b border-gray-700 px-6">
        <div className="flex gap-2">
          {[
            { id: 'trading', label: '🎯 Trading', icon: '▶' },
            { id: 'wallet', label: '💰 Wallet', icon: '💰' },
            { id: 'positions', label: '📊 Positions', icon: '📊' },
            { id: 'orders', label: '📋 Orders', icon: '📋' },
            { id: 'analytics', label: '📈 Analytics', icon: '📈' }
          ].map(tab => (
            <button
              key={tab.id}
              className={`px-6 py-4 font-medium transition-all ${
                activeTab === tab.id
                  ? 'border-b-2 border-blue-500 text-blue-400 bg-blue-500/10'
                  : 'text-gray-400 hover:text-gray-300 hover:bg-gray-800/50'
              }`}
              onClick={() => setActiveTab(tab.id)}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="p-6 max-w-7xl mx-auto">
        {activeTab === 'trading' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 space-y-6">
              <TradingControl api={api} />
              <SignalsPanel api={api} />
            </div>
            <div className="space-y-6">
              <PriceChart api={api} />
              <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl p-6 border border-gray-700">
                <h3 className="text-lg font-bold text-white mb-4">Quick Stats</h3>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Active Trades</span>
                    <span className="text-white font-bold">0</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Win Rate</span>
                    <span className="text-green-400 font-bold">--</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Today's P&L</span>
                    <span className="text-white font-bold">₹0.00</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
        
        {activeTab === 'wallet' && (
          <div className="max-w-4xl">
            <WalletV2 api={api} />
          </div>
        )}
        
        {activeTab === 'positions' && (
          <div className="max-w-6xl">
            <PositionsPanel api={api} />
          </div>
        )}
        
        {activeTab === 'orders' && (
          <div className="max-w-6xl">
            <OrdersPanel api={api} />
          </div>
        )}
        
        {activeTab === 'analytics' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <PriceChart api={api} />
            <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl p-6 border border-gray-700">
              <h3 className="text-xl font-bold text-white mb-4">Performance</h3>
              <p className="text-gray-400">Analytics coming soon...</p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
