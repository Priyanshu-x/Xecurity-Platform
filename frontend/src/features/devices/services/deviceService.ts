import { createCrudService } from '@/lib/api/crudService';
import { Device, DeviceCreate, DeviceUpdate } from '../types';

export const deviceService = createCrudService<Device, DeviceCreate, DeviceUpdate>('/api/v1/devices');
