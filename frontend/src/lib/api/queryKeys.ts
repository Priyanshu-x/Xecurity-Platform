export const createEntityKeys = (entity: string) => ({
  all: () => [entity] as const,
  lists: () => [...createEntityKeys(entity).all(), 'list'] as const,
  list: (filters: Record<string, any> = {}) => [...createEntityKeys(entity).lists(), filters] as const,
  details: () => [...createEntityKeys(entity).all(), 'detail'] as const,
  detail: (id: string) => [...createEntityKeys(entity).details(), id] as const,
});

export const queryKeys = {
  products: createEntityKeys('products'),
  capabilities: createEntityKeys('capabilities'),
  plans: createEntityKeys('plans'),
  organizations: createEntityKeys('organizations'),
  subscriptions: createEntityKeys('subscriptions'),
  deployments: createEntityKeys('deployments'),
  licenses: createEntityKeys('licenses'),
  releases: createEntityKeys('releases'),
  devices: createEntityKeys('devices'),
  activationRequests: createEntityKeys('activation-requests'),
};
