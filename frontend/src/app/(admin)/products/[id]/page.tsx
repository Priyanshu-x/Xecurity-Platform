'use client';

import React from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { ArrowLeft, Package, Clock, Shield, Box, Zap, CreditCard } from 'lucide-react';

import { productService } from '@/features/products/productService';
import { ProductStatus } from '@/features/products/types';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

export default function ProductDetailsPage() {
  const params = useParams();
  const router = useRouter();
  const productId = params.id as string;

  const { data: product, isLoading, isError } = useQuery({
    queryKey: ['products', productId],
    queryFn: () => productService.getProduct(productId),
  });

  const getStatusColor = (status: ProductStatus) => {
    switch (status) {
      case ProductStatus.ACTIVE:
        return 'bg-green-500/10 text-green-500 hover:bg-green-500/20';
      case ProductStatus.BETA:
        return 'bg-blue-500/10 text-blue-500 hover:bg-blue-500/20';
      case ProductStatus.DEPRECATED:
        return 'bg-yellow-500/10 text-yellow-500 hover:bg-yellow-500/20';
      default:
        return 'bg-gray-500/10 text-gray-500 hover:bg-gray-500/20';
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-10 w-[200px]" />
        <Skeleton className="h-[200px] w-full" />
      </div>
    );
  }

  if (isError || !product) {
    return (
      <div className="flex flex-col items-center justify-center h-96 space-y-4">
        <div className="text-destructive font-medium">Failed to load product details</div>
        <Button variant="outline" onClick={() => router.push('/products')}>
          Go Back
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button variant="ghost" size="icon" onClick={() => router.push('/products')}>
            <ArrowLeft className="w-5 h-5" />
          </Button>
          <div>
            <div className="flex items-center space-x-3">
              <h1 className="text-3xl font-bold tracking-tight">{product.name}</h1>
              <Badge variant="outline" className={getStatusColor(product.status)}>
                {product.status}
              </Badge>
            </div>
            <p className="text-muted-foreground mt-1">
              {product.slug} {product.category && `• ${product.category}`}
            </p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <Button variant="outline">Settings</Button>
        </div>
      </div>

      {/* Info Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="bg-card/50 backdrop-blur-sm">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">About</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm">
              {product.description || <span className="italic text-muted-foreground">No description provided.</span>}
            </p>
          </CardContent>
        </Card>
        
        <Card className="bg-card/50 backdrop-blur-sm">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Links</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Website</span>
              {product.website ? <a href={product.website} target="_blank" rel="noreferrer" className="text-primary hover:underline">Link</a> : <span>—</span>}
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Repository</span>
              {product.repository_url ? <a href={product.repository_url} target="_blank" rel="noreferrer" className="text-primary hover:underline">Link</a> : <span>—</span>}
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Docs</span>
              {product.documentation_url ? <a href={product.documentation_url} target="_blank" rel="noreferrer" className="text-primary hover:underline">Link</a> : <span>—</span>}
            </div>
          </CardContent>
        </Card>

        <Card className="bg-card/50 backdrop-blur-sm">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Metadata</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-muted-foreground">ID</span>
              <span className="font-mono text-xs">{product.id.split('-')[0]}...</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Created</span>
              <span>{new Date(product.created_at).toLocaleDateString()}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Updated</span>
              <span>{product.updated_at ? new Date(product.updated_at).toLocaleDateString() : '—'}</span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Placeholders for Future Modules */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 pt-4">
        <Card className="border-dashed border-2 opacity-60">
          <CardHeader>
            <div className="w-10 h-10 rounded-lg bg-muted flex items-center justify-center mb-2">
              <Box className="w-5 h-5 text-muted-foreground" />
            </div>
            <CardTitle>Releases</CardTitle>
            <CardDescription>Manage versioned releases and artifacts.</CardDescription>
          </CardHeader>
          <CardContent>
            <Button variant="secondary" className="w-full" disabled>Coming Soon</Button>
          </CardContent>
        </Card>

        <Card className="border-dashed border-2 opacity-60">
          <CardHeader>
            <div className="w-10 h-10 rounded-lg bg-muted flex items-center justify-center mb-2">
              <Zap className="w-5 h-5 text-muted-foreground" />
            </div>
            <CardTitle>Capabilities</CardTitle>
            <CardDescription>Define RBAC permissions for this product.</CardDescription>
          </CardHeader>
          <CardContent>
            <Button variant="secondary" className="w-full" disabled>Coming Soon</Button>
          </CardContent>
        </Card>

        <Card className="border-dashed border-2 opacity-60">
          <CardHeader>
            <div className="w-10 h-10 rounded-lg bg-muted flex items-center justify-center mb-2">
              <CreditCard className="w-5 h-5 text-muted-foreground" />
            </div>
            <CardTitle>Plans</CardTitle>
            <CardDescription>Configure pricing and capability limits.</CardDescription>
          </CardHeader>
          <CardContent>
            <Button variant="secondary" className="w-full" disabled>Coming Soon</Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
