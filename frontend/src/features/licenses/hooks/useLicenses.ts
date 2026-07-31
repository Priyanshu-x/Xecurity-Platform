import { useQuery } from '@tanstack/react-query';
import { licenseService } from '../licenseService';
import { queryKeys } from '@/lib/api/queryKeys';

export function useLicenses(params?: Record<string, any>) {
  return useQuery({
    queryKey: queryKeys.licenses.list(params),
    queryFn: () => licenseService.getAll(params),
  });
}
