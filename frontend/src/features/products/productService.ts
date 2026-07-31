import { api } from '@/lib/api';
import { Product, ProductCreate, ProductUpdate } from './types';

export const productService = {
  getProducts: async (includeDeleted: boolean = false): Promise<Product[]> => {
    const response = await api.get<Product[]>('/products/', {
      params: { include_deleted: includeDeleted },
    });
    return response.data;
  },

  getProduct: async (id: string): Promise<Product> => {
    const response = await api.get<Product>(`/products/${id}`);
    return response.data;
  },

  createProduct: async (data: ProductCreate): Promise<Product> => {
    const response = await api.post<Product>('/products/', data);
    return response.data;
  },

  updateProduct: async (id: string, data: ProductUpdate): Promise<Product> => {
    const response = await api.put<Product>(`/products/${id}`, data);
    return response.data;
  },

  deleteProduct: async (id: string): Promise<void> => {
    await api.delete(`/products/${id}`);
  },
};
