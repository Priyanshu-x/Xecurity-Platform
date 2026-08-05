import { Capability } from '../capabilities/types';

export enum PlanTier {
  COMMUNITY = 'COMMUNITY',
  PROFESSIONAL = 'PROFESSIONAL',
  ENTERPRISE = 'ENTERPRISE',
  GOVERNMENT = 'GOVERNMENT',
  CUSTOM = 'CUSTOM',
}

export enum PlanStatus {
  ACTIVE = 'ACTIVE',
  DEPRECATED = 'DEPRECATED',
}

export interface Plan {
  id: string;
  name: string;
  slug: string;
  description?: string;
  tier?: PlanTier;
  status: PlanStatus;
  product_id: string;
  max_devices?: number | null;
  max_users?: number | null;
  trial_days?: number;
  duration_months?: number | null;
  created_at: string;
  updated_at: string;
  capabilities?: Capability[];
}

export interface PlanCreate {
  name: string;
  slug: string;
  description?: string;
  tier?: PlanTier;
  status: PlanStatus;
  product_id: string;
  max_devices?: number | null;
  max_users?: number | null;
  trial_days?: number;
  duration_months?: number | null;
}

export type PlanUpdate = Partial<PlanCreate>;
