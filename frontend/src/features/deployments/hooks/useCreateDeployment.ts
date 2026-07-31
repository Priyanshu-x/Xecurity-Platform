import { useMutation } from '@tanstack/react-query';
import { deploymentService } from '../deploymentService';
import { queryKeys } from '@/lib/api/queryKeys';
import { invalidate } from '@/lib/react-query/invalidate';
import { DeploymentCreate } from '../types';

interface UseCreateDeploymentOptions {
  onSuccess?: () => void;
  onError?: (error: Error) => void;
}

export function useCreateDeployment(options?: UseCreateDeploymentOptions) {
  return useMutation({
    mutationFn: (data: DeploymentCreate) => deploymentService.createDeployment(data),
    onSuccess: () => {
      invalidate(queryKeys.deployments.lists());
      options?.onSuccess?.();
    },
    onError: (error) => {
      options?.onError?.(error);
    },
  });
}
