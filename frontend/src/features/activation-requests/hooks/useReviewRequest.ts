import { useMutation, useQueryClient } from '@tanstack/react-query';
import { activationRequestService } from '../services/activationRequestService';
import { queryKeys } from '@/lib/api/queryKeys';

export function useReviewRequest(id: string) {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: () => activationRequestService.review(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.activationRequests.detail(id) });
      queryClient.invalidateQueries({ queryKey: queryKeys.activationRequests.all() });
    },
  });
}
