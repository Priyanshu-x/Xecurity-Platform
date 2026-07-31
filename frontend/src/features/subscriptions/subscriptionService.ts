import { api } from '@/lib/api';
import { Subscription, SubscriptionCreate, SubscriptionUpdate } from './types';

export const subscriptionService = {
  getSubscriptions: async (organizationId?: string): Promise<Subscription[]> => {
    const params = organizationId ? { organization_id: organizationId } : {};
    const response = await api.get<Subscription[]>('/subscriptions', { params });
    return response.data;
  },

  getSubscription: async (id: string): Promise<Subscription> => {
    const response = await api.get<Subscription>(`/subscriptions/${id}`);
    return response.data;
  },

  createSubscription: async (data: SubscriptionCreate): Promise<Subscription> => {
    const response = await api.post<Subscription>('/subscriptions', data);
    return response.data;
  },

  updateSubscription: async (id: string, data: SubscriptionUpdate): Promise<Subscription> => {
    const response = await api.patch<Subscription>(`/subscriptions/${id}`, data);
    return response.data;
  },

  cancelSubscription: async (id: string): Promise<Subscription> => {
    const response = await api.post<Subscription>(`/subscriptions/${id}/cancel`);
    return response.data;
  },
};
