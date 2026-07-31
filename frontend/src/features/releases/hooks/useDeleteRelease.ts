import { useMutation, useQueryClient } from '@tanstack/react-query';
import { queryKeys } from '@/lib/api/queryKeys';
import { releaseService } from '../services/releaseService';

export function useDeleteRelease() {
  const queryClient = useQueryClient();

  return useMutation<void, Error, string>({
    mutationFn: (id) => releaseService.remove(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.releases.all() });
      queryClient.removeQueries({ queryKey: queryKeys.releases.detail(id) });
    },
  });
}
