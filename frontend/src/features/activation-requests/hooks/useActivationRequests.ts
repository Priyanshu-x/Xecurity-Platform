import { useQuery } from '@tanstack/react-query';
import { activationRequestService } from '../services/activationRequestService';
import { queryKeys } from '@/lib/api/queryKeys';

export function useActivationRequests(params?: Record<string, any>) {
  return useQuery({
    queryKey: queryKeys.activationRequests.list(params || {}),
    queryFn: () => activationRequestService.getAll(params),
  });
}
