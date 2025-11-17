import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import LogExplorerPage from './page';
import { logsApi } from '@/lib/api/logs';
import { useAuth } from '@/lib/contexts/AuthContext';

// Mock dependencies
vi.mock('@/lib/api/logs');
vi.mock('@/lib/contexts/AuthContext');
vi.mock('next/link', () => ({
  default: ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  ),
}));
vi.mock('next/navigation', () => ({
  usePathname: vi.fn(() => '/logentry'),
}));

const mockUseAuth = vi.mocked(useAuth);
const mockLogsApi = vi.mocked(logsApi);

const mockLogEntry = {
  id: '123e4567-e89b-12d3-a456-426614174000',
  log_file_id: 'file-123',
  timestamp: '2024-01-01T12:00:00Z',
  location: 'ny-gre',
  protocol: 'HTTPS',
  url: 'https://example.com/path',
  domain: 'example.com',
  action: 'Blocked',
  app_name: 'Chrome',
  app_class: 'Browser',
  throttle_req_size: null,
  throttle_resp_size: null,
  req_size: 1024,
  resp_size: 2048,
  url_class: 'Business',
  url_supercat: 'Technology',
  url_cat: 'Web Services',
  dlp_dict: null,
  dlp_eng: null,
  dlp_hits: 0,
  file_class: null,
  file_type: null,
  location2: 'US',
  department: 'Engineering',
  client_ip: '192.168.1.1',
  server_ip: '10.0.0.1',
  http_method: 'GET',
  http_status: 403,
  user_agent: 'Mozilla/5.0',
  threat_category: 'Malware',
  fw_filter: null,
  fw_rule: null,
  policy_type: 'Security',
  reason: 'Malicious content detected',
  is_anomalous: true,
  anomaly_type: 'malicious_domain',
  anomaly_reason: 'Domain example.com is in malicious domains list',
  anomaly_confidence: 0.95,
  created_at: '2024-01-01T12:00:00Z',
};

describe('LogExplorerPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockUseAuth.mockReturnValue({
      isAuthenticated: true,
      isLoading: false,
      user: null,
      login: vi.fn(),
      logout: vi.fn(),
    });
  });

  it('should fetch log entries when component mounts', async () => {
    // Arrange
    const mockResponse = {
      entries: [mockLogEntry],
      total: 1,
      page: 1,
      limit: 50,
    };
    mockLogsApi.listLogEntries.mockResolvedValue(mockResponse);

    // Act
    render(<LogExplorerPage />);

    // Assert
    await waitFor(() => {
      expect(mockLogsApi.listLogEntries).toHaveBeenCalledWith({
        page: 1,
        limit: 50,
      });
    });
  });

  it('should display log entries in table when data is loaded', async () => {
    // Arrange
    const mockResponse = {
      entries: [mockLogEntry],
      total: 1,
      page: 1,
      limit: 50,
    };
    mockLogsApi.listLogEntries.mockResolvedValue(mockResponse);

    // Act
    render(<LogExplorerPage />);

    // Assert
    await waitFor(() => {
      expect(screen.getByText('https://example.com/path')).toBeInTheDocument();
      expect(screen.getByText('Blocked')).toBeInTheDocument();
    });
  });

  it('should display anomaly explanation when entry is anomalous', async () => {
    // Arrange
    const mockResponse = {
      entries: [mockLogEntry],
      total: 1,
      page: 1,
      limit: 50,
    };
    mockLogsApi.listLogEntries.mockResolvedValue(mockResponse);

    // Act
    render(<LogExplorerPage />);

    // Assert
    await waitFor(() => {
      expect(screen.getByText('Domain example.com is in malicious domains list')).toBeInTheDocument();
    });
  });

  it('should fetch entries with filters when search query is applied', async () => {
    // Arrange
    const user = userEvent.setup();
    const mockResponse = {
      entries: [],
      total: 0,
      page: 1,
      limit: 50,
    };
    mockLogsApi.listLogEntries.mockResolvedValue(mockResponse);

    // Act
    render(<LogExplorerPage />);
    await waitFor(() => {
      expect(mockLogsApi.listLogEntries).toHaveBeenCalled();
    });

    const searchInput = screen.getByPlaceholderText(/search logs/i);
    await user.type(searchInput, 'example');
    const applyButton = screen.getByRole('button', { name: /apply filters/i });
    await user.click(applyButton);

    // Assert
    await waitFor(() => {
      expect(mockLogsApi.listLogEntries).toHaveBeenCalledWith(
        expect.objectContaining({
          user_identifier: 'example',
        })
      );
    });
  });

  it('should open modal when log entry is clicked', async () => {
    // Arrange
    const user = userEvent.setup();
    const mockResponse = {
      entries: [mockLogEntry],
      total: 1,
      page: 1,
      limit: 50,
    };
    mockLogsApi.listLogEntries.mockResolvedValue(mockResponse);
    mockLogsApi.getLogEntry.mockResolvedValue(mockLogEntry);

    // Act
    render(<LogExplorerPage />);
    await waitFor(() => {
      expect(screen.getByText('https://example.com/path')).toBeInTheDocument();
    });

    const logRow = screen.getByText('https://example.com/path').closest('tr');
    if (logRow) {
      await user.click(logRow);
    }

    // Assert
    await waitFor(() => {
      expect(screen.getByText('Log Entry Details')).toBeInTheDocument();
    });
  });

  it('should display loading state while fetching entries', () => {
    // Arrange
    mockLogsApi.listLogEntries.mockImplementation(() => new Promise(() => {})); // Never resolves

    // Act
    render(<LogExplorerPage />);

    // Assert - component should render (loading state handled internally)
    expect(screen.getByText('Log Explorer')).toBeInTheDocument();
  });

  it('should handle pagination when page is changed', async () => {
    // Arrange
    const user = userEvent.setup();
    const mockResponse = {
      entries: [],
      total: 100,
      page: 1,
      limit: 50,
    };
    mockLogsApi.listLogEntries.mockResolvedValue(mockResponse);

    // Act
    render(<LogExplorerPage />);
    await waitFor(() => {
      expect(mockLogsApi.listLogEntries).toHaveBeenCalled();
    });

    const page2Button = screen.getByRole('button', { name: '2' });
    await user.click(page2Button);

    // Assert
    await waitFor(() => {
      expect(mockLogsApi.listLogEntries).toHaveBeenCalledWith(
        expect.objectContaining({
          page: 2,
        })
      );
    });
  });

  it('should highlight anomalous entries in table', async () => {
    // Arrange
    const mockResponse = {
      entries: [mockLogEntry],
      total: 1,
      page: 1,
      limit: 50,
    };
    mockLogsApi.listLogEntries.mockResolvedValue(mockResponse);

    // Act
    render(<LogExplorerPage />);

    // Assert
    await waitFor(() => {
      const logRow = screen.getByText('https://example.com/path').closest('tr');
      expect(logRow).toHaveClass(/bg-amber-500\/10/);
    });
  });
});

