'use client';

import { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { logsApi, LogEntry, ListLogEntriesParams } from '@/lib/api/logs';
import LogEntryDetailModal from '@/lib/components/LogEntryDetailModal';

export default function LogExplorerPage() {
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedAction, setSelectedAction] = useState<string>('All');
  const [selectedCategory, setSelectedCategory] = useState<string>('All');
  const [timeRange, setTimeRange] = useState<string>('Last 24h');
  const [entries, setEntries] = useState<LogEntry[]>([]);
  const [totalEntries, setTotalEntries] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedEntry, setSelectedEntry] = useState<LogEntry | null>(null);
  const [limit] = useState(50);

  const fetchEntries = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const params: ListLogEntriesParams = {
        page: currentPage,
        limit,
      };

      // Apply action filter
      if (selectedAction !== 'All') {
        params.action = selectedAction;
      }

      // Apply category filter
      if (selectedCategory !== 'All') {
        params.category = selectedCategory;
      }

      // Apply time range filter
      if (timeRange !== 'All') {
        const now = new Date();
        let startTime: Date;
        if (timeRange === 'Last 24h') {
          startTime = new Date(now.getTime() - 24 * 60 * 60 * 1000);
        } else if (timeRange === 'Last 7d') {
          startTime = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
        } else if (timeRange === 'Last 30d') {
          startTime = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
        } else {
          startTime = new Date(0); // All time
        }
        params.start_time = startTime.toISOString();
        params.end_time = now.toISOString();
      }

      const response = await logsApi.listLogEntries(params);
      setEntries(response.entries);
      setTotalEntries(response.total);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to load log entries');
      console.error('Error fetching log entries:', err);
    } finally {
      setIsLoading(false);
    }
  }, [currentPage, selectedAction, selectedCategory, timeRange, limit]);

  useEffect(() => {
    fetchEntries();
  }, [fetchEntries]);


  const handleEntryClick = async (entry: LogEntry) => {
    try {
      // Fetch full entry details
      const fullEntry = await logsApi.getLogEntry(entry.id);
      setSelectedEntry(fullEntry);
    } catch (err: any) {
      console.error('Error fetching entry details:', err);
      // Fallback to using the entry we already have
      setSelectedEntry(entry);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const getActionBadgeClass = (action: string) => {
    if (action === 'Blocked') {
      return 'bg-red-100 dark:bg-red-500/20 text-red-800 dark:text-red-400';
    }
    return 'bg-green-100 dark:bg-green-500/20 text-green-800 dark:text-green-400';
  };

  const getTotalPages = () => {
    return Math.ceil(totalEntries / limit);
  };

  const renderPaginationButtons = () => {
    const totalPages = getTotalPages();
    const buttons = [];
    const maxVisiblePages = 5;

    if (totalPages <= maxVisiblePages) {
      // Show all pages if total pages is small
      for (let i = 1; i <= totalPages; i++) {
        buttons.push(
          <button
            key={i}
            className={`flex h-8 w-8 items-center justify-center rounded-lg border ${
              currentPage === i
                ? 'border-primary bg-primary/20 text-primary dark:border-primary dark:bg-[#233648]'
                : 'border-gray-200/10 dark:border-[#324d67] transition-colors hover:bg-gray-100 dark:hover:bg-white/10'
            }`}
            onClick={() => setCurrentPage(i)}
          >
            {i}
          </button>
        );
      }
    } else {
      // Show first page
      buttons.push(
        <button
          key={1}
          className={`flex h-8 w-8 items-center justify-center rounded-lg border ${
            currentPage === 1
              ? 'border-primary bg-primary/20 text-primary dark:border-primary dark:bg-[#233648]'
              : 'border-gray-200/10 dark:border-[#324d67] transition-colors hover:bg-gray-100 dark:hover:bg-white/10'
          }`}
          onClick={() => setCurrentPage(1)}
        >
          1
        </button>
      );

      // Show ellipsis if current page is far from start
      if (currentPage > 3) {
        buttons.push(<span key="ellipsis-start" className="text-gray-500">...</span>);
      }

      // Show pages around current page
      const start = Math.max(2, currentPage - 1);
      const end = Math.min(totalPages - 1, currentPage + 1);

      for (let i = start; i <= end; i++) {
        if (i !== 1 && i !== totalPages) {
          buttons.push(
            <button
              key={i}
              className={`flex h-8 w-8 items-center justify-center rounded-lg border ${
                currentPage === i
                  ? 'border-primary bg-primary/20 text-primary dark:border-primary dark:bg-[#233648]'
                  : 'border-gray-200/10 dark:border-[#324d67] transition-colors hover:bg-gray-100 dark:hover:bg-white/10'
              }`}
              onClick={() => setCurrentPage(i)}
            >
              {i}
            </button>
          );
        }
      }

      // Show ellipsis if current page is far from end
      if (currentPage < totalPages - 2) {
        buttons.push(<span key="ellipsis-end" className="text-gray-500">...</span>);
      }

      // Show last page
      buttons.push(
        <button
          key={totalPages}
          className={`flex h-8 w-8 items-center justify-center rounded-lg border ${
            currentPage === totalPages
              ? 'border-primary bg-primary/20 text-primary dark:border-primary dark:bg-[#233648]'
              : 'border-gray-200/10 dark:border-[#324d67] transition-colors hover:bg-gray-100 dark:hover:bg-white/10'
          }`}
          onClick={() => setCurrentPage(totalPages)}
        >
          {totalPages}
        </button>
      );
    }

    return buttons;
  };

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
              <Link href="/dashboard" className="text-gray-300 hover:text-white text-sm font-medium leading-normal">
                Dashboard
              </Link>
              <Link href="/upload" className="text-gray-300 hover:text-white text-sm font-medium leading-normal">
                Upload
              </Link>
              <Link href="/logentry" className="text-white text-sm font-medium leading-normal px-3 py-2 rounded-lg bg-primary/20">
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
          {/* PageHeading */}
          <div className="mb-6">
            <h1 className="text-gray-900 dark:text-white text-4xl font-black leading-tight tracking-[-0.033em]">Log Explorer</h1>
            <p className="text-gray-500 dark:text-[#92adc9] text-base font-normal leading-normal mt-2">
              Ingest and analyze Zscaler Web Proxy Logs for threats and anomalies.
            </p>
          </div>

          {/* Filters */}
          <div className="space-y-4 rounded-lg border border-gray-200/10 bg-[#111a22] p-4">
            {/* Filters */}
            <div className="flex gap-3 flex-wrap">
              <label className="flex flex-col">
                <select
                  value={selectedAction}
                  onChange={(e) => {
                    setSelectedAction(e.target.value);
                    setCurrentPage(1);
                  }}
                  className="flex h-8 shrink-0 items-center justify-center gap-x-2 rounded-lg bg-gray-100 dark:bg-[#233648] pl-4 pr-8 text-gray-800 dark:text-white transition-colors hover:bg-gray-200 dark:hover:bg-[#324d67] text-sm font-medium leading-normal appearance-none cursor-pointer"
                  style={{
                    backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='%23ffffff' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E")`,
                    backgroundRepeat: 'no-repeat',
                    backgroundPosition: 'right 0.5rem center',
                    backgroundSize: '1rem'
                  }}
                >
                  <option value="All">Action: All</option>
                  <option value="Blocked">Action: Blocked</option>
                  <option value="Allowed">Action: Allowed</option>
                </select>
              </label>
              <label className="flex flex-col">
                <select
                  value={selectedCategory}
                  onChange={(e) => {
                    setSelectedCategory(e.target.value);
                    setCurrentPage(1);
                  }}
                  className="flex h-8 shrink-0 items-center justify-center gap-x-2 rounded-lg bg-gray-100 dark:bg-[#233648] pl-4 pr-8 text-gray-800 dark:text-white transition-colors hover:bg-gray-200 dark:hover:bg-[#324d67] text-sm font-medium leading-normal appearance-none cursor-pointer"
                  style={{
                    backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='%23ffffff' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E")`,
                    backgroundRepeat: 'no-repeat',
                    backgroundPosition: 'right 0.5rem center',
                    backgroundSize: '1rem'
                  }}
                >
                  <option value="All">URL Category: All</option>
                  <option value="Malware">URL Category: Malware</option>
                  <option value="Phishing">URL Category: Phishing</option>
                  <option value="Adult">URL Category: Adult</option>
                  <option value="Gambling">URL Category: Gambling</option>
                  <option value="Social Networking">URL Category: Social Networking</option>
                  <option value="Streaming Media">URL Category: Streaming Media</option>
                  <option value="Business">URL Category: Business</option>
                  <option value="Technology">URL Category: Technology</option>
                  <option value="Shopping">URL Category: Shopping</option>
                  <option value="News">URL Category: News</option>
                </select>
              </label>
              <label className="flex flex-col">
                <select
                  value={timeRange}
                  onChange={(e) => {
                    setTimeRange(e.target.value);
                    setCurrentPage(1);
                  }}
                  className="flex h-8 shrink-0 items-center justify-center gap-x-2 rounded-lg bg-gray-100 dark:bg-[#233648] pl-4 pr-8 text-gray-800 dark:text-white transition-colors hover:bg-gray-200 dark:hover:bg-[#324d67] text-sm font-medium leading-normal appearance-none cursor-pointer"
                  style={{
                    backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='%23ffffff' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E")`,
                    backgroundRepeat: 'no-repeat',
                    backgroundPosition: 'right 0.5rem center',
                    backgroundSize: '1rem'
                  }}
                >
                  <option value="All">Time Range: All</option>
                  <option value="Last 24h">Time Range: Last 24h</option>
                  <option value="Last 7d">Time Range: Last 7d</option>
                  <option value="Last 30d">Time Range: Last 30d</option>
                </select>
              </label>
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="mt-4 rounded-lg border border-red-500/50 bg-red-500/10 p-4">
              <p className="text-sm text-red-700 dark:text-red-400">{error}</p>
            </div>
          )}

          {/* Table */}
          <div className="mt-6">
            {isLoading ? (
              <div className="flex items-center justify-center py-12">
                <div className="text-gray-500 dark:text-gray-400">Loading log entries...</div>
              </div>
            ) : entries.length === 0 ? (
              <div className="flex items-center justify-center py-12">
                <div className="text-gray-500 dark:text-gray-400">No log entries found</div>
              </div>
            ) : (
              <div className="flex overflow-hidden rounded-lg border border-gray-200/10 dark:border-[#324d67] bg-gray-50 dark:bg-[#111a22]">
                <table className="w-full">
                  <thead className="bg-gray-100/50 dark:bg-[#192633]">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-white w-[15%]">
                        Timestamp
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-white w-[15%]">
                        User
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-white w-[10%]">
                        Action
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-white w-[25%]">
                        URL
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-white w-[15%]">
                        Category
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-white w-[10%]">
                        Anomaly
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-white w-[10%]"></th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200/10 dark:divide-[#324d67]">
                    {entries.map((entry) => (
                      <tr
                        key={entry.id}
                        onClick={() => handleEntryClick(entry)}
                        className={`transition-colors hover:bg-gray-100/50 dark:hover:bg-white/5 cursor-pointer ${
                          entry.is_anomalous ? 'bg-amber-500/10' : ''
                        }`}
                      >
                        <td className="h-[72px] px-4 py-2 text-gray-600 dark:text-[#92adc9] text-sm font-normal leading-normal whitespace-nowrap">
                          {formatDate(entry.timestamp)}
                        </td>
                        <td className="h-[72px] px-4 py-2 text-gray-600 dark:text-[#92adc9] text-sm font-normal leading-normal whitespace-nowrap">
                          {entry.department || entry.client_ip || 'N/A'}
                        </td>
                        <td className="h-[72px] px-4 py-2 text-sm font-normal leading-normal">
                          <span className={`inline-flex items-center rounded-md px-2.5 py-0.5 text-sm font-medium ${getActionBadgeClass(entry.action)}`}>
                            {entry.action}
                          </span>
                        </td>
                        <td className="h-[72px] px-4 py-2 text-gray-600 dark:text-[#92adc9] text-sm font-normal leading-normal truncate max-w-xs" title={entry.url}>
                          {entry.url}
                        </td>
                        <td className="h-[72px] px-4 py-2 text-gray-600 dark:text-[#92adc9] text-sm font-normal leading-normal whitespace-nowrap">
                          {entry.url_cat || 'N/A'}
                        </td>
                        <td className="h-[72px] px-4 py-2 text-sm font-normal leading-normal">
                          {entry.is_anomalous && entry.anomaly_reason ? (
                            <div className="flex items-center gap-2" title={entry.anomaly_reason}>
                              <span className="material-symbols-outlined text-amber-500 text-sm">warning</span>
                              <span className="text-xs text-amber-600 dark:text-amber-400 truncate max-w-[150px]" title={entry.anomaly_reason}>
                                {entry.anomaly_reason.length > 30 ? `${entry.anomaly_reason.substring(0, 30)}...` : entry.anomaly_reason}
                              </span>
                            </div>
                          ) : (
                            <span className="text-gray-400 dark:text-gray-500 text-xs">—</span>
                          )}
                        </td>
                        <td className="h-[72px] px-4 py-2 text-gray-500 dark:text-primary text-sm font-bold leading-normal tracking-[0.015em]">
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              handleEntryClick(entry);
                            }}
                            className="text-primary hover:underline"
                          >
                            View
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* Pagination */}
          {!isLoading && entries.length > 0 && (
            <div className="mt-6 flex items-center justify-between">
              <div className="text-sm text-gray-500 dark:text-gray-400">
                Showing <span className="font-medium">{(currentPage - 1) * limit + 1}</span> to{' '}
                <span className="font-medium">{Math.min(currentPage * limit, totalEntries)}</span> of{' '}
                <span className="font-medium">{totalEntries}</span> results
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                  disabled={currentPage === 1}
                  className="flex h-8 w-8 items-center justify-center rounded-lg border border-gray-200/10 dark:border-[#324d67] transition-colors hover:bg-gray-100 dark:hover:bg-white/10 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <span className="material-symbols-outlined text-base">chevron_left</span>
                </button>
                {renderPaginationButtons()}
                <button
                  onClick={() => setCurrentPage(Math.min(getTotalPages(), currentPage + 1))}
                  disabled={currentPage >= getTotalPages()}
                  className="flex h-8 w-8 items-center justify-center rounded-lg border border-gray-200/10 dark:border-[#324d67] transition-colors hover:bg-gray-100 dark:hover:bg-white/10 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <span className="material-symbols-outlined text-base">chevron_right</span>
                </button>
              </div>
            </div>
          )}
        </main>
      </div>

      {/* Log Entry Detail Modal */}
      {selectedEntry && <LogEntryDetailModal entry={selectedEntry} onClose={() => setSelectedEntry(null)} />}
    </div>
  );
}
