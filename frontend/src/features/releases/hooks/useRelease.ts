import { useQuery } from '@tanstack/react-query';
import { queryKeys } from '@/lib/api/queryKeys';
import { releaseService } from '../services/releaseService';
import { Release } from '../types';

export function useRelease(id: string) {
  return useQuery<Release>({
    queryKey: queryKeys.releases.detail(id),
    queryFn: () => releaseService.getOne(id),
    enabled: !!id,
  });
}
