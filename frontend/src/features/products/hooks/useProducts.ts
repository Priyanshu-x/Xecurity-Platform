import { useQuery } from '@tanstack/react-query';
import { productService } from '../productService';

export function useProducts() {
  return useQuery({
    queryKey: ['products'],
    queryFn: () => productService.getProducts(),
  });
}
