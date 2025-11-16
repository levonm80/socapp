import { apiClient } from './client';

export interface LogFile {
  id: string;
  filename: string;
  uploaded_by: string;
  uploaded_at: string;
  status: 'uploading' | 'processing' | 'completed' | 'failed';
  total_entries: number;
  date_range_start: string | null;
  date_range_end: string | null;
  metadata: any;
}

export interface UploadResponse {
  log_file_id: string;
  status: string;
}

export interface LogFilePreview {
  preview: string[];
}

export interface LogEntry {
  id: string;
  log_file_id: string;
  timestamp: string;
  location: string | null;
  protocol: string | null;
  url: string;
  domain: string | null;
  action: string;
  app_name: string | null;
  app_class: string | null;
  throttle_req_size: number | null;
  throttle_resp_size: number | null;
  req_size: number | null;
  resp_size: number | null;
  url_class: string | null;
  url_supercat: string | null;
  url_cat: string | null;
  dlp_dict: string | null;
  dlp_eng: string | null;
  dlp_hits: number | null;
  file_class: string | null;
  file_type: string | null;
  location2: string | null;
  department: string | null;
  client_ip: string | null;
  server_ip: string | null;
  http_method: string | null;
  http_status: number | null;
  user_agent: string | null;
  threat_category: string | null;
  fw_filter: string | null;
  fw_rule: string | null;
  policy_type: string | null;
  reason: string | null;
  is_anomalous: boolean;
  anomaly_type: string | null;
  anomaly_reason: string | null;
  anomaly_confidence: number | null;
  created_at: string;
}

export interface ListLogEntriesParams {
  page?: number;
  limit?: number;
  log_file_id?: string;
  start_time?: string;
  end_time?: string;
  action?: string;
  category?: string;
  threat_category?: string;
  user_identifier?: string;
  is_anomalous?: boolean;
  domain?: string;
  search?: string;  // General text search across multiple columns
}

export interface ListLogEntriesResponse {
  entries: LogEntry[];
  total: number;
  page: number;
  limit: number;
}

export const logsApi = {
  uploadLog: async (file: File, onProgress?: (progress: number) => void): Promise<UploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);

    // Create a custom config that removes Content-Type header to let axios set it with boundary
    const config = {
      headers: {
        'Content-Type': undefined, // Let axios set Content-Type with boundary for FormData
      },
      // @ts-ignore - axios supports onUploadProgress but types may not be complete
      onUploadProgress: (progressEvent: any) => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(progress);
        }
      },
    };

    const response = await apiClient.post('/logs/upload', formData, config);

    return response.data;
  },

  getLogFile: async (fileId: string): Promise<LogFile> => {
    const response = await apiClient.get(`/logs/files/${fileId}`);
    return response.data;
  },

  getLogFilePreview: async (fileId: string, lines: number = 10): Promise<LogFilePreview> => {
    const response = await apiClient.get(`/logs/files/${fileId}/preview`, {
      params: { lines },
    });
    return response.data;
  },

  listLogFiles: async (page: number = 1, limit: number = 20): Promise<{ files: LogFile[]; total: number; page: number; limit: number }> => {
    const response = await apiClient.get('/logs/files', {
      params: { page, limit },
    });
    return response.data;
  },

  listLogEntries: async (params: ListLogEntriesParams = {}): Promise<ListLogEntriesResponse> => {
    const {
      page = 1,
      limit = 50,
      log_file_id,
      start_time,
      end_time,
      action,
      category,
      threat_category,
      user_identifier,
      is_anomalous,
      domain,
      search,
    } = params;

    const queryParams: Record<string, any> = { page, limit };
    if (log_file_id) queryParams.log_file_id = log_file_id;
    if (start_time) queryParams.start_time = start_time;
    if (end_time) queryParams.end_time = end_time;
    if (action) queryParams.action = action;
    if (category) queryParams.category = category;
    if (threat_category) queryParams.threat_category = threat_category;
    if (user_identifier) queryParams.user_identifier = user_identifier;
    if (is_anomalous !== undefined) queryParams.is_anomalous = is_anomalous;
    if (domain) queryParams.domain = domain;
    if (search) queryParams.search = search;

    const response = await apiClient.get('/logs/entries', {
      params: queryParams,
    });
    return response.data;
  },

  getLogEntry: async (entryId: string): Promise<LogEntry> => {
    const response = await apiClient.get(`/logs/entries/${entryId}`);
    return response.data;
  },
};

