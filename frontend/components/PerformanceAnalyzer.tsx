"use client";

import { useState, useEffect } from 'react';
import axios from 'axios';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface PerformanceMetrics {
    total_trades: number;
    win_rate: number;
    total_pnl: number;
    profit_factor: number | string;
    max_drawdown: number;
    balance_curve: number[];
}

export default function PerformanceAnalyzer() {
    const [metrics, setMetrics] = useState<PerformanceMetrics | null>(null);

    useEffect(() => {
        const fetchMetrics = async () => {
            try {
                const token = localStorage.getItem('token');
                const res = await axios.get('http://localhost:8005/api/v1/strategies/performance', {
                    headers: { Authorization: `Bearer ${token}` }
                });
                setMetrics(res.data);
            } catch (e) {
                console.error(e);
            }
        };

        fetchMetrics();
        const interval = setInterval(fetchMetrics, 5000);
        return () => clearInterval(interval);
    }, []);

    if (!metrics) return <div className="text-gray-400 text-sm">Loading analytics...</div>;

    const chartData = metrics.balance_curve.map((val, idx) => ({
        trade: idx,
        balance: val
    }));

    return (
        <div className="bg-gray-800/50 backdrop-blur-xl rounded-2xl border border-gray-700/50 shadow-xl overflow-hidden p-6">
            <h3 className="text-gray-400 text-xs uppercase tracking-wider mb-6">Performance Analyzer</h3>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
                <div className="bg-gray-700/30 p-4 rounded-xl">
                    <div className="text-xs text-gray-400 mb-1">Win Rate</div>
                    <div className={`text-xl font-bold ${metrics.win_rate >= 50 ? 'text-green-400' : 'text-red-400'}`}>
                        {metrics.win_rate}%
                    </div>
                </div>
                <div className="bg-gray-700/30 p-4 rounded-xl">
                    <div className="text-xs text-gray-400 mb-1">Total PnL</div>
                    <div className={`text-xl font-bold ${metrics.total_pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                        ₹{metrics.total_pnl.toLocaleString()}
                    </div>
                </div>
                <div className="bg-gray-700/30 p-4 rounded-xl">
                    <div className="text-xs text-gray-400 mb-1">Profit Factor</div>
                    <div className="text-xl font-bold text-blue-400">
                        {metrics.profit_factor}
                    </div>
                </div>
                <div className="bg-gray-700/30 p-4 rounded-xl">
                    <div className="text-xs text-gray-400 mb-1">Max Drawdown</div>
                    <div className="text-xl font-bold text-red-400">
                        ₹{metrics.max_drawdown.toLocaleString()}
                    </div>
                </div>
            </div>

            <div className="h-[200px] w-full">
                <div className="text-xs text-gray-500 mb-2">PnL Curve</div>
                <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={chartData}>
                        <defs>
                            <linearGradient id="colorPnL" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#10B981" stopOpacity={0.3} />
                                <stop offset="95%" stopColor="#10B981" stopOpacity={0} />
                            </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="#374151" vertical={false} />
                        <XAxis hide dataKey="trade" />
                        <YAxis
                            stroke="#9CA3AF"
                            tick={{ fill: '#9CA3AF', fontSize: 10 }}
                            tickLine={false}
                            axisLine={false}
                        />
                        <Tooltip
                            contentStyle={{ backgroundColor: '#1F2937', border: 'none', borderRadius: '8px' }}
                            itemStyle={{ color: '#E5E7EB' }}
                        />
                        <Area
                            type="monotone"
                            dataKey="balance"
                            stroke="#10B981"
                            fillOpacity={1}
                            fill="url(#colorPnL)"
                        />
                    </AreaChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
}
