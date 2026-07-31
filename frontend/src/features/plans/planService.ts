import { api } from '@/lib/api';
import { Plan, PlanCreate, PlanUpdate } from './types';

export const planService = {
  getPlans: async (): Promise<Plan[]> => {
    const response = await api.get<Plan[]>('/plans');
    return response.data;
  },

  getPlan: async (id: string): Promise<Plan> => {
    const response = await api.get<Plan>(`/plans/${id}`);
    return response.data;
  },

  createPlan: async (data: PlanCreate): Promise<Plan> => {
    const response = await api.post<Plan>('/plans', data);
    return response.data;
  },

  updatePlan: async (id: string, data: PlanUpdate): Promise<Plan> => {
    const response = await api.patch<Plan>(`/plans/${id}`, data);
    return response.data;
  },

  assignCapability: async (planId: string, capabilityId: string): Promise<void> => {
    await api.post(`/plans/${planId}/capabilities/${capabilityId}`);
  },

  removeCapability: async (planId: string, capabilityId: string): Promise<void> => {
    await api.delete(`/plans/${planId}/capabilities/${capabilityId}`);
  },
};
