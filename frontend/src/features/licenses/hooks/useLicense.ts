import { useQuery } from '@tanstack/react-query';
import { licenseService } from '../licenseService';
import { queryKeys } from '@/lib/api/queryKeys';

export function useLicense(id: string) {
  return useQuery({
    queryKey: queryKeys.licenses.detail(id),
    queryFn: () => licenseService.getOne(id),
    enabled: !!id,
  });
}
