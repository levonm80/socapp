import { apiClient } from './client';

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  token: string;
  user: {
    id: string;
    email: string;
  };
}

export const authApi = {
  login: async (data: LoginRequest): Promise<LoginResponse> => {
    const response = await apiClient.post('/auth/login', data);
    if (response.data.token) {
      localStorage.setItem('auth_token', response.data.token);
    }
    return response.data;
  },

  logout: async (): Promise<void> => {
    await apiClient.post('/auth/logout');
    localStorage.removeItem('auth_token');
  },

  getCurrentUser: async () => {
    const response = await apiClient.get('/auth/me');
    return response.data.user;
  },
};

