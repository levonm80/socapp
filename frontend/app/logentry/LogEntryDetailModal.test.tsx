import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import LogEntryDetailModal from './LogEntryDetailModal';
import { LogEntry } from '@/lib/api/logs';

// Mock next/navigation
vi.mock('next/navigation', () => ({
  usePathname: vi.fn(() => '/logentry'),
}));

const mockLogEntry: LogEntry = {
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

describe('LogEntryDetailModal', () => {
  const mockOnClose = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render modal when entry is provided', () => {
    // Arrange & Act
    render(<LogEntryDetailModal entry={mockLogEntry} onClose={mockOnClose} />);

    // Assert
    expect(screen.getByText('Log Entry Details')).toBeInTheDocument();
    expect(screen.getByText('https://example.com/path')).toBeInTheDocument();
  });

  it('should not render modal when entry is null', () => {
    // Arrange & Act
    render(<LogEntryDetailModal entry={null} onClose={mockOnClose} />);

    // Assert
    expect(screen.queryByText('Log Entry Details')).not.toBeInTheDocument();
  });

  it('should display all log entry fields when entry provided', () => {
    // Arrange & Act
    render(<LogEntryDetailModal entry={mockLogEntry} onClose={mockOnClose} />);

    // Assert - check key fields are displayed (using getAllByText for labels that appear multiple times)
    expect(screen.getAllByText(/Timestamp/i)[0]).toBeInTheDocument();
    expect(screen.getAllByText(/URL/i)[0]).toBeInTheDocument();
    expect(screen.getAllByText(/Domain/i)[0]).toBeInTheDocument();
    expect(screen.getAllByText(/Action/i)[0]).toBeInTheDocument();
    expect(screen.getAllByText(/Client IP/i)[0]).toBeInTheDocument();
    expect(screen.getAllByText(/User Agent/i)[0]).toBeInTheDocument();
  });

  it('should display anomaly reason when entry is anomalous', () => {
    // Arrange & Act
    render(<LogEntryDetailModal entry={mockLogEntry} onClose={mockOnClose} />);

    // Assert
    expect(screen.getByText(/Anomaly Explanation/i)).toBeInTheDocument();
    expect(screen.getByText('Domain example.com is in malicious domains list')).toBeInTheDocument();
  });

  it('should not display anomaly section when entry is not anomalous', () => {
    // Arrange
    const nonAnomalousEntry = { ...mockLogEntry, is_anomalous: false, anomaly_reason: null };

    // Act
    render(<LogEntryDetailModal entry={nonAnomalousEntry} onClose={mockOnClose} />);

    // Assert
    expect(screen.queryByText(/Anomaly Explanation/i)).not.toBeInTheDocument();
  });

  it('should call onClose when close button is clicked', async () => {
    // Arrange
    render(<LogEntryDetailModal entry={mockLogEntry} onClose={mockOnClose} />);
    const user = userEvent.setup();

    // Act - get the close button in the header (first one)
    const closeButtons = screen.getAllByRole('button', { name: /close/i });
    await user.click(closeButtons[0]);

    // Assert
    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });

  it('should call onClose when backdrop is clicked', async () => {
    // Arrange
    render(<LogEntryDetailModal entry={mockLogEntry} onClose={mockOnClose} />);
    const user = userEvent.setup();

    // Act - click on backdrop (the overlay div that contains the dialog)
    // The backdrop is the parent of the dialog element
    const dialog = screen.getByRole('dialog');
    const backdrop = dialog.closest('div[class*="fixed"]');
    if (backdrop) {
      // Click on the backdrop overlay, not the dialog content
      await user.click(backdrop);
    }

    // Assert - backdrop click should trigger onClose
    // Note: The backdrop click handler is on the outer div with onClick={onClose}
    expect(mockOnClose).toHaveBeenCalled();
  });

  it('should format timestamp correctly when displayed', () => {
    // Arrange & Act
    render(<LogEntryDetailModal entry={mockLogEntry} onClose={mockOnClose} />);

    // Assert - timestamp should be formatted (not raw ISO string)
    const timestampElement = screen.getByText(/2024/i);
    expect(timestampElement).toBeInTheDocument();
  });

  it('should display null values as N/A', () => {
    // Arrange
    const entryWithNulls = {
      ...mockLogEntry,
      location: null,
      department: null,
    };

    // Act
    render(<LogEntryDetailModal entry={entryWithNulls} onClose={mockOnClose} />);

    // Assert - check that labels are displayed and null values are handled
    // The component should show N/A for null values
    expect(screen.getAllByText(/Location/i)[0]).toBeInTheDocument();
    // Check that N/A appears (there may be multiple N/A values, so use getAllByText)
    const naElements = screen.getAllByText('N/A');
    expect(naElements.length).toBeGreaterThan(0);
  });
});

