import { api } from '@/lib/api';
import { Capability, CapabilityCreate, CapabilityUpdate } from './types';

export const capabilityService = {
  getCapabilities: async (): Promise<Capability[]> => {
    const response = await api.get<Capability[]>('/capabilities');
    return response.data;
  },

  getCapability: async (id: string): Promise<Capability> => {
    const response = await api.get<Capability>(`/capabilities/${id}`);
    return response.data;
  },

  getProductCapabilities: async (productId: string): Promise<Capability[]> => {
    const response = await api.get<Capability[]>(`/capabilities/product/${productId}`);
    return response.data;
  },

  createCapability: async (data: CapabilityCreate): Promise<Capability> => {
    const response = await api.post<Capability>('/capabilities', data);
    return response.data;
  },

  updateCapability: async (id: string, data: CapabilityUpdate): Promise<Capability> => {
    const response = await api.patch<Capability>(`/capabilities/${id}`, data);
    return response.data;
  },

  deleteCapability: async (id: string): Promise<void> => {
    await api.delete(`/capabilities/${id}`);
  },
};
