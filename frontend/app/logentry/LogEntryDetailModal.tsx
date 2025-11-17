'use client';

import React from 'react';
import { LogEntry } from '@/lib/api/logs';

interface LogEntryDetailModalProps {
  entry: LogEntry | null;
  onClose: () => void;
}

export default function LogEntryDetailModal({ entry, onClose }: LogEntryDetailModalProps) {
  if (!entry) {
    return null;
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const formatBytes = (bytes: number | null) => {
    if (bytes === null || bytes === 0) return 'N/A';
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return `${(bytes / Math.pow(1024, i)).toFixed(2)} ${sizes[i]}`;
  };

  const getActionBadgeClass = (action: string) => {
    if (action === 'Blocked') {
      return 'bg-red-100 dark:bg-red-500/20 text-red-800 dark:text-red-400';
    }
    return 'bg-green-100 dark:bg-green-500/20 text-green-800 dark:text-green-400';
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
    >
      <div
        className="relative w-full max-w-4xl max-h-[90vh] overflow-y-auto rounded-lg border border-gray-200/10 dark:border-[#324d67] bg-gray-50 dark:bg-[#111a22] shadow-xl"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="sticky top-0 flex items-center justify-between border-b border-gray-200/10 dark:border-[#324d67] bg-gray-100/50 dark:bg-[#192633] px-6 py-4">
          <h2 id="modal-title" className="text-xl font-bold text-gray-900 dark:text-white">
            Log Entry Details
          </h2>
          <button
            onClick={onClose}
            className="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 transition-colors"
            aria-label="Close"
          >
            <span className="material-symbols-outlined">close</span>
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Anomaly Alert */}
          {entry.is_anomalous && entry.anomaly_reason && (
            <div className="rounded-lg border border-amber-500/50 bg-amber-500/10 p-4">
              <div className="flex items-start gap-3">
                <span className="material-symbols-outlined text-amber-500">warning</span>
                <div className="flex-1">
                  <h3 className="text-sm font-semibold text-amber-800 dark:text-amber-400 mb-1">
                    Anomaly Explanation
                  </h3>
                  <p className="text-sm text-amber-700 dark:text-amber-300">{entry.anomaly_reason}</p>
                  {entry.anomaly_confidence && (
                    <p className="text-xs text-amber-600 dark:text-amber-400 mt-2">
                      Confidence: {(entry.anomaly_confidence * 100).toFixed(0)}%
                    </p>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Basic Information */}
          <div>
            <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">Basic Information</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-xs font-medium text-gray-500 dark:text-gray-400">Timestamp</label>
                <p className="text-sm text-gray-900 dark:text-white mt-1">{formatDate(entry.timestamp)}</p>
              </div>
              <div>
                <label className="text-xs font-medium text-gray-500 dark:text-gray-400">Action</label>
                <div className="mt-1">
                  <span className={`inline-flex items-center rounded-md px-2.5 py-0.5 text-sm font-medium ${getActionBadgeClass(entry.action)}`}>
                    {entry.action}
                  </span>
                </div>
              </div>
              <div>
                <label className="text-xs font-medium text-gray-500 dark:text-gray-400">URL</label>
                <p className="text-sm text-gray-900 dark:text-white mt-1 break-all">{entry.url || 'N/A'}</p>
              </div>
              <div>
                <label className="text-xs font-medium text-gray-500 dark:text-gray-400">Domain</label>
                <p className="text-sm text-gray-900 dark:text-white mt-1">{entry.domain || 'N/A'}</p>
              </div>
              <div>
                <label className="text-xs font-medium text-gray-500 dark:text-gray-400">Protocol</label>
                <p className="text-sm text-gray-900 dark:text-white mt-1">{entry.protocol || 'N/A'}</p>
              </div>
              <div>
                <label className="text-xs font-medium text-gray-500 dark:text-gray-400">HTTP Method</label>
                <p className="text-sm text-gray-900 dark:text-white mt-1">{entry.http_method || 'N/A'}</p>
              </div>
              <div>
                <label className="text-xs font-medium text-gray-500 dark:text-gray-400">HTTP Status</label>
                <p className="text-sm text-gray-900 dark:text-white mt-1">{entry.http_status || 'N/A'}</p>
              </div>
              <div>
                <label className="text-xs font-medium text-gray-500 dark:text-gray-400">Threat Category</label>
                <p className="text-sm text-gray-900 dark:text-white mt-1">{entry.threat_category || 'None'}</p>
              </div>
            </div>
          </div>

          {/* Network Information */}
          <div>
            <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">Network Information</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-xs font-medium text-gray-500 dark:text-gray-400">Client IP</label>
                <p className="text-sm text-gray-900 dark:text-white mt-1">{entry.client_ip || 'N/A'}</p>
              </div>
              <div>
                <label className="text-xs font-medium text-gray-500 dark:text-gray-400">Server IP</label>
                <p className="text-sm text-gray-900 dark:text-white mt-1">{entry.server_ip || 'N/A'}</p>
              </div>
              <div>
                <label className="text-xs font-medium text-gray-500 dark:text-gray-400">Location</label>
                <p className="text-sm text-gray-900 dark:text-white mt-1">{entry.location || 'N/A'}</p>
              </div>
              <div>
                <label className="text-xs font-medium text-gray-500 dark:text-gray-400">Location 2</label>
                <p className="text-sm text-gray-900 dark:text-white mt-1">{entry.location2 || 'N/A'}</p>
              </div>
            </div>
          </div>

          {/* User Information */}
          <div>
            <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">User Information</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-xs font-medium text-gray-500 dark:text-gray-400">Department</label>
                <p className="text-sm text-gray-900 dark:text-white mt-1">{entry.department || 'N/A'}</p>
              </div>
              <div>
                <label className="text-xs font-medium text-gray-500 dark:text-gray-400">User Agent</label>
                <p className="text-sm text-gray-900 dark:text-white mt-1 break-all">{entry.user_agent || 'N/A'}</p>
              </div>
            </div>
          </div>

          {/* URL Classification */}
          <div>
            <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">URL Classification</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-xs font-medium text-gray-500 dark:text-gray-400">Category</label>
                <p className="text-sm text-gray-900 dark:text-white mt-1">{entry.url_cat || 'N/A'}</p>
              </div>
              <div>
                <label className="text-xs font-medium text-gray-500 dark:text-gray-400">Super Category</label>
                <p className="text-sm text-gray-900 dark:text-white mt-1">{entry.url_supercat || 'N/A'}</p>
              </div>
              <div>
                <label className="text-xs font-medium text-gray-500 dark:text-gray-400">Class</label>
                <p className="text-sm text-gray-900 dark:text-white mt-1">{entry.url_class || 'N/A'}</p>
              </div>
            </div>
          </div>

          {/* Data Transfer */}
          <div>
            <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">Data Transfer</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-xs font-medium text-gray-500 dark:text-gray-400">Request Size</label>
                <p className="text-sm text-gray-900 dark:text-white mt-1">{formatBytes(entry.req_size)}</p>
              </div>
              <div>
                <label className="text-xs font-medium text-gray-500 dark:text-gray-400">Response Size</label>
                <p className="text-sm text-gray-900 dark:text-white mt-1">{formatBytes(entry.resp_size)}</p>
              </div>
            </div>
          </div>

          {/* Application Information */}
          <div>
            <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">Application Information</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-xs font-medium text-gray-500 dark:text-gray-400">App Name</label>
                <p className="text-sm text-gray-900 dark:text-white mt-1">{entry.app_name || 'N/A'}</p>
              </div>
              <div>
                <label className="text-xs font-medium text-gray-500 dark:text-gray-400">App Class</label>
                <p className="text-sm text-gray-900 dark:text-white mt-1">{entry.app_class || 'N/A'}</p>
              </div>
            </div>
          </div>

          {/* Security & Policy */}
          {(entry.fw_filter || entry.fw_rule || entry.policy_type || entry.reason) && (
            <div>
              <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">Security & Policy</h3>
              <div className="grid grid-cols-2 gap-4">
                {entry.fw_filter && (
                  <div>
                    <label className="text-xs font-medium text-gray-500 dark:text-gray-400">Firewall Filter</label>
                    <p className="text-sm text-gray-900 dark:text-white mt-1">{entry.fw_filter}</p>
                  </div>
                )}
                {entry.fw_rule && (
                  <div>
                    <label className="text-xs font-medium text-gray-500 dark:text-gray-400">Firewall Rule</label>
                    <p className="text-sm text-gray-900 dark:text-white mt-1">{entry.fw_rule}</p>
                  </div>
                )}
                {entry.policy_type && (
                  <div>
                    <label className="text-xs font-medium text-gray-500 dark:text-gray-400">Policy Type</label>
                    <p className="text-sm text-gray-900 dark:text-white mt-1">{entry.policy_type}</p>
                  </div>
                )}
                {entry.reason && (
                  <div>
                    <label className="text-xs font-medium text-gray-500 dark:text-gray-400">Reason</label>
                    <p className="text-sm text-gray-900 dark:text-white mt-1">{entry.reason}</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* DLP Information */}
          {entry.dlp_hits !== null && entry.dlp_hits > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">DLP Information</h3>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-xs font-medium text-gray-500 dark:text-gray-400">DLP Hits</label>
                  <p className="text-sm text-gray-900 dark:text-white mt-1">{entry.dlp_hits}</p>
                </div>
                {entry.dlp_dict && (
                  <div>
                    <label className="text-xs font-medium text-gray-500 dark:text-gray-400">DLP Dictionary</label>
                    <p className="text-sm text-gray-900 dark:text-white mt-1">{entry.dlp_dict}</p>
                  </div>
                )}
                {entry.dlp_eng && (
                  <div>
                    <label className="text-xs font-medium text-gray-500 dark:text-gray-400">DLP Engine</label>
                    <p className="text-sm text-gray-900 dark:text-white mt-1">{entry.dlp_eng}</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* File Information */}
          {(entry.file_class || entry.file_type) && (
            <div>
              <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">File Information</h3>
              <div className="grid grid-cols-2 gap-4">
                {entry.file_class && (
                  <div>
                    <label className="text-xs font-medium text-gray-500 dark:text-gray-400">File Class</label>
                    <p className="text-sm text-gray-900 dark:text-white mt-1">{entry.file_class}</p>
                  </div>
                )}
                {entry.file_type && (
                  <div>
                    <label className="text-xs font-medium text-gray-500 dark:text-gray-400">File Type</label>
                    <p className="text-sm text-gray-900 dark:text-white mt-1">{entry.file_type}</p>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="sticky bottom-0 flex justify-end gap-3 border-t border-gray-200/10 dark:border-[#324d67] bg-gray-100/50 dark:bg-[#192633] px-6 py-4">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg bg-gray-200 dark:bg-[#233648] text-gray-800 dark:text-white hover:bg-gray-300 dark:hover:bg-[#324d67] transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

