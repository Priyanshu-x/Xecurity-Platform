export interface Capability {
  id: string;
  name: string;
  slug: string;
  description?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface CapabilityCreate {
  name: string;
  slug: string;
  description?: string;
  is_active?: boolean;
}

export type CapabilityUpdate = Partial<CapabilityCreate>;
