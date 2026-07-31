import { useQuery } from '@tanstack/react-query';
import { queryKeys } from '@/lib/api/queryKeys';
import { releaseService } from '../services/releaseService';
import { Release } from '../types';

export function useReleases(filters?: { product_id?: string; channel?: string }) {
  return useQuery<Release[]>({
    queryKey: queryKeys.releases.list(filters),
    queryFn: () => releaseService.getAll(filters),
  });
}
