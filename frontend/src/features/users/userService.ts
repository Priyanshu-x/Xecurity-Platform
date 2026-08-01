import { api } from '@/lib/api';
import { User, UserCreate, UserUpdate } from './types';

export const userService = {
  getUsers: async (): Promise<User[]> => {
    const response = await api.get<User[]>('/users');
    return response.data;
  },

  getUser: async (id: string): Promise<User> => {
    const response = await api.get<User>(`/users/${id}`);
    return response.data;
  },

  createUser: async (data: UserCreate): Promise<User> => {
    const response = await api.post<User>('/users', data);
    return response.data;
  },

  updateUser: async (id: string, data: UserUpdate): Promise<User> => {
    const response = await api.patch<User>(`/users/${id}`, data);
    return response.data;
  },

  disableUser: async (id: string): Promise<User> => {
    const response = await api.post<User>(`/users/${id}/disable`);
    return response.data;
  },
};
