import { api } from '@/lib/api';
import { Organization, OrganizationCreate, OrganizationUpdate } from './types';

export const organizationService = {
  getOrganizations: async (includeDeleted: boolean = false): Promise<Organization[]> => {
    const response = await api.get<Organization[]>('/organizations/', {
      params: { include_deleted: includeDeleted }
    });
    return response.data;
  },

  getOrganization: async (id: string): Promise<Organization> => {
    const response = await api.get<Organization>(`/organizations/${id}`);
    return response.data;
  },

  createOrganization: async (data: OrganizationCreate): Promise<Organization> => {
    const response = await api.post<Organization>('/organizations/', data);
    return response.data;
  },

  updateOrganization: async (id: string, data: OrganizationUpdate): Promise<Organization> => {
    const response = await api.put<Organization>(`/organizations/${id}`, data);
    return response.data;
  },

  deleteOrganization: async (id: string): Promise<void> => {
    await api.delete(`/organizations/${id}`);
  },
};
