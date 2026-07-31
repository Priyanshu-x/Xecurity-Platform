import { useQuery } from '@tanstack/react-query';
import { deviceService } from '../services/deviceService';
import { queryKeys } from '@/lib/api/queryKeys';

export function useDevices() {
  return useQuery({
    queryKey: queryKeys.devices.all(),
    queryFn: () => deviceService.getAll(),
  });
}
