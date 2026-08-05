import api from '@/lib/api/client';
import { DashboardStatsResponse } from '../types';

class DashboardService {
  async getStats(): Promise<DashboardStatsResponse> {
    const response = await api.get('/dashboard/');
    return response.data;
  }
}

export const dashboardService = new DashboardService();
