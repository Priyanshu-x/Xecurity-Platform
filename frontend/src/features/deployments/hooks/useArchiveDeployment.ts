import { useMutation } from '@tanstack/react-query';
import { deploymentService } from '../deploymentService';
import { queryKeys } from '@/lib/api/queryKeys';
import { invalidate } from '@/lib/react-query/invalidate';

interface UseArchiveDeploymentOptions {
  onSuccess?: () => void;
  onError?: (error: Error) => void;
}

export function useArchiveDeployment(options?: UseArchiveDeploymentOptions) {
  return useMutation({
    mutationFn: (id: string) => deploymentService.deleteDeployment(id),
    onSuccess: (_, id) => {
      invalidate(queryKeys.deployments.lists());
      invalidate(queryKeys.deployments.detail(id));
      options?.onSuccess?.();
    },
    onError: (error) => {
      options?.onError?.(error);
    },
  });
}
