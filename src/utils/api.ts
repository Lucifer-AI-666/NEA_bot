/**
 * API Utilities
 * Centralized API communication utilities
 */

import axios, { AxiosError, AxiosResponse } from 'axios';

// API Configuration
export const API_CONFIG = {
  BASE_URL: 'http://localhost:3001',
  TIMEOUT: 30000,
  USER_ID: 'tauros',
} as const;

// Create axios instance with default configuration
export const apiClient = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  timeout: API_CONFIG.TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
    'x-user-id': API_CONFIG.USER_ID,
  },
});

// Request/Response types
export interface ChatRequest {
  message: string;
}

export interface ChatResponse {
  response: string;
  timestamp?: string;
}

// API Methods
export const chatAPI = {
  sendMessage: async (message: string): Promise<ChatResponse> => {
    try {
      const response: AxiosResponse<ChatResponse> = await apiClient.post('/chat', {
        message,
      });
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new APIError(
          error.message || 'Network error',
          error.response?.status || 0,
          error.code
        );
      }
      throw new APIError('Unknown error occurred', 0);
    }
  },
};

// Custom API Error class
export class APIError extends Error {
  constructor(
    message: string,
    public statusCode: number,
    public code?: string
  ) {
    super(message);
    this.name = 'APIError';
  }

  // Helper methods for error type checking
  get isTimeoutError(): boolean {
    return this.code === 'ECONNABORTED';
  }

  get isNetworkError(): boolean {
    return this.statusCode === 0 || !this.statusCode;
  }

  get isServerError(): boolean {
    return this.statusCode >= 500;
  }

  get isClientError(): boolean {
    return this.statusCode >= 400 && this.statusCode < 500;
  }

  // Get user-friendly error message
  getUserMessage(): string {
    if (this.isTimeoutError) {
      return 'Timeout della richiesta. Riprova.';
    }
    
    if (this.isNetworkError) {
      return 'Impossibile connettersi al server.';
    }
    
    if (this.isServerError) {
      return 'Errore interno del server.';
    }
    
    if (this.isClientError) {
      return 'Richiesta non valida.';
    }
    
    return 'Errore nel contatto con TAUROS.';
  }
}