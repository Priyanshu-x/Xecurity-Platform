import { useMutation, useQueryClient } from '@tanstack/react-query';
import { queryKeys } from '@/lib/api/queryKeys';
import { releaseService } from '../services/releaseService';
import { Release, ReleaseCreate } from '../types';

export function useCreateRelease() {
  const queryClient = useQueryClient();

  return useMutation<Release, Error, ReleaseCreate>({
    mutationFn: (data) => releaseService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.releases.all() });
    },
  });
}
