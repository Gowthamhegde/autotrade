'use client'

import { useState, useEffect } from 'react'
import axios from 'axios'

interface LoginV2Props {
  onLogin: (token: string) => void
}

declare global {
  interface Window {
    google: any
    FB: any
  }
}

export default function LoginV2({ onLogin }: LoginV2Props) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleEmailLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const formData = new FormData()
      formData.append('username', email)
      formData.append('password', password)

      const res = await axios.post(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/auth/login`,
        formData
      )
      onLogin(res.data.access_token)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  const handleGoogleLogin = async (response: any) => {
    try {
      const res = await axios.post(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/oauth/google`,
        { token: response.credential }
      )
      onLogin(res.data.access_token)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Google login failed')
    }
  }

  const handleFacebookLogin = () => {
    window.FB.login((response: any) => {
      if (response.authResponse) {
        axios.post(
          `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/oauth/facebook`,
          { access_token: response.authResponse.accessToken }
        ).then(res => {
          onLogin(res.data.access_token)
        }).catch(err => {
          setError(err.response?.data?.detail || 'Facebook login failed')
        })
      }
    }, { scope: 'public_profile,email' })
  }

  // Load Google Sign-In
  useEffect(() => {
    // Only load if client ID is configured
    const googleClientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID
    if (googleClientId && googleClientId !== 'YOUR_GOOGLE_CLIENT_ID') {
      const script = document.createElement('script')
      script.src = 'https://accounts.google.com/gsi/client'
      script.async = true
      script.defer = true
      document.body.appendChild(script)

      script.onload = () => {
        if (window.google) {
          window.google.accounts.id.initialize({
            client_id: googleClientId,
            callback: handleGoogleLogin
          })
          window.google.accounts.id.renderButton(
            document.getElementById('googleSignInButton'),
            { theme: 'filled_blue', size: 'large', width: 350 }
          )
        }
      }
    }

    // Load Facebook SDK
    const facebookAppId = process.env.NEXT_PUBLIC_FACEBOOK_APP_ID
    if (facebookAppId && facebookAppId !== 'YOUR_FACEBOOK_APP_ID') {
      const fbScript = document.createElement('script')
      fbScript.src = 'https://connect.facebook.net/en_US/sdk.js'
      fbScript.async = true
      fbScript.defer = true
      document.body.appendChild(fbScript)

      fbScript.onload = () => {
        window.FB.init({
          appId: facebookAppId,
          cookie: true,
          xfbml: true,
          version: 'v18.0'
        })
      }
    }
  }, [])

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900">
      <div className="bg-gray-800/80 backdrop-blur-lg p-8 rounded-2xl shadow-2xl w-full max-w-md border border-gray-700">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <span className="text-white font-bold text-2xl">AI</span>
          </div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
            AutoTrader Pro
          </h1>
          <p className="text-gray-400 mt-2">AI-Powered Trading Platform</p>
        </div>

        {/* OAuth Buttons - Only show if configured */}
        {(process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || process.env.NEXT_PUBLIC_FACEBOOK_APP_ID) && (
          <>
            <div className="space-y-3 mb-6">
              {process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID && process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID !== 'YOUR_GOOGLE_CLIENT_ID' && (
                <div id="googleSignInButton" className="flex justify-center"></div>
              )}
              
              {process.env.NEXT_PUBLIC_FACEBOOK_APP_ID && process.env.NEXT_PUBLIC_FACEBOOK_APP_ID !== 'YOUR_FACEBOOK_APP_ID' && (
                <button
                  onClick={handleFacebookLogin}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors flex items-center justify-center gap-2"
                >
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                  </svg>
                  Continue with Facebook
                </button>
              )}
            </div>

            <div className="relative mb-6">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-600"></div>
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-4 bg-gray-800 text-gray-400">Or continue with email</span>
              </div>
            </div>
          </>
        )}

        {/* Email Login Form */}
        <form onSubmit={handleEmailLogin} className="space-y-4">
          <div>
            <label className="block text-gray-300 mb-2 font-medium">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-3 bg-gray-900/50 text-white rounded-lg border border-gray-700 focus:border-blue-500 focus:outline-none transition-colors"
              placeholder="your@email.com"
              required
            />
          </div>
          <div>
            <label className="block text-gray-300 mb-2 font-medium">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-3 bg-gray-900/50 text-white rounded-lg border border-gray-700 focus:border-blue-500 focus:outline-none transition-colors"
              placeholder="••••••••"
              required
            />
          </div>
          
          {error && (
            <div className="bg-red-500/10 border border-red-500/50 text-red-400 px-4 py-3 rounded-lg">
              {error}
            </div>
          )}
          
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white font-bold py-3 px-6 rounded-lg transition-all transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg"
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        {/* Demo Credentials */}
        <div className="mt-6 p-4 bg-blue-500/10 border border-blue-500/30 rounded-lg">
          <p className="text-blue-400 text-sm font-semibold mb-2">Demo Account:</p>
          <p className="text-gray-300 text-sm">Email: admin@example.com</p>
          <p className="text-gray-300 text-sm">Password: admin123</p>
        </div>

        {/* Footer */}
        <p className="text-center text-gray-500 text-sm mt-6">
          By signing in, you agree to our Terms & Privacy Policy
        </p>
      </div>
    </div>
  )
}
