import { api } from '@/lib/api';
import { Deployment, DeploymentCreate, DeploymentUpdate } from './types';

export const deploymentService = {
  getDeployments: async (): Promise<Deployment[]> => {
    const response = await api.get<Deployment[]>('/deployments');
    return response.data;
  },

  getDeployment: async (id: string): Promise<Deployment> => {
    const response = await api.get<Deployment>(`/deployments/${id}`);
    return response.data;
  },

  createDeployment: async (data: DeploymentCreate): Promise<Deployment> => {
    const response = await api.post<Deployment>('/deployments', data);
    return response.data;
  },

  updateDeployment: async (id: string, data: DeploymentUpdate): Promise<Deployment> => {
    const response = await api.patch<Deployment>(`/deployments/${id}`, data);
    return response.data;
  },

  deleteDeployment: async (id: string): Promise<void> => {
    await api.delete(`/deployments/${id}`);
  },
};
