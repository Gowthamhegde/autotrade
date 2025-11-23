"use client";

import { useState, useEffect } from 'react';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { useRouter } from 'next/navigation';
import TradeHistory from './TradeHistory';

interface TickData {
  symbol: string;
  timestamp: string;
  last: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export default function Dashboard() {
  const [data, setData] = useState<any[]>([]);
  const [currentTick, setCurrentTick] = useState<TickData | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [wallet, setWallet] = useState({ total_balance: 0, available_balance: 0 });
  const [isRunning, setIsRunning] = useState(false);
  const [selectedSymbol, setSelectedSymbol] = useState("^NSEI");
  const [showDeposit, setShowDeposit] = useState(false);
  const [depositAmount, setDepositAmount] = useState("");

  const fetchWallet = async () => {
    try {
      const token = localStorage.getItem('token');
      const res = await axios.get('http://localhost:8005/api/v1/wallet/', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setWallet(res.data);
    } catch (e) { console.error(e); }
  };

  const fetchStatus = async () => {
    try {
      const token = localStorage.getItem('token');
      const res = await axios.get('http://localhost:8005/api/v1/market/status', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setIsRunning(res.data.is_running);
      if (res.data.is_running) setSelectedSymbol(res.data.symbol);
    } catch (e) { console.error(e); }
  };

  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
      return;
    }

    fetchWallet();
    fetchStatus();

    const fetchData = async () => {
      try {
        const token = localStorage.getItem('token');
        const response = await axios.get(`http://localhost:8005/api/v1/market/tick?symbol=${encodeURIComponent(selectedSymbol)}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        const tick = response.data;

        setCurrentTick(tick);
        setIsConnected(true);

        setData(prev => {
          const newData = [...prev, { ...tick, time: new Date(tick.timestamp).toLocaleTimeString() }];
          if (newData.length > 50) return newData.slice(newData.length - 50);
          return newData;
        });
      } catch (error) {
        console.error("Error fetching data:", error);
        setIsConnected(false);
      }
    };

    const interval = setInterval(fetchData, 2000);
    fetchData();

    return () => clearInterval(interval);
  }, [selectedSymbol]);

  const handleStart = async () => {
    const token = localStorage.getItem('token');
    await axios.post('http://localhost:8005/api/v1/market/start',
      { symbol: selectedSymbol },
      { headers: { Authorization: `Bearer ${token}` } }
    );
    setIsRunning(true);
  };

  const handleStop = async () => {
    const token = localStorage.getItem('token');
    await axios.post('http://localhost:8005/api/v1/market/stop', {}, {
      headers: { Authorization: `Bearer ${token}` }
    });
    setIsRunning(false);
  };

  const handleDeposit = async () => {
    const token = localStorage.getItem('token');
    await axios.post('http://localhost:8005/api/v1/wallet/deposit',
      { amount: parseFloat(depositAmount) },
      { headers: { Authorization: `Bearer ${token}` } }
    );
    setShowDeposit(false);
    fetchWallet();
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8 font-sans">
      <header className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-600">
            NIFTY AutoTrader
          </h1>
          <p className="text-gray-400 text-sm mt-1">AI-Powered Algorithmic Trading</p>
        </div>
        <div className="flex items-center gap-6">
          <div className="text-right">
            <div className="text-xs text-gray-400">Wallet Balance</div>
            <div className="text-xl font-bold text-green-400">₹{wallet.total_balance.toLocaleString()}</div>
          </div>
          <button
            onClick={() => setShowDeposit(true)}
            className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          >
            Add Funds
          </button>
          <div className={`px-3 py-1 rounded-full text-xs font-medium ${isConnected ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
            {isConnected ? '● System Online' : '○ Disconnected'}
          </div>
        </div>
      </header>

      {/* Controls */}
      <div className="bg-gray-800/30 p-4 rounded-xl mb-8 flex items-center gap-4 border border-gray-700/50">
        <select
          value={selectedSymbol}
          onChange={(e) => setSelectedSymbol(e.target.value)}
          disabled={isRunning}
          className="bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 text-white outline-none focus:border-blue-500"
        >
          <option value="^NSEI">NIFTY 50</option>
          <option value="^NSEBANK">BANK NIFTY</option>
        </select>

        {!isRunning ? (
          <button
            onClick={handleStart}
            className="bg-green-600 hover:bg-green-700 px-6 py-2 rounded-lg font-medium transition-all shadow-lg shadow-green-900/20"
          >
            Start Trading
          </button>
        ) : (
          <button
            onClick={handleStop}
            className="bg-red-600 hover:bg-red-700 px-6 py-2 rounded-lg font-medium transition-all shadow-lg shadow-red-900/20 animate-pulse"
          >
            Stop Trading
          </button>
        )}

        {isRunning && <span className="text-green-400 text-sm ml-auto">● Trading Active on {selectedSymbol}</span>}
      </div>

      {showDeposit && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="bg-gray-800 p-6 rounded-2xl w-96 border border-gray-700 shadow-2xl">
            <h3 className="text-xl font-bold mb-4">Add Funds</h3>
            <input
              type="number"
              value={depositAmount}
              onChange={(e) => setDepositAmount(e.target.value)}
              placeholder="Amount (₹)"
              className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 mb-4 text-white outline-none focus:border-blue-500"
            />
            <div className="flex justify-end gap-2">
              <button onClick={() => setShowDeposit(false)} className="px-4 py-2 text-gray-400 hover:text-white">Cancel</button>
              <button onClick={handleDeposit} className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg">Deposit</button>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        {/* Stats Cards */}
        <div className="bg-gray-800/50 backdrop-blur-xl p-6 rounded-2xl border border-gray-700/50 shadow-xl">
          <h3 className="text-gray-400 text-xs uppercase tracking-wider mb-2">Current Price</h3>
          <div className="text-2xl font-bold text-white">
            {currentTick ? `₹${currentTick.last.toFixed(2)}` : '---'}
          </div>
          <div className={`text-sm mt-1 ${currentTick && currentTick.last >= currentTick.open ? 'text-green-400' : 'text-red-400'}`}>
            {currentTick ? `${((currentTick.last - currentTick.open) / currentTick.open * 100).toFixed(2)}%` : '---'}
          </div>
        </div>

        <div className="bg-gray-800/50 backdrop-blur-xl p-6 rounded-2xl border border-gray-700/50 shadow-xl">
          <h3 className="text-gray-400 text-xs uppercase tracking-wider mb-2">Day High</h3>
          <div className="text-2xl font-bold text-white">
            {currentTick ? `₹${currentTick.high.toFixed(2)}` : '---'}
          </div>
        </div>

        <div className="bg-gray-800/50 backdrop-blur-xl p-6 rounded-2xl border border-gray-700/50 shadow-xl">
          <h3 className="text-gray-400 text-xs uppercase tracking-wider mb-2">Day Low</h3>
          <div className="text-2xl font-bold text-white">
            {currentTick ? `₹${currentTick.low.toFixed(2)}` : '---'}
          </div>
        </div>

        <div className="bg-gray-800/50 backdrop-blur-xl p-6 rounded-2xl border border-gray-700/50 shadow-xl">
          <h3 className="text-gray-400 text-xs uppercase tracking-wider mb-2">Volume</h3>
          <div className="text-2xl font-bold text-white">
            {currentTick ? currentTick.volume.toLocaleString() : '---'}
          </div>
        </div>
      </div>

      {/* Main Chart & History */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 bg-gray-800/50 backdrop-blur-xl p-6 rounded-2xl border border-gray-700/50 shadow-xl h-[500px]">
          <h3 className="text-gray-400 text-xs uppercase tracking-wider mb-6">Real-time Market Data ({selectedSymbol})</h3>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" vertical={false} />
              <XAxis
                dataKey="time"
                stroke="#9CA3AF"
                tick={{ fill: '#9CA3AF', fontSize: 12 }}
                tickLine={false}
                axisLine={false}
              />
              <YAxis
                domain={['auto', 'auto']}
                stroke="#9CA3AF"
                tick={{ fill: '#9CA3AF', fontSize: 12 }}
                tickLine={false}
                axisLine={false}
                tickFormatter={(value) => `₹${value}`}
              />
              <Tooltip
                contentStyle={{ backgroundColor: '#1F2937', border: 'none', borderRadius: '8px', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' }}
                itemStyle={{ color: '#E5E7EB' }}
                labelStyle={{ color: '#9CA3AF' }}
              />
              <Line
                type="monotone"
                dataKey="last"
                stroke="#8B5CF6"
                strokeWidth={3}
                dot={false}
                activeDot={{ r: 6, fill: '#8B5CF6', stroke: '#fff', strokeWidth: 2 }}
                animationDuration={500}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="lg:col-span-1">
          <TradeHistory />
        </div>
      </div>
    </div>
  );
}
