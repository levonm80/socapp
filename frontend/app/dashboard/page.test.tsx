import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import DashboardPage from './page';
import { dashboardApi } from '@/lib/api/dashboard';
import { useAuth } from '@/lib/contexts/AuthContext';

// Mock dependencies
vi.mock('@/lib/api/dashboard');
vi.mock('@/lib/contexts/AuthContext');
vi.mock('next/link', () => ({
  default: ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  ),
}));

const mockUseAuth = vi.mocked(useAuth);
const mockDashboardApi = vi.mocked(dashboardApi);

describe('DashboardPage', () => {
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

  it('should fetch all sections independently when component mounts', async () => {
    // Arrange
    const mockStats = { total_requests: 1000, blocked_events: 50, malicious_urls: 10, high_risk_users: 3, data_transfer_bytes: 1000000, trends: { total_requests_pct: 5.0, blocked_events_pct: 2.0 } };
    const mockTimeline = { buckets: [] };
    const mockCategories = { categories: [] };
    const mockRecentLogs = { entries: [] };

    mockDashboardApi.getStats = vi.fn().mockResolvedValue(mockStats);
    mockDashboardApi.getTimeline = vi.fn().mockResolvedValue(mockTimeline);
    mockDashboardApi.getTopCategories = vi.fn().mockResolvedValue(mockCategories);
    mockDashboardApi.getRecentLogs = vi.fn().mockResolvedValue(mockRecentLogs);

    // Act
    render(<DashboardPage />);

    // Assert - all API calls should be made independently (not waiting for each other)
    await waitFor(() => {
      expect(mockDashboardApi.getStats).toHaveBeenCalled();
      expect(mockDashboardApi.getTimeline).toHaveBeenCalledWith(24);
      expect(mockDashboardApi.getTopCategories).toHaveBeenCalledWith(10);
      expect(mockDashboardApi.getRecentLogs).toHaveBeenCalledWith(4);
    });
  });

  it('should display stats section when stats data is loaded independently', async () => {
    // Arrange
    const mockStats = { total_requests: 1000, blocked_events: 50, malicious_urls: 10, high_risk_users: 3, data_transfer_bytes: 1000000, trends: { total_requests_pct: 5.0, blocked_events_pct: 2.0 } };
    
    mockDashboardApi.getStats = vi.fn().mockResolvedValue(mockStats);
    mockDashboardApi.getTimeline = vi.fn().mockImplementation(() => new Promise(() => {})); // Never resolves (simulating slow load)
    mockDashboardApi.getTopCategories = vi.fn().mockImplementation(() => new Promise(() => {}));
    mockDashboardApi.getRecentLogs = vi.fn().mockImplementation(() => new Promise(() => {}));

    // Act
    render(<DashboardPage />);

    // Assert - stats should appear even if timeline is still loading
    await waitFor(() => {
      expect(screen.getByText('Total Requests')).toBeInTheDocument();
      expect(screen.getByText('1.0K')).toBeInTheDocument();
    });
  });

  it('should display timeline section when timeline data loads independently', async () => {
    // Arrange
    const mockStats = { total_requests: 1000, blocked_events: 50, malicious_urls: 10, high_risk_users: 3, data_transfer_bytes: 1000000, trends: { total_requests_pct: 5.0, blocked_events_pct: 2.0 } };
    const mockTimeline = { buckets: [{ time: '2024-01-01T00:00:00', total: 100, blocked: 5 }] };
    
    mockDashboardApi.getStats = vi.fn().mockImplementation(() => new Promise(() => {})); // Never resolves
    mockDashboardApi.getTimeline = vi.fn().mockResolvedValue(mockTimeline);
    mockDashboardApi.getTopCategories = vi.fn().mockImplementation(() => new Promise(() => {}));
    mockDashboardApi.getRecentLogs = vi.fn().mockImplementation(() => new Promise(() => {}));

    // Act
    render(<DashboardPage />);

    // Assert - timeline should appear even if stats are still loading
    await waitFor(() => {
      expect(screen.getByText(/Traffic & Block Events/i)).toBeInTheDocument();
    });
  });

  it('should display loading state for individual sections independently', async () => {
    // Arrange
    mockDashboardApi.getStats = vi.fn().mockImplementation(() => new Promise(() => {})); // Never resolves
    mockDashboardApi.getTimeline = vi.fn().mockImplementation(() => new Promise(() => {}));
    mockDashboardApi.getTopCategories = vi.fn().mockImplementation(() => new Promise(() => {}));
    mockDashboardApi.getRecentLogs = vi.fn().mockImplementation(() => new Promise(() => {}));

    // Act
    render(<DashboardPage />);

    // Assert - component should render (not show overall loading screen)
    // Individual sections can show their own loading states
    expect(screen.queryByText('Loading dashboard...')).not.toBeInTheDocument();
  });

  it('should handle errors for individual sections without blocking other sections', async () => {
    // Arrange
    const mockStats = { total_requests: 1000, blocked_events: 50, malicious_urls: 10, high_risk_users: 3, data_transfer_bytes: 1000000, trends: { total_requests_pct: 5.0, blocked_events_pct: 2.0 } };
    const mockTimeline = { buckets: [] };
    const errorResponse = { response: { data: { error: 'Failed to load categories' } } };
    
    mockDashboardApi.getStats = vi.fn().mockResolvedValue(mockStats);
    mockDashboardApi.getTimeline = vi.fn().mockResolvedValue(mockTimeline);
    mockDashboardApi.getTopCategories = vi.fn().mockRejectedValue(errorResponse);
    mockDashboardApi.getRecentLogs = vi.fn().mockResolvedValue({ entries: [] });

    // Act
    render(<DashboardPage />);

    // Assert - stats and timeline should still display even if categories fail
    await waitFor(() => {
      expect(screen.getByText('Total Requests')).toBeInTheDocument();
    });
  });

  it('should refresh all sections independently when refresh button is clicked', async () => {
    // Arrange
    const mockStats = { total_requests: 1000, blocked_events: 50, malicious_urls: 10, high_risk_users: 3, data_transfer_bytes: 1000000, trends: { total_requests_pct: 5.0, blocked_events_pct: 2.0 } };
    const mockTimeline = { buckets: [] };
    const mockCategories = { categories: [] };
    const mockRecentLogs = { entries: [] };

    mockDashboardApi.getStats = vi.fn().mockResolvedValue(mockStats);
    mockDashboardApi.getTimeline = vi.fn().mockResolvedValue(mockTimeline);
    mockDashboardApi.getTopCategories = vi.fn().mockResolvedValue(mockCategories);
    mockDashboardApi.getRecentLogs = vi.fn().mockResolvedValue(mockRecentLogs);

    render(<DashboardPage />);

    // Wait for initial load
    await waitFor(() => {
      expect(mockDashboardApi.getStats).toHaveBeenCalledTimes(1);
    });

    // Act - click refresh button
    const refreshButton = screen.getByRole('button', { name: /refresh/i });
    refreshButton.click();

    // Assert - all sections should be refreshed independently
    await waitFor(() => {
      expect(mockDashboardApi.getStats).toHaveBeenCalledTimes(2);
      expect(mockDashboardApi.getTimeline).toHaveBeenCalledTimes(2);
      expect(mockDashboardApi.getTopCategories).toHaveBeenCalledTimes(2);
      expect(mockDashboardApi.getRecentLogs).toHaveBeenCalledTimes(2);
    });
  });
});

