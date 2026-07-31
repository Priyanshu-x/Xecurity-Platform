import { useMutation } from '@tanstack/react-query';
import { licenseService } from '../licenseService';
import { queryKeys } from '@/lib/api/queryKeys';
import { invalidate } from '@/lib/react-query/invalidate';
import { LicenseIssue } from '../types';

interface UseIssueLicenseOptions {
  onSuccess?: () => void;
  onError?: (error: Error) => void;
}

export function useIssueLicense(options?: UseIssueLicenseOptions) {
  return useMutation({
    mutationFn: ({ deploymentId, data }: { deploymentId: string; data: LicenseIssue }) => 
      licenseService.issue(deploymentId, data),
    onSuccess: () => {
      invalidate(queryKeys.licenses.lists());
      options?.onSuccess?.();
    },
    onError: (error) => {
      options?.onError?.(error);
    },
  });
}
