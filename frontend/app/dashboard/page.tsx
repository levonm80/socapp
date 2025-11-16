'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useAuth } from '@/lib/contexts/AuthContext';
import { dashboardApi, DashboardStats, TimelineData, RecentLogs, TopCategories } from '@/lib/api/dashboard';
import { logsApi, LogEntry } from '@/lib/api/logs';
import LogEntryDetailModal from '../logs/LogEntryDetailModal';

export default function DashboardPage() {
  const { isAuthenticated, isLoading } = useAuth();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [timeline, setTimeline] = useState<TimelineData | null>(null);
  const [categories, setCategories] = useState<TopCategories | null>(null);
  const [recentLogs, setRecentLogs] = useState<RecentLogs | null>(null);
  const [recentLogEntries, setRecentLogEntries] = useState<LogEntry[]>([]);
  const [selectedEntry, setSelectedEntry] = useState<LogEntry | null>(null);
  
  // Individual loading states for each section
  const [loadingStats, setLoadingStats] = useState(false);
  const [loadingTimeline, setLoadingTimeline] = useState(false);
  const [loadingCategories, setLoadingCategories] = useState(false);
  const [loadingRecentLogs, setLoadingRecentLogs] = useState(false);
  
  // Individual error states for each section
  const [errorStats, setErrorStats] = useState<string | null>(null);
  const [errorTimeline, setErrorTimeline] = useState<string | null>(null);
  const [errorCategories, setErrorCategories] = useState<string | null>(null);
  const [errorRecentLogs, setErrorRecentLogs] = useState<string | null>(null);
  
  const [lastUpdated, setLastUpdated] = useState<string>('Just now');

  // Helper function to fetch stats independently
  const fetchStats = async () => {
    try {
      setLoadingStats(true);
      setErrorStats(null);
      const data = await dashboardApi.getStats();
      setStats(data);
    } catch (err: any) {
      setErrorStats(err.response?.data?.error || 'Failed to load stats');
      console.error('Stats error:', err);
    } finally {
      setLoadingStats(false);
    }
  };

  // Helper function to fetch timeline independently using v2 endpoint
  const fetchTimeline = async () => {
    try {
      setLoadingTimeline(true);
      setErrorTimeline(null);
      // Use v2 endpoint with last 24 hours
      const endTime = new Date();
      const startTime = new Date(endTime.getTime() - 24 * 60 * 60 * 1000);
      const data = await dashboardApi.getTimelineV2(
        startTime.toISOString(),
        endTime.toISOString(),
        15 // 15-minute buckets
      );
      setTimeline(data);
    } catch (err: any) {
      setErrorTimeline(err.response?.data?.error || 'Failed to load timeline');
      console.error('Timeline error:', err);
    } finally {
      setLoadingTimeline(false);
    }
  };

  // Helper function to fetch categories independently
  const fetchCategories = async () => {
    try {
      setLoadingCategories(true);
      setErrorCategories(null);
      const data = await dashboardApi.getTopCategories(10);
      setCategories(data);
    } catch (err: any) {
      setErrorCategories(err.response?.data?.error || 'Failed to load categories');
      console.error('Categories error:', err);
    } finally {
      setLoadingCategories(false);
    }
  };

  // Helper function to fetch recent logs independently
  const fetchRecentLogs = async () => {
    try {
      setLoadingRecentLogs(true);
      setErrorRecentLogs(null);
      // Use logs API to get recent entries with pagination
      const response = await logsApi.listLogEntries({
        page: 1,
        limit: 20, // Show 20 recent entries
      });
      setRecentLogEntries(response.entries);
    } catch (err: any) {
      setErrorRecentLogs(err.response?.data?.error || 'Failed to load recent logs');
      console.error('Recent logs error:', err);
    } finally {
      setLoadingRecentLogs(false);
    }
  };

  // Fetch all sections independently on mount
  useEffect(() => {
    if (isLoading) {
      return;
    }
    if (!isAuthenticated) {
      return;
    }

    // Fetch all sections independently - they won't block each other
    fetchStats();
    fetchTimeline();
    fetchCategories();
    fetchRecentLogs();
    
    setLastUpdated(new Date().toLocaleTimeString());
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthenticated, isLoading]);

  // Refresh all sections independently
  const refreshAll = async () => {
    setLastUpdated('Refreshing...');
    
    // Refresh all sections independently - they won't block each other
    fetchStats();
    fetchTimeline();
    fetchCategories();
    fetchRecentLogs();
    
    setLastUpdated(new Date().toLocaleTimeString());
  };

  const formatNumber = (num: number): string => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M';
    }
    if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num.toLocaleString();
  };

  const formatBytes = (bytes: number): string => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return (bytes / Math.pow(k, i)).toFixed(2) + ' ' + sizes[i];
  };

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background-dark">
        <div className="text-text-primary-dark">Loading dashboard...</div>
      </div>
    );
  }

  return (
    <div className="relative flex h-auto min-h-screen w-full flex-col dark overflow-x-hidden bg-background-light dark:bg-background-dark">
      <div className="layout-container flex h-full grow flex-col">
        {/* Header */}
        <header className="sticky top-0 z-50 flex items-center justify-between whitespace-nowrap border-b border-solid border-border-dark px-6 sm:px-10 py-3 bg-background-dark/80 backdrop-blur-sm">
          <div className="flex items-center gap-4 text-white">
            <div className="size-6 text-primary">
              <svg fill="none" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
                <g clipPath="url(#clip0_6_330)">
                  <path
                    clipRule="evenodd"
                    d="M24 0.757355L47.2426 24L24 47.2426L0.757355 24L24 0.757355ZM21 35.7574V12.2426L9.24264 24L21 35.7574Z"
                    fill="currentColor"
                    fillRule="evenodd"
                  ></path>
                </g>
                <defs>
                  <clipPath id="clip0_6_330">
                    <rect fill="white" height="48" width="48"></rect>
                  </clipPath>
                </defs>
              </svg>
            </div>
            <h2 className="text-white text-xl font-bold leading-tight tracking-[-0.015em]">Security Analytics</h2>
          </div>
          <div className="flex flex-1 justify-end gap-4 md:gap-8">
            <div className="hidden md:flex items-center gap-8">
              <Link href="/dashboard" className="text-white text-sm font-medium leading-normal px-3 py-2 rounded-lg bg-primary/20">
                Dashboard
              </Link>
              <Link href="/upload" className="text-gray-300 hover:text-white text-sm font-medium leading-normal">
                Upload
              </Link>
              <Link href="/logs" className="text-gray-300 hover:text-white text-sm font-medium leading-normal">
                Logs
              </Link>
              <Link href="/ai-copilot" className="text-gray-300 hover:text-white text-sm font-medium leading-normal">
                AI Assistant
              </Link>
            </div>
            <div className="bg-center bg-no-repeat aspect-square bg-cover rounded-full size-10 border-2 border-border-dark bg-primary/20"></div>
          </div>
        </header>

        <main className="px-4 sm:px-6 lg:px-10 py-8">
          <div className="flex flex-wrap items-center justify-between gap-4 pb-6">
            <p className="text-white text-4xl font-black leading-tight tracking-[-0.033em] min-w-72">Main Dashboard</p>
            <div className="flex items-center gap-4">
              <span className="text-gray-400 text-sm">Last updated: {lastUpdated}</span>
              <button
                onClick={refreshAll}
                className="flex items-center justify-center p-2 rounded-lg bg-card-dark border border-border-dark text-white hover:bg-border-dark"
                aria-label="Refresh dashboard"
              >
                <span className="material-symbols-outlined text-xl">refresh</span>
              </button>
            </div>
          </div>

          <div className="grid grid-cols-1 gap-6 lg:grid-cols-12">
            {/* Main Content Area */}
            <div className="lg:col-span-8 flex flex-col gap-6">
              {/* Stats Cards */}
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
                {loadingStats && !stats ? (
                  <div className="col-span-full flex items-center justify-center py-8 text-gray-400">
                    Loading stats...
                  </div>
                ) : errorStats && !stats ? (
                  <div className="col-span-full flex items-center justify-center py-8 text-danger">
                    {errorStats}
                  </div>
                ) : stats ? (
                  <>
                    <div className="flex min-w-[158px] flex-1 flex-col gap-2 rounded-xl p-4 border border-border-dark bg-card-dark">
                      <p className="text-gray-300 text-sm font-medium leading-normal">Total Requests</p>
                      <p className="text-white tracking-light text-2xl font-bold leading-tight">
                        {formatNumber(stats.total_requests)}
                      </p>
                      <p className={`${stats.trends.total_requests_pct >= 0 ? 'text-success' : 'text-danger'} text-sm font-medium leading-normal`}>
                        {stats.trends.total_requests_pct >= 0 ? '+' : ''}
                        {stats.trends.total_requests_pct.toFixed(1)}%
                      </p>
                    </div>
                    <div className="flex min-w-[158px] flex-1 flex-col gap-2 rounded-xl p-4 border border-border-dark bg-card-dark">
                      <p className="text-gray-300 text-sm font-medium leading-normal">Blocked Events</p>
                      <p className="text-white tracking-light text-2xl font-bold leading-tight">
                        {stats.blocked_events.toLocaleString()}
                      </p>
                      <p className={`${stats.trends.blocked_events_pct >= 0 ? 'text-danger' : 'text-success'} text-sm font-medium leading-normal`}>
                        {stats.trends.blocked_events_pct >= 0 ? '+' : ''}
                        {stats.trends.blocked_events_pct.toFixed(1)}%
                      </p>
                    </div>
                    <div className="flex min-w-[158px] flex-1 flex-col gap-2 rounded-xl p-4 border border-border-dark bg-card-dark">
                      <p className="text-gray-300 text-sm font-medium leading-normal">Malicious URLs</p>
                      <p className="text-white tracking-light text-2xl font-bold leading-tight">
                        {stats.malicious_urls.toLocaleString()}
                      </p>
                      <p className="text-success text-sm font-medium leading-normal">+12%</p>
                    </div>
                    <div className="flex min-w-[158px] flex-1 flex-col gap-2 rounded-xl p-4 border border-border-dark bg-card-dark">
                      <p className="text-gray-300 text-sm font-medium leading-normal">High-Risk Users</p>
                      <p className="text-white tracking-light text-2xl font-bold leading-tight">
                        {stats.high_risk_users}
                      </p>
                      <p className="text-success text-sm font-medium leading-normal">+3%</p>
                    </div>
                    <div className="flex min-w-[158px] flex-1 flex-col gap-2 rounded-xl p-4 border border-border-dark bg-card-dark">
                      <p className="text-gray-300 text-sm font-medium leading-normal">Data Transfer</p>
                      <p className="text-white tracking-light text-2xl font-bold leading-tight">
                        {formatBytes(stats.data_transfer_bytes)}
                      </p>
                      <p className="text-success text-sm font-medium leading-normal">+1.8%</p>
                    </div>
                  </>
                ) : null}
              </div>

              {/* Time Series Chart */}
              {loadingTimeline && !timeline ? (
                <div className="flex min-w-72 flex-1 flex-col gap-2 rounded-xl border border-border-dark p-6 bg-card-dark">
                  <div className="flex items-center justify-center py-8 text-gray-400">
                    Loading timeline...
                  </div>
                </div>
              ) : errorTimeline && !timeline ? (
                <div className="flex min-w-72 flex-1 flex-col gap-2 rounded-xl border border-border-dark p-6 bg-card-dark">
                  <div className="flex items-center justify-center py-8 text-danger">
                    {errorTimeline}
                  </div>
                </div>
              ) : timeline && stats ? (
                <div className="flex min-w-72 flex-1 flex-col gap-2 rounded-xl border border-border-dark p-6 bg-card-dark">
                  <p className="text-white text-base font-medium leading-normal">Traffic & Block Events (Last 24 Hours)</p>
                  <p className="text-white tracking-light text-[32px] font-bold leading-tight truncate">
                    {formatNumber(stats.total_requests)} Requests
                  </p>
                  <div className="flex gap-1 items-center">
                    <p className="text-gray-400 text-sm font-normal leading-normal">Last 24h</p>
                    <p className={`${stats.trends.total_requests_pct >= 0 ? 'text-success' : 'text-danger'} text-sm font-medium leading-normal`}>
                      {stats.trends.total_requests_pct >= 0 ? '+' : ''}
                      {stats.trends.total_requests_pct.toFixed(1)}%
                    </p>
                  </div>
                  <div className="flex min-h-[220px] flex-1 flex-col gap-8 py-4">
                    {timeline.buckets.length > 0 ? (
                      <div className="relative w-full h-full">
                        <svg
                          fill="none"
                          height="100%"
                          preserveAspectRatio="none"
                          viewBox={`0 0 ${Math.max(478, timeline.buckets.length * 20)} 150`}
                          width="100%"
                          xmlns="http://www.w3.org/2000/svg"
                        >
                          <defs>
                            {/* Gradient for total requests */}
                            <linearGradient gradientUnits="userSpaceOnUse" id="paint0_linear_total" x1="236" x2="236" y1="1" y2="149">
                              <stop stopColor="#137fec" stopOpacity="0.4"></stop>
                              <stop offset="1" stopColor="#137fec" stopOpacity="0"></stop>
                            </linearGradient>
                            {/* Gradient for blocked requests */}
                            <linearGradient gradientUnits="userSpaceOnUse" id="paint0_linear_blocked" x1="236" x2="236" y1="1" y2="149">
                              <stop stopColor="#ef4444" stopOpacity="0.4"></stop>
                              <stop offset="1" stopColor="#ef4444" stopOpacity="0"></stop>
                            </linearGradient>
                          </defs>
                          {/* Calculate max value for scaling */}
                          {(() => {
                            const maxTotal = Math.max(...timeline.buckets.map((b) => b.total || b.log_count || 0), 1);
                            const maxBlocked = Math.max(...timeline.buckets.map((b) => b.blocked || b.blocked_count || 0), 1);
                            const maxValue = Math.max(maxTotal, maxBlocked);
                            const width = Math.max(478, timeline.buckets.length * 20);
                            const stepX = timeline.buckets.length > 1 ? width / (timeline.buckets.length - 1) : width;
                            
                            // Total requests line (blue)
                            const totalPoints = timeline.buckets
                              .map((bucket, i) => {
                                const value = bucket.total || bucket.log_count || 0;
                                const y = 150 - (value / maxValue) * 120;
                                return `${i * stepX},${y}`;
                              })
                              .join(' ');
                            
                            // Blocked requests line (red)
                            const blockedPoints = timeline.buckets
                              .map((bucket, i) => {
                                const value = bucket.blocked || bucket.blocked_count || 0;
                                const y = 150 - (value / maxValue) * 120;
                                return `${i * stepX},${y}`;
                              })
                              .join(' ');
                            
                            return (
                              <>
                                {/* Total requests area */}
                                <polyline
                                  points={totalPoints}
                                  fill="url(#paint0_linear_total)"
                                  stroke="#137fec"
                                  strokeWidth="3"
                                  strokeLinecap="round"
                                  strokeLinejoin="round"
                                />
                                {/* Blocked requests line */}
                                <polyline
                                  points={blockedPoints}
                                  fill="url(#paint0_linear_blocked)"
                                  stroke="#ef4444"
                                  strokeWidth="2"
                                  strokeLinecap="round"
                                  strokeLinejoin="round"
                                  strokeDasharray="5,5"
                                />
                              </>
                            );
                          })()}
                        </svg>
                        {/* Legend */}
                        <div className="absolute top-0 right-0 flex gap-4 text-xs">
                          <div className="flex items-center gap-2">
                            <div className="w-3 h-0.5 bg-[#137fec]"></div>
                            <span className="text-gray-400">Total</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <div className="w-3 h-0.5 bg-[#ef4444] border-dashed border-t-2"></div>
                            <span className="text-gray-400">Blocked</span>
                          </div>
                        </div>
                      </div>
                    ) : (
                      <div className="flex items-center justify-center h-full text-text-secondary-dark">
                        No timeline data available
                      </div>
                    )}
                  </div>
                  <div className="flex justify-around -mt-4">
                    <p className="text-gray-400 text-xs font-bold tracking-wider">00:00</p>
                    <p className="text-gray-400 text-xs font-bold tracking-wider">04:00</p>
                    <p className="text-gray-400 text-xs font-bold tracking-wider">08:00</p>
                    <p className="text-gray-400 text-xs font-bold tracking-wider">12:00</p>
                    <p className="text-gray-400 text-xs font-bold tracking-wider">16:00</p>
                    <p className="text-gray-400 text-xs font-bold tracking-wider">20:00</p>
                    <p className="text-gray-400 text-xs font-bold tracking-wider">23:59</p>
                  </div>
                </div>
              ) : null}

              {/* Pie Charts */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {loadingCategories && !categories ? (
                  <div className="flex min-w-72 flex-1 flex-col gap-4 rounded-xl border border-border-dark p-6 bg-card-dark">
                    <div className="flex items-center justify-center py-8 text-gray-400">
                      Loading categories...
                    </div>
                  </div>
                ) : errorCategories && !categories ? (
                  <div className="flex min-w-72 flex-1 flex-col gap-4 rounded-xl border border-border-dark p-6 bg-card-dark">
                    <div className="flex items-center justify-center py-8 text-danger">
                      {errorCategories}
                    </div>
                  </div>
                ) : categories ? (
                  <div className="flex min-w-72 flex-1 flex-col gap-4 rounded-xl border border-border-dark p-6 bg-card-dark">
                    <p className="text-white text-base font-medium leading-normal">Top URL Categories</p>
                    <div className="flex flex-1 flex-col gap-2 min-h-[200px]">
                      {categories.categories && categories.categories.length > 0 ? (
                        categories.categories.slice(0, 5).map((cat, index) => (
                          <div key={index} className="flex justify-between items-center">
                            <span className="text-text-secondary-dark text-sm">{cat.name}</span>
                            <div className="flex items-center gap-2">
                              <span className="text-text-primary-dark text-sm font-medium">{cat.count.toLocaleString()}</span>
                              <span className="text-text-secondary-dark text-xs">({cat.percentage.toFixed(1)}%)</span>
                            </div>
                          </div>
                        ))
                      ) : (
                        <div className="flex items-center justify-center h-full text-text-secondary-dark">
                          No category data available
                        </div>
                      )}
                    </div>
                  </div>
                ) : null}
                {stats ? (
                  <div className="flex min-w-72 flex-1 flex-col gap-4 rounded-xl border border-border-dark p-6 bg-card-dark">
                    <p className="text-white text-base font-medium leading-normal">Action Breakdown</p>
                    <div className="flex flex-1 flex-col gap-2 min-h-[200px]">
                      <div className="flex justify-between items-center">
                        <span className="text-text-secondary-dark text-sm">Blocked</span>
                        <div className="flex items-center gap-2">
                          <span className="text-text-primary-dark text-sm font-medium">
                            {stats.blocked_events.toLocaleString()}
                          </span>
                          <span className="text-text-secondary-dark text-xs">
                            ({stats.total_requests > 0 ? ((stats.blocked_events / stats.total_requests) * 100).toFixed(1) : 0}%)
                          </span>
                        </div>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-text-secondary-dark text-sm">Allowed</span>
                        <div className="flex items-center gap-2">
                          <span className="text-text-primary-dark text-sm font-medium">
                            {(stats.total_requests - stats.blocked_events).toLocaleString()}
                          </span>
                          <span className="text-text-secondary-dark text-xs">
                            ({stats.total_requests > 0 ? (((stats.total_requests - stats.blocked_events) / stats.total_requests) * 100).toFixed(1) : 0}%)
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                ) : null}
              </div>

              {/* Recent Log Entries Table */}
              {loadingRecentLogs && recentLogEntries.length === 0 ? (
                <div>
                  <h2 className="text-white text-xl font-bold leading-tight tracking-[-0.015em] px-1 pb-4 pt-2">
                    Recent Log Entries
                  </h2>
                  <div className="rounded-xl border border-border-dark bg-card-dark p-8">
                    <div className="flex items-center justify-center text-gray-400">
                      Loading recent logs...
                    </div>
                  </div>
                </div>
              ) : errorRecentLogs && recentLogEntries.length === 0 ? (
                <div>
                  <h2 className="text-white text-xl font-bold leading-tight tracking-[-0.015em] px-1 pb-4 pt-2">
                    Recent Log Entries
                  </h2>
                  <div className="rounded-xl border border-border-dark bg-card-dark p-8">
                    <div className="flex items-center justify-center text-danger">
                      {errorRecentLogs}
                    </div>
                  </div>
                </div>
              ) : recentLogEntries.length > 0 ? (
                <div>
                  <div className="flex items-center justify-between px-1 pb-4 pt-2">
                    <h2 className="text-white text-xl font-bold leading-tight tracking-[-0.015em]">
                      Recent Log Entries
                    </h2>
                    <Link
                      href="/logs"
                      className="text-primary text-sm font-medium hover:underline"
                    >
                      View All →
                    </Link>
                  </div>
                  <div className="rounded-xl border border-border-dark bg-card-dark overflow-x-auto">
                    <table className="w-full text-sm text-left text-gray-400">
                      <thead className="text-xs text-gray-300 uppercase bg-card-dark/50">
                        <tr>
                          <th className="px-6 py-3" scope="col">
                            Timestamp
                          </th>
                          <th className="px-6 py-3" scope="col">
                            User
                          </th>
                          <th className="px-6 py-3" scope="col">
                            Source IP
                          </th>
                          <th className="px-6 py-3" scope="col">
                            URL
                          </th>
                          <th className="px-6 py-3" scope="col">
                            Category
                          </th>
                          <th className="px-6 py-3 text-right" scope="col">
                            Action
                          </th>
                        </tr>
                      </thead>
                      <tbody>
                        {recentLogEntries.map((entry) => (
                          <tr 
                            key={entry.id} 
                            className="border-t border-border-dark hover:bg-border-dark/30 cursor-pointer"
                            onClick={async () => {
                              try {
                                const fullEntry = await logsApi.getLogEntry(entry.id);
                                setSelectedEntry(fullEntry);
                              } catch (err: any) {
                                console.error('Error fetching entry details:', err);
                                setSelectedEntry(entry);
                              }
                            }}
                          >
                            <td className="px-6 py-4 text-white whitespace-nowrap">
                              {new Date(entry.timestamp).toLocaleString()}
                            </td>
                            <td className="px-6 py-4 text-white">{entry.department || entry.client_ip || 'Unknown'}</td>
                            <td className="px-6 py-4 text-white">{entry.client_ip || 'N/A'}</td>
                            <td className="px-6 py-4 text-white truncate max-w-xs" title={entry.url}>
                              {entry.url || entry.domain || 'N/A'}
                            </td>
                            <td className="px-6 py-4 text-white">{entry.url_cat || 'Unknown'}</td>
                            <td className="px-6 py-4 text-right">
                              <span
                                className={`inline-flex items-center text-xs font-medium px-2.5 py-0.5 rounded-full ${
                                  entry.action === 'Blocked'
                                    ? 'bg-danger/20 text-danger'
                                    : entry.action === 'Allowed' || entry.action === 'ALLOW'
                                    ? 'bg-success/20 text-success'
                                    : 'bg-warning/20 text-warning'
                                }`}
                              >
                                {entry.action?.toUpperCase() || 'UNKNOWN'}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              ) : null}
            </div>

            {/* AI Summary Side Panel */}
            <aside className="lg:col-span-4 lg:sticky top-24 h-fit">
              <div className="flex flex-col gap-4 rounded-xl border border-border-dark p-6 bg-card-dark">
                <div className="flex items-center gap-3">
                  <span className="material-symbols-outlined text-primary text-2xl">auto_awesome</span>
                  <h3 className="text-white text-lg font-bold">AI Daily Security Summary</h3>
                </div>
                <p className="text-sm text-gray-400">Generated: 2023-10-27 14:30:00 UTC</p>
                <ul className="space-y-4 text-gray-300">
                  <li className="flex items-start gap-3">
                    <span className="material-symbols-outlined text-warning text-lg mt-1">warning</span>
                    <span>
                      A significant spike in malware blocks (+35%) was detected at 14:15 PM, primarily targeting users in
                      the Engineering department.
                    </span>
                  </li>
                  <li className="flex items-start gap-3">
                    <span className="material-symbols-outlined text-gray-400 text-lg mt-1">person_alert</span>
                    <span>
                      User <strong className="text-white">j.doe</strong> shows anomalous outbound traffic patterns to
                      suspicious domains, warranting further investigation.
                    </span>
                  </li>
                  <li className="flex items-start gap-3">
                    <span className="material-symbols-outlined text-gray-400 text-lg mt-1">trending_up</span>
                    <span>
                      Overall data exfiltration attempts are trending down by 15% compared to the previous 24-hour period.
                    </span>
                  </li>
                  <li className="flex items-start gap-3">
                    <span className="material-symbols-outlined text-danger text-lg mt-1">block</span>
                    <span>
                      Increased blocking activity observed for the 'Phishing' category, suggesting an active campaign may be
                      underway.
                    </span>
                  </li>
                </ul>
                <button className="w-full text-center py-2 px-4 rounded-lg bg-primary/20 text-primary font-medium text-sm hover:bg-primary/30">
                  View Full Report
                </button>
              </div>
            </aside>
          </div>
        </main>
      </div>

      {/* Log Entry Detail Modal */}
      {selectedEntry && <LogEntryDetailModal entry={selectedEntry} onClose={() => setSelectedEntry(null)} />}
    </div>
  );
}
