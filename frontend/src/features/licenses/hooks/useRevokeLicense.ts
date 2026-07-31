import { useMutation } from '@tanstack/react-query';
import { licenseService } from '../licenseService';
import { queryKeys } from '@/lib/api/queryKeys';
import { invalidate } from '@/lib/react-query/invalidate';
import { LicenseRevoke } from '../types';

interface UseRevokeLicenseOptions {
  onSuccess?: () => void;
  onError?: (error: Error) => void;
}

export function useRevokeLicense(options?: UseRevokeLicenseOptions) {
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: LicenseRevoke }) => 
      licenseService.revoke(id, data),
    onSuccess: (_, variables) => {
      invalidate(queryKeys.licenses.lists());
      invalidate(queryKeys.licenses.detail(variables.id));
      options?.onSuccess?.();
    },
    onError: (error) => {
      options?.onError?.(error);
    },
  });
}
