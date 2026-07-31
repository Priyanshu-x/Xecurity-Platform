import { createCrudService } from '@/lib/api/crudService';
import { Release, ReleaseCreate, ReleaseUpdate } from '../types';

export const releaseService = createCrudService<Release, ReleaseCreate, ReleaseUpdate>({
  endpoint: '/releases',
});
