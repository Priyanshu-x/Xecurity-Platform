import { useMutation, useQueryClient } from '@tanstack/react-query';
import { queryKeys } from '@/lib/api/queryKeys';
import { releaseService } from '../services/releaseService';
import { Release, ReleaseUpdate } from '../types';

export function useUpdateRelease() {
  const queryClient = useQueryClient();

  return useMutation<Release, Error, { id: string; data: ReleaseUpdate }>({
    mutationFn: ({ id, data }) => releaseService.update(id, data),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.releases.all() });
      queryClient.setQueryData(queryKeys.releases.detail(data.id), data);
    },
  });
}
