"use client";

import { useState, useEffect } from 'react';
import axios from 'axios';

interface Order {
    order_id: string;
    symbol: string;
    side: string;
    qty: number;
    price: number;
    status: string;
    timestamp: string;
}

export default function TradeHistory() {
    const [orders, setOrders] = useState<Order[]>([]);

    useEffect(() => {
        const fetchOrders = async () => {
            try {
                // In a real app, we'd have an endpoint for this. 
                // For now, we'll mock it or assume there's an endpoint.
                // Let's create a simple endpoint in backend or just mock it here for UI demo
                // if the backend doesn't support listing all orders easily yet.
                // But wait, we have 'app.brokers.paper' which stores orders in memory.
                // We need an endpoint to get them.

                const res = await axios.get('http://localhost:8005/api/v1/orders/');
                setOrders(res.data);
            } catch (e) {
                console.error(e);
            }
        };

        const interval = setInterval(fetchOrders, 2000);
        fetchOrders();
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="bg-gray-800/50 backdrop-blur-xl rounded-2xl border border-gray-700/50 shadow-xl overflow-hidden">
            <div className="p-6 border-b border-gray-700/50">
                <h3 className="text-gray-400 text-xs uppercase tracking-wider">Recent Trades</h3>
            </div>
            <div className="overflow-x-auto">
                <table className="w-full text-sm text-left text-gray-400">
                    <thead className="text-xs text-gray-400 uppercase bg-gray-700/50">
                        <tr>
                            <th className="px-6 py-3">Time</th>
                            <th className="px-6 py-3">Symbol</th>
                            <th className="px-6 py-3">Side</th>
                            <th className="px-6 py-3">Price</th>
                            <th className="px-6 py-3">Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {orders.length === 0 ? (
                            <tr>
                                <td colSpan={5} className="px-6 py-4 text-center">No trades yet</td>
                            </tr>
                        ) : (
                            orders.map((order) => (
                                <tr key={order.order_id} className="border-b border-gray-700/50 hover:bg-gray-700/30">
                                    <td className="px-6 py-4">{new Date(order.timestamp).toLocaleTimeString()}</td>
                                    <td className="px-6 py-4 font-medium text-white">{order.symbol}</td>
                                    <td className={`px-6 py-4 ${order.side === 'buy' ? 'text-green-400' : 'text-red-400'}`}>
                                        {order.side.toUpperCase()}
                                    </td>
                                    <td className="px-6 py-4">₹{order.price.toFixed(2)}</td>
                                    <td className="px-6 py-4">
                                        <span className={`px-2 py-1 rounded-full text-xs ${order.status === 'filled' ? 'bg-green-500/20 text-green-400' : 'bg-yellow-500/20 text-yellow-400'
                                            }`}>
                                            {order.status.toUpperCase()}
                                        </span>
                                    </td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
