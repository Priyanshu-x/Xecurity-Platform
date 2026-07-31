import { api } from '@/lib/api';
import { createCrudService } from '@/lib/api/crudService';
import { License, LicenseIssue, LicenseRevoke } from './types';

export const licenseService = createCrudService<
  License,
  any, // We don't use standard create for licenses
  any, // We don't use standard update for licenses
  {
    issue: (deploymentId: string, data: LicenseIssue) => Promise<License>;
    revoke: (id: string, data: LicenseRevoke) => Promise<License>;
  }
>({
  endpoint: '/licenses',
  custom: {
    issue: async (deploymentId: string, data: LicenseIssue): Promise<License> => {
      const response = await api.post<License>(`/licenses/${deploymentId}/issue`, data);
      return response.data;
    },
    revoke: async (id: string, data: LicenseRevoke): Promise<License> => {
      const response = await api.post<License>(`/licenses/${id}/revoke`, data);
      return response.data;
    },
  },
});
