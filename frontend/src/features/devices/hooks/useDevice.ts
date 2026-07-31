import { useQuery } from '@tanstack/react-query';
import { deviceService } from '../services/deviceService';
import { queryKeys } from '@/lib/api/queryKeys';

export function useDevice(id: string) {
  return useQuery({
    queryKey: queryKeys.devices.detail(id),
    queryFn: () => deviceService.get(id),
    enabled: !!id,
  });
}
