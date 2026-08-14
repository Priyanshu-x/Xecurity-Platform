import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { trialTokenService } from '../services/trialTokenService';
import { GenerateTokenRequest } from '../types';

export const useTrialTokens = () => {
  return useQuery({
    queryKey: ['trialTokens'],
    queryFn: () => trialTokenService.getAll(),
  });
};

export const useGenerateTrialToken = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: GenerateTokenRequest) => trialTokenService.generate(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['trialTokens'] });
    },
  });
};

export const useRevokeTrialToken = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: string) => trialTokenService.revoke(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['trialTokens'] });
    },
  });
};

export const useManifest = () => {
  return useQuery({
    queryKey: ['manifest'],
    queryFn: () => trialTokenService.getManifest(),
  });
};
