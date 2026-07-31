import { useMutation, useQueryClient } from '@tanstack/react-query';
import { activationRequestService } from '../services/activationRequestService';
import { queryKeys } from '@/lib/api/queryKeys';

export function useRejectRequest(id: string) {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: { reason: string, notes?: string }) => activationRequestService.reject(id, data.reason, data.notes),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.activationRequests.detail(id) });
      queryClient.invalidateQueries({ queryKey: queryKeys.activationRequests.all() });
    },
  });
}
