import { api } from '@/lib/api';
import { TrialToken, GenerateTokenRequest, ManifestResponse } from '../types';

export const trialTokenService = {
  getAll: async (): Promise<TrialToken[]> => {
    const response = await api.get<TrialToken[]>('/trial-tokens');
    return response.data;
  },

  generate: async (data: GenerateTokenRequest): Promise<TrialToken> => {
    const response = await api.post<TrialToken>('/trial-tokens', data);
    return response.data;
  },

  revoke: async (id: string): Promise<TrialToken> => {
    const response = await api.patch<TrialToken>(`/trial-tokens/${id}/revoke`);
    return response.data;
  },

  getManifest: async (): Promise<ManifestResponse> => {
    const response = await api.get<ManifestResponse>('/trial-tokens/manifest');
    return response.data;
  },
};
