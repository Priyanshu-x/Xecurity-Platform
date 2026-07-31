export enum ProductStatus {
  BETA = 'BETA',
  ACTIVE = 'ACTIVE',
  DEPRECATED = 'DEPRECATED',
}

export interface Product {
  id: string;
  name: string;
  slug: string;
  short_name?: string;
  description?: string;
  icon?: string;
  category?: string;
  website?: string;
  repository_url?: string;
  documentation_url?: string;
  status: ProductStatus;
  current_stable_release_id?: string;
  latest_release_id?: string;
  is_deleted: boolean;
  created_at: string;
  updated_at?: string;
}

export interface ProductCreate {
  name: string;
  slug: string;
  short_name?: string;
  description?: string;
  icon?: string;
  category?: string;
  website?: string;
  repository_url?: string;
  documentation_url?: string;
  status: ProductStatus;
}

export type ProductUpdate = Partial<ProductCreate>;
