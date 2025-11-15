import { describe, it, expect, vi, beforeEach } from 'vitest';
import { logsApi } from './logs';
import { apiClient } from './client';

// Mock the apiClient
vi.mock('./client', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
  },
}));

const mockApiClient = vi.mocked(apiClient);

describe('logsApi', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('listLogEntries', () => {
    it('should fetch log entries with default pagination when no params provided', async () => {
      // Arrange
      const mockResponse = {
        entries: [],
        total: 0,
        page: 1,
        limit: 50,
      };
      mockApiClient.get.mockResolvedValue({ data: mockResponse });

      // Act
      const result = await logsApi.listLogEntries();

      // Assert
      expect(mockApiClient.get).toHaveBeenCalledWith('/logs/entries', {
        params: { page: 1, limit: 50 },
      });
      expect(result).toEqual(mockResponse);
    });

    it('should fetch log entries with custom pagination when params provided', async () => {
      // Arrange
      const mockResponse = {
        entries: [],
        total: 100,
        page: 2,
        limit: 25,
      };
      mockApiClient.get.mockResolvedValue({ data: mockResponse });

      // Act
      const result = await logsApi.listLogEntries({ page: 2, limit: 25 });

      // Assert
      expect(mockApiClient.get).toHaveBeenCalledWith('/logs/entries', {
        params: { page: 2, limit: 25 },
      });
      expect(result).toEqual(mockResponse);
    });

    it('should include filters when provided', async () => {
      // Arrange
      const mockResponse = {
        entries: [],
        total: 0,
        page: 1,
        limit: 50,
      };
      mockApiClient.get.mockResolvedValue({ data: mockResponse });

      // Act
      await logsApi.listLogEntries({
        page: 1,
        limit: 50,
        action: 'Blocked',
        category: 'Malware',
        is_anomalous: true,
        start_time: '2024-01-01T00:00:00Z',
        end_time: '2024-01-02T00:00:00Z',
        user_identifier: 'user@example.com',
        domain: 'example.com',
      });

      // Assert
      expect(mockApiClient.get).toHaveBeenCalledWith('/logs/entries', {
        params: {
          page: 1,
          limit: 50,
          action: 'Blocked',
          category: 'Malware',
          is_anomalous: true,
          start_time: '2024-01-01T00:00:00Z',
          end_time: '2024-01-02T00:00:00Z',
          user_identifier: 'user@example.com',
          domain: 'example.com',
        },
      });
    });

    it('should handle API errors when fetching entries fails', async () => {
      // Arrange
      const error = new Error('Network error');
      mockApiClient.get.mockRejectedValue(error);

      // Act & Assert
      await expect(logsApi.listLogEntries()).rejects.toThrow('Network error');
    });
  });

  describe('getLogEntry', () => {
    it('should fetch single log entry by id when valid id provided', async () => {
      // Arrange
      const entryId = '123e4567-e89b-12d3-a456-426614174000';
      const mockEntry = {
        id: entryId,
        timestamp: '2024-01-01T00:00:00Z',
        url: 'https://example.com',
        action: 'Allowed',
        is_anomalous: false,
      };
      mockApiClient.get.mockResolvedValue({ data: mockEntry });

      // Act
      const result = await logsApi.getLogEntry(entryId);

      // Assert
      expect(mockApiClient.get).toHaveBeenCalledWith(`/logs/entries/${entryId}`);
      expect(result).toEqual(mockEntry);
    });

    it('should handle API errors when entry not found', async () => {
      // Arrange
      const entryId = '123e4567-e89b-12d3-a456-426614174000';
      const error = { response: { status: 404, data: { error: 'Log entry not found' } } };
      mockApiClient.get.mockRejectedValue(error);

      // Act & Assert
      await expect(logsApi.getLogEntry(entryId)).rejects.toEqual(error);
    });
  });
});

