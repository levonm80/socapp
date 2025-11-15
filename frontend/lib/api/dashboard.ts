import { apiClient } from './client';

export interface DashboardStats {
  total_requests: number;
  blocked_events: number;
  malicious_urls: number;
  high_risk_users: number;
  data_transfer_bytes: number;
  trends: {
    total_requests_pct: number;
    blocked_events_pct: number;
  };
}

export interface TimelineBucket {
  time: string;
  bucket_time?: string;  // v2 format
  total: number;
  log_count?: number;  // v2 format
  blocked: number;
  blocked_count?: number;  // v2 format
  // Extensible for future additions
  [key: string]: any;
}

export interface TimelineData {
  buckets: TimelineBucket[];
}

export interface Category {
  name: string;
  count: number;
  percentage: number;
}

export interface TopCategories {
  categories: Category[];
}

export interface RecentLogEntry {
  id: string;
  timestamp: string;
  user: string;
  domain: string;
  url: string;
  action: string;
  url_cat: string;
  client_ip: string;
  http_status: number;
  is_anomalous: boolean;
}

export interface RecentLogs {
  entries: RecentLogEntry[];
}

export interface LogSummary {
  summary: string;
  generated_at: string;
  key_findings: string[];
  recommendations: string[];
}

export const dashboardApi = {
  getStats: async (logFileId?: string): Promise<DashboardStats> => {
    const params = logFileId ? { log_file_id: logFileId } : {};
    const response = await apiClient.get('/dashboard/stats', { params });
    return response.data;
  },

  getTimeline: async (hours: number = 24, logFileId?: string): Promise<TimelineData> => {
    const params: any = { hours, bucket_minutes: 15 };
    if (logFileId) params.log_file_id = logFileId;
    const response = await apiClient.get('/dashboard/timeline', { params });
    return response.data;
  },

  getTimelineV2: async (
    startTime?: string,
    endTime?: string,
    bucketMinutes: number = 15,
    logFileId?: string
  ): Promise<TimelineData> => {
    const params: any = { bucket_minutes: bucketMinutes };
    if (startTime) params.start_time = startTime;
    if (endTime) params.end_time = endTime;
    if (logFileId) params.log_file_id = logFileId;
    const response = await apiClient.get('/dashboard/timeline/v2', { params });
    return response.data;
  },

  getTopCategories: async (limit: number = 10, logFileId?: string): Promise<TopCategories> => {
    const params: any = { limit };
    if (logFileId) params.log_file_id = logFileId;
    const response = await apiClient.get('/dashboard/top-categories', { params });
    return response.data;
  },

  getRecentLogs: async (limit: number = 10, logFileId?: string): Promise<RecentLogs> => {
    const params: any = { limit };
    if (logFileId) params.log_file_id = logFileId;
    const response = await apiClient.get('/dashboard/recent-logs', { params });
    return response.data;
  },

  getLogSummary: async (logFileId: string): Promise<LogSummary> => {
    const response = await apiClient.get(`/ai/log-summary/${logFileId}`);
    return response.data;
  },
};

