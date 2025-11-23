'use client'

import { useState, useEffect } from 'react'
import DashboardV2 from '@/components/DashboardV2'
import LoginV2 from '@/components/LoginV2'

export default function Home() {
  const [token, setToken] = useState<string | null>(null)

  useEffect(() => {
    const stored = localStorage.getItem('token')
    if (stored) setToken(stored)
  }, [])

  const handleLogin = (newToken: string) => {
    localStorage.setItem('token', newToken)
    setToken(newToken)
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    setToken(null)
  }

  if (!token) {
    return <LoginV2 onLogin={handleLogin} />
  }

  return <DashboardV2 token={token} onLogout={handleLogout} />
}
