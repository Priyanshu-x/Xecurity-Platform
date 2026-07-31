import { useMutation } from '@tanstack/react-query';
import { deploymentService } from '../deploymentService';
import { queryKeys } from '@/lib/api/queryKeys';
import { invalidate } from '@/lib/react-query/invalidate';
import { DeploymentUpdate } from '../types';

interface UseUpdateDeploymentOptions {
  onSuccess?: () => void;
  onError?: (error: Error) => void;
}

export function useUpdateDeployment(options?: UseUpdateDeploymentOptions) {
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: DeploymentUpdate }) => deploymentService.updateDeployment(id, data),
    onSuccess: (_, variables) => {
      invalidate(queryKeys.deployments.lists());
      invalidate(queryKeys.deployments.detail(variables.id));
      options?.onSuccess?.();
    },
    onError: (error) => {
      options?.onError?.(error);
    },
  });
}
