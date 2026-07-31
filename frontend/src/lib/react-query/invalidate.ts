import { QueryKey } from '@tanstack/react-query';
import { queryClient } from './queryClient';

export const invalidate = (queryKey: QueryKey) => {
  return queryClient.invalidateQueries({ queryKey });
};
