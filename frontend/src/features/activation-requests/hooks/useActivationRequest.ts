import { useQuery } from '@tanstack/react-query';
import { activationRequestService } from '../services/activationRequestService';
import { queryKeys } from '@/lib/api/queryKeys';

export function useActivationRequest(id: string) {
  return useQuery({
    queryKey: queryKeys.activationRequests.detail(id),
    queryFn: () => activationRequestService.get(id),
    enabled: !!id,
  });
}
