import { useQuery } from '@tanstack/react-query';
import { deploymentService } from '../deploymentService';
import { queryKeys } from '@/lib/api/queryKeys';

export function useDeployments(params?: Record<string, any>) {
  return useQuery({
    queryKey: queryKeys.deployments.list(params),
    queryFn: () => deploymentService.getDeployments(),
  });
}
