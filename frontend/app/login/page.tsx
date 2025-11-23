"use client";

import { useState } from 'react';
import axios from 'axios';
import { useRouter } from 'next/navigation';

export default function Login() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const router = useRouter();

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            const formData = new FormData();
            formData.append('username', email);
            formData.append('password', password);

            const res = await axios.post('http://localhost:8005/api/v1/auth/token', formData);
            localStorage.setItem('token', res.data.access_token);

            // Set default header for future requests
            axios.defaults.headers.common['Authorization'] = `Bearer ${res.data.access_token}`;

            router.push('/dashboard');
        } catch (err) {
            setError("Invalid credentials");
        }
    };

    return (
        <div className="min-h-screen bg-gray-900 flex items-center justify-center text-white">
            <div className="bg-gray-800 p-8 rounded-2xl shadow-2xl w-96 border border-gray-700">
                <h2 className="text-2xl font-bold mb-6 text-center bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-600">
                    NIFTY AutoTrader
                </h2>

                {error && <div className="bg-red-500/20 text-red-400 p-3 rounded-lg mb-4 text-sm">{error}</div>}

                <form onSubmit={handleLogin} className="space-y-4">
                    <div>
                        <label className="block text-sm text-gray-400 mb-1">Email</label>
                        <input
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 outline-none focus:border-blue-500"
                            placeholder="admin@example.com"
                        />
                    </div>

                    <div>
                        <label className="block text-sm text-gray-400 mb-1">Password</label>
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 outline-none focus:border-blue-500"
                            placeholder="admin123"
                        />
                    </div>

                    <button
                        type="submit"
                        className="w-full bg-blue-600 hover:bg-blue-700 py-2 rounded-lg font-medium transition-colors"
                    >
                        Login
                    </button>
                </form>

                <div className="mt-4 text-center text-xs text-gray-500">
                    Demo Credentials: admin@example.com / admin123
                </div>
            </div>
        </div>
    );
}
