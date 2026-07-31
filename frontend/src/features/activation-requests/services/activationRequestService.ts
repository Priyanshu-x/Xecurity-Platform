import { api } from '@/lib/api';
import { ActivationRequest, LicenseGenerationConfig } from '../types';

export const activationRequestService = {
  getAll: async (params?: Record<string, any>) => {
    const response = await api.get('/activation-requests/', { params });
    return response.data;
  },

  get: async (id: string): Promise<ActivationRequest> => {
    const response = await api.get(`/activation-requests/${id}`);
    return response.data;
  },

  review: async (id: string): Promise<ActivationRequest> => {
    const response = await api.post(`/activation-requests/${id}/review`);
    return response.data;
  },

  reject: async (id: string, reason: string, notes?: string): Promise<ActivationRequest> => {
    const response = await api.post(`/activation-requests/${id}/reject`, { reason, notes });
    return response.data;
  },

  generateLicense: async (id: string, config: LicenseGenerationConfig): Promise<ActivationRequest> => {
    const response = await api.post(`/activation-requests/${id}/generate`, config);
    return response.data;
  },
};
