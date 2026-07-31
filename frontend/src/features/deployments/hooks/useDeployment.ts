import { useQuery } from '@tanstack/react-query';
import { deploymentService } from '../deploymentService';
import { queryKeys } from '@/lib/api/queryKeys';

export function useDeployment(id: string) {
  return useQuery({
    queryKey: queryKeys.deployments.detail(id),
    queryFn: () => deploymentService.getDeployment(id),
    enabled: !!id,
  });
}
