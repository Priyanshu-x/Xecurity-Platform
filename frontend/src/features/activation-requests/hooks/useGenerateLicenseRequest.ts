import { useMutation, useQueryClient } from '@tanstack/react-query';
import { activationRequestService } from '../services/activationRequestService';
import { queryKeys } from '@/lib/api/queryKeys';
import { LicenseGenerationConfig } from '../types';

export function useGenerateLicenseRequest(id: string) {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (config: LicenseGenerationConfig) => activationRequestService.generateLicense(id, config),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.activationRequests.detail(id) });
      queryClient.invalidateQueries({ queryKey: queryKeys.activationRequests.all() });
    },
  });
}
