import { useMutation, useQueryClient } from '@tanstack/react-query';
import { deviceService } from '../services/deviceService';
import { queryKeys } from '@/lib/api/queryKeys';
import { DeviceUpdate } from '../types';

export function useUpdateDevice(id: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: DeviceUpdate) => deviceService.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.devices.detail(id) });
      queryClient.invalidateQueries({ queryKey: queryKeys.devices.all() });
    },
  });
}
