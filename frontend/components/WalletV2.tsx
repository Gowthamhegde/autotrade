'use client'

import { useState, useEffect } from 'react'
import { AxiosInstance } from 'axios'

interface WalletV2Props {
  api: AxiosInstance
}

declare global {
  interface Window {
    Razorpay: any
  }
}

export default function WalletV2({ api }: WalletV2Props) {
  const [wallet, setWallet] = useState<any>(null)
  const [stats, setStats] = useState<any>(null)
  const [transactions, setTransactions] = useState<any[]>([])
  const [showDeposit, setShowDeposit] = useState(false)
  const [showWithdraw, setShowWithdraw] = useState(false)
  const [depositAmount, setDepositAmount] = useState('')
  const [withdrawAmount, setWithdrawAmount] = useState('')
  const [upiId, setUpiId] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchWallet()
    fetchStats()
    fetchTransactions()
    loadRazorpayScript()
    
    const interval = setInterval(fetchWallet, 10000)
    return () => clearInterval(interval)
  }, [])

  const loadRazorpayScript = () => {
    const script = document.createElement('script')
    script.src = 'https://checkout.razorpay.com/v1/checkout.js'
    script.async = true
    document.body.appendChild(script)
  }

  const fetchWallet = async () => {
    try {
      const res = await api.get('/api/v1/wallet/')
      setWallet(res.data)
    } catch (err) {
      console.error('Failed to fetch wallet', err)
    }
  }

  const fetchStats = async () => {
    try {
      const res = await api.get('/api/v1/wallet/stats')
      setStats(res.data)
    } catch (err) {
      console.error('Failed to fetch stats', err)
    }
  }

  const fetchTransactions = async () => {
    try {
      const res = await api.get('/api/v1/wallet/transactions')
      setTransactions(res.data)
    } catch (err) {
      console.error('Failed to fetch transactions', err)
    }
  }

  const handleDeposit = async () => {
    const amount = parseFloat(depositAmount)
    if (!amount || amount < 100) {
      alert('Minimum deposit amount is ₹100')
      return
    }

    setLoading(true)
    try {
      // Initiate deposit
      const res = await api.post('/api/v1/wallet/deposit/initiate', { amount })
      
      // Open Razorpay checkout
      const options = {
        key: res.data.razorpay_key,
        amount: amount * 100,
        currency: 'INR',
        name: 'AutoTrader Pro',
        description: 'Add funds to wallet',
        order_id: res.data.order_id,
        handler: async function (response: any) {
          // Verify payment
          try {
            await api.post('/api/v1/wallet/deposit/verify', {
              razorpay_order_id: response.razorpay_order_id,
              razorpay_payment_id: response.razorpay_payment_id,
              razorpay_signature: response.razorpay_signature
            })
            
            alert(`₹${amount} added successfully!`)
            setDepositAmount('')
            setShowDeposit(false)
            fetchWallet()
            fetchStats()
            fetchTransactions()
          } catch (err: any) {
            alert(err.response?.data?.detail || 'Payment verification failed')
          }
        },
        prefill: {
          name: 'User',
          email: 'user@example.com'
        },
        theme: {
          color: '#3B82F6'
        }
      }

      const rzp = new window.Razorpay(options)
      rzp.open()
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to initiate deposit')
    } finally {
      setLoading(false)
    }
  }

  const handleWithdraw = async () => {
    const amount = parseFloat(withdrawAmount)
    if (!amount || amount < 100) {
      alert('Minimum withdrawal amount is ₹100')
      return
    }

    if (!upiId) {
      alert('Please enter UPI ID')
      return
    }

    setLoading(true)
    try {
      const res = await api.post('/api/v1/wallet/withdraw', {
        amount,
        upi_id: upiId
      })
      
      alert(res.data.message)
      setWithdrawAmount('')
      setUpiId('')
      setShowWithdraw(false)
      fetchWallet()
      fetchStats()
      fetchTransactions()
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Withdrawal failed')
    } finally {
      setLoading(false)
    }
  }

  if (!wallet) return <div className="text-white">Loading...</div>

  return (
    <div className="space-y-6">
      {/* Balance Card */}
      <div className="bg-gradient-to-br from-blue-600 to-purple-600 rounded-xl p-6 shadow-2xl">
        <div className="flex justify-between items-start mb-6">
          <div>
            <p className="text-blue-100 text-sm mb-1">Total Balance</p>
            <h2 className="text-4xl font-bold text-white">₹{wallet.total_balance.toFixed(2)}</h2>
          </div>
          <div className="bg-white/20 backdrop-blur-sm rounded-lg px-4 py-2">
            <p className="text-white text-xs">Available</p>
            <p className="text-white font-bold">₹{wallet.available_balance.toFixed(2)}</p>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <button
            onClick={() => setShowDeposit(true)}
            className="bg-white text-blue-600 font-semibold py-3 px-6 rounded-lg hover:bg-blue-50 transition-colors"
          >
            + Add Money
          </button>
          <button
            onClick={() => setShowWithdraw(true)}
            className="bg-white/20 backdrop-blur-sm text-white font-semibold py-3 px-6 rounded-lg hover:bg-white/30 transition-colors border border-white/30"
          >
            Withdraw
          </button>
        </div>
      </div>

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <p className="text-gray-400 text-sm">Total Deposits</p>
            <p className="text-white text-xl font-bold">₹{stats.total_deposits.toFixed(0)}</p>
          </div>
          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <p className="text-gray-400 text-sm">Total Withdrawals</p>
            <p className="text-white text-xl font-bold">₹{stats.total_withdrawals.toFixed(0)}</p>
          </div>
          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <p className="text-gray-400 text-sm">Total Trades</p>
            <p className="text-white text-xl font-bold">{stats.total_trades}</p>
          </div>
          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <p className="text-gray-400 text-sm">Total Fees</p>
            <p className="text-white text-xl font-bold">₹{stats.total_fees.toFixed(0)}</p>
          </div>
        </div>
      )}

      {/* Transactions */}
      <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
        <h3 className="text-xl font-bold text-white mb-4">Recent Transactions</h3>
        {transactions.length === 0 ? (
          <p className="text-gray-400 text-center py-8">No transactions yet</p>
        ) : (
          <div className="space-y-3">
            {transactions.map((txn) => (
              <div key={txn.id} className="flex justify-between items-center p-4 bg-gray-900/50 rounded-lg">
                <div>
                  <p className="text-white font-medium capitalize">{txn.type}</p>
                  <p className="text-gray-400 text-sm">{new Date(txn.timestamp).toLocaleString()}</p>
                </div>
                <div className="text-right">
                  <p className={`font-bold ${txn.amount >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {txn.amount >= 0 ? '+' : ''}₹{Math.abs(txn.amount).toFixed(2)}
                  </p>
                  <p className="text-gray-400 text-sm">Balance: ₹{txn.balance_after.toFixed(2)}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Deposit Modal */}
      {showDeposit && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-xl p-6 max-w-md w-full mx-4 border border-gray-700">
            <h3 className="text-2xl font-bold text-white mb-4">Add Money</h3>
            <div className="mb-4">
              <label className="block text-gray-300 mb-2">Amount (₹)</label>
              <input
                type="number"
                value={depositAmount}
                onChange={(e) => setDepositAmount(e.target.value)}
                placeholder="Min ₹100"
                className="w-full px-4 py-3 bg-gray-900 text-white rounded-lg border border-gray-700 focus:border-blue-500 focus:outline-none"
              />
            </div>
            <div className="flex gap-3">
              <button
                onClick={handleDeposit}
                disabled={loading}
                className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 rounded-lg disabled:opacity-50"
              >
                {loading ? 'Processing...' : 'Continue to Payment'}
              </button>
              <button
                onClick={() => setShowDeposit(false)}
                className="px-6 bg-gray-700 hover:bg-gray-600 text-white font-semibold py-3 rounded-lg"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Withdraw Modal */}
      {showWithdraw && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-xl p-6 max-w-md w-full mx-4 border border-gray-700">
            <h3 className="text-2xl font-bold text-white mb-4">Withdraw Funds</h3>
            <div className="mb-4">
              <label className="block text-gray-300 mb-2">Amount (₹)</label>
              <input
                type="number"
                value={withdrawAmount}
                onChange={(e) => setWithdrawAmount(e.target.value)}
                placeholder="Min ₹100"
                className="w-full px-4 py-3 bg-gray-900 text-white rounded-lg border border-gray-700 focus:border-blue-500 focus:outline-none"
              />
            </div>
            <div className="mb-4">
              <label className="block text-gray-300 mb-2">UPI ID</label>
              <input
                type="text"
                value={upiId}
                onChange={(e) => setUpiId(e.target.value)}
                placeholder="yourname@upi"
                className="w-full px-4 py-3 bg-gray-900 text-white rounded-lg border border-gray-700 focus:border-blue-500 focus:outline-none"
              />
            </div>
            <div className="flex gap-3">
              <button
                onClick={handleWithdraw}
                disabled={loading}
                className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 rounded-lg disabled:opacity-50"
              >
                {loading ? 'Processing...' : 'Withdraw'}
              </button>
              <button
                onClick={() => setShowWithdraw(false)}
                className="px-6 bg-gray-700 hover:bg-gray-600 text-white font-semibold py-3 rounded-lg"
              >
                Cancel
              </button>
            </div>
            <p className="text-gray-400 text-sm mt-4">
              * Withdrawals are processed in 1-2 business days
            </p>
          </div>
        </div>
      )}
    </div>
  )
}
