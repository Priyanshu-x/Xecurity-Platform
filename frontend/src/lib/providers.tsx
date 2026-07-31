'use client';

import { QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from '@/features/auth/authContext';
import { queryClient } from './react-query/queryClient';

export function Providers({ children }: { children: React.ReactNode }) {

  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>{children}</AuthProvider>
    </QueryClientProvider>
  );
}
