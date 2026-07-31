import { api } from '@/lib/api';

export interface CrudServiceOptions<TCustom> {
  endpoint: string;
  custom?: TCustom;
}

export function createCrudService<T, TCreate, TUpdate, TCustom = {}>(
  options: CrudServiceOptions<TCustom>
) {
  const { endpoint, custom } = options;

  const base = {
    getAll: async (params?: Record<string, any>): Promise<T[]> => {
      const response = await api.get<T[]>(endpoint, { params });
      return response.data;
    },

    getOne: async (id: string): Promise<T> => {
      const response = await api.get<T>(`${endpoint}/${id}`);
      return response.data;
    },

    create: async (data: TCreate): Promise<T> => {
      const response = await api.post<T>(endpoint, data);
      return response.data;
    },

    update: async (id: string, data: TUpdate): Promise<T> => {
      const response = await api.patch<T>(`${endpoint}/${id}`, data);
      return response.data;
    },

    remove: async (id: string): Promise<void> => {
      await api.delete(`${endpoint}/${id}`);
    },
  };

  return {
    ...base,
    ...custom,
  } as typeof base & TCustom;
}
