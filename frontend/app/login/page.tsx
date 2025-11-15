'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/contexts/AuthContext';

export default function LoginPage() {
  const router = useRouter();
  const { login, isAuthenticated, isLoading } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      router.push('/dashboard');
    }
  }, [isAuthenticated, isLoading, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(email, password);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Login failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  if (isLoading || isAuthenticated) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-text-primary-dark">Loading...</div>
      </div>
    );
  }

  return (
    <div className="relative flex min-h-screen w-full flex-col items-center justify-center overflow-x-hidden p-4 bg-background-light dark:bg-background-dark">
      <div className="flex w-full max-w-md flex-col gap-8">
        {/* Header Section */}
        <div className="flex flex-col items-center text-center gap-2">
          <h1 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-white">
            AI Web Proxy Analyzer
          </h1>
          <p className="text-base text-slate-600 dark:text-slate-400">
            Sign In to Your Account
          </p>
        </div>

        {/* Form Container */}
        <div className="flex flex-col gap-6 rounded-xl border border-slate-200/80 bg-white p-6 dark:border-slate-800/80 dark:bg-slate-900/50">
          {error && (
            <div className="rounded-lg bg-red-500/20 p-3 text-sm text-red-400">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="flex flex-col gap-6">
            {/* Email Field */}
            <div className="flex flex-col gap-2">
              <label 
                htmlFor="email" 
                className="text-sm font-medium text-slate-700 dark:text-slate-300"
              >
                Email Address
              </label>
              <input
                id="email"
                name="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="h-11 w-full flex-1 rounded-lg border border-slate-300 bg-transparent px-4 py-2.5 text-sm text-slate-900 placeholder:text-slate-400 focus:border-primary focus:ring-0 dark:border-slate-700 dark:text-white dark:placeholder:text-slate-500"
                placeholder="Enter your email"
              />
            </div>

            {/* Password Field */}
            <div className="flex flex-col gap-2">
              <label 
                htmlFor="password" 
                className="text-sm font-medium text-slate-700 dark:text-slate-300"
              >
                Password
              </label>
              <div className="relative flex w-full items-center">
                <input
                  id="password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="h-11 w-full flex-1 rounded-lg border border-slate-300 bg-transparent px-4 py-2.5 pr-10 text-sm text-slate-900 placeholder:text-slate-400 focus:border-primary focus:ring-0 dark:border-slate-700 dark:text-white dark:placeholder:text-slate-500"
                  placeholder="Enter your password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 flex items-center px-3 text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200"
                >
                  <span className="material-symbols-outlined text-xl">
                    {showPassword ? 'visibility_off' : 'visibility'}
                  </span>
                </button>
              </div>
            </div>

            {/* Forgot Password Link */}
            <div className="flex justify-end">
              <a 
                href="#" 
                className="text-sm font-medium text-primary hover:underline"
              >
                Forgot password?
              </a>
            </div>

            {/* Login Button */}
            <div className="flex flex-col">
              <button
                type="submit"
                disabled={loading}
                className="flex h-11 cursor-pointer items-center justify-center overflow-hidden rounded-lg bg-primary px-5 text-base font-bold text-white transition-colors hover:bg-primary/90 disabled:opacity-50"
              >
                <span className="truncate">
                  {loading ? 'Logging in...' : 'Login'}
                </span>
              </button>
            </div>
          </form>
        </div>

        {/* Footer Text */}
        <p className="text-center text-sm text-slate-500 dark:text-slate-400">
          © 2024 SecureAI Corp. All rights reserved.
        </p>
      </div>
    </div>
  );
}

