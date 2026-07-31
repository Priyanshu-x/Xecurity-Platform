import { Organization } from '../organizations/types';
import { Plan } from '../plans/types';

export enum SubscriptionStatus {
  ACTIVE = 'ACTIVE',
  EXPIRED = 'EXPIRED',
  CANCELLED = 'CANCELLED',
  SUSPENDED = 'SUSPENDED',
  TRIAL = 'TRIAL',
}

export interface Subscription {
  id: string;
  product_plan_id: string;
  organization_id: string;
  status: SubscriptionStatus;
  notes?: string;
  starts_at: string;
  expires_at?: string;
  activated_at?: string;
  created_at: string;
  updated_at: string;
  
  // Eagerly loaded relationships
  organization?: Organization;
  product_plan?: Plan;
}

export interface SubscriptionCreate {
  organization_id: string;
  product_plan_id: string;
  starts_at?: string;
  expires_at?: string;
  notes?: string;
}

export interface SubscriptionUpdate {
  status?: SubscriptionStatus;
  expires_at?: string;
  notes?: string;
}
