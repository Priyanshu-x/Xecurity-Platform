'use client';

import React, { useState } from 'react';
import { Plus, MoreHorizontal, FileText, Download, CheckCircle, Package } from 'lucide-react';
import { toast } from 'sonner';

import { Release, ReleaseStatus } from '@/features/releases/types';
import { useReleases } from '@/features/releases/hooks/useReleases';
import { useCreateRelease } from '@/features/releases/hooks/useCreateRelease';
import { useQuery } from '@tanstack/react-query';
import { productService } from '@/features/products/productService';
import { ReleaseForm } from '@/features/releases/components/ReleaseForm';
import { useAuth } from '@/features/auth/authContext';

import { Button } from '@/components/ui/button';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Skeleton } from '@/components/ui/skeleton';
import { Badge } from '@/components/ui/badge';
import Link from 'next/link';

export default function ReleasesPage() {
  const { user } = useAuth();
  const canManage = user && ['OWNER', 'ADMIN'].includes(user.role);

  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const { data: releases, isLoading, isError } = useReleases();
  const { data: products } = useQuery({
    queryKey: ['products'],
    queryFn: () => productService.getProducts(),
  });
  
  const createMutation = useCreateRelease();

  const handleCreateRelease = (data: any) => {
    createMutation.mutate(data, {
      onSuccess: () => {
        setIsCreateOpen(false);
        toast.success('Release created successfully');
      },
      onError: (error: any) => {
        toast.error(error?.response?.data?.detail?.message || 'Failed to create release');
      }
    });
  };

  const getStatusBadge = (status: ReleaseStatus) => {
    switch (status) {
      case ReleaseStatus.PUBLISHED: return <Badge variant="outline" className="bg-green-500/10 text-green-500 border-green-500/20">Published</Badge>;
      case ReleaseStatus.RELEASE_CANDIDATE: return <Badge variant="outline" className="bg-blue-500/10 text-blue-500 border-blue-500/20">RC</Badge>;
      case ReleaseStatus.TESTING: return <Badge variant="outline" className="bg-yellow-500/10 text-yellow-500 border-yellow-500/20">Testing</Badge>;
      case ReleaseStatus.DRAFT: return <Badge variant="outline" className="bg-slate-500/10 text-slate-500 border-slate-500/20">Draft</Badge>;
      case ReleaseStatus.DEPRECATED: return <Badge variant="outline" className="bg-orange-500/10 text-orange-500 border-orange-500/20">Deprecated</Badge>;
      case ReleaseStatus.ARCHIVED: return <Badge variant="outline" className="bg-red-500/10 text-red-500 border-red-500/20">Archived</Badge>;
      default: return <Badge variant="outline">{status}</Badge>;
    }
  };

  const getProductName = (id: string) => {
    return products?.find(p => p.id === id)?.name || 'Unknown Product';
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Releases</h1>
          <p className="text-muted-foreground">
            Manage software versions, channels, and downloadable artifacts.
          </p>
        </div>
        
        {canManage && (
          <Dialog open={isCreateOpen} onOpenChange={setIsCreateOpen}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="w-4 h-4 mr-2" />
                Create Release
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Create New Release</DialogTitle>
                <DialogDescription>
                  Define the version and channel for this release. You can upload artifacts later.
                </DialogDescription>
              </DialogHeader>
              <ReleaseForm 
                products={products || []} 
                onSubmit={handleCreateRelease} 
                isSubmitting={createMutation.isPending} 
              />
            </DialogContent>
          </Dialog>
        )}
      </div>

      <div className="border border-border/50 rounded-lg bg-card/50 backdrop-blur-sm overflow-hidden">
        <Table>
          <TableHeader className="bg-muted/50">
            <TableRow>
              <TableHead>Version</TableHead>
              <TableHead>Product</TableHead>
              <TableHead>Channel</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Artifacts</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading && (
              Array.from({ length: 3 }).map((_, i) => (
                <TableRow key={i}>
                  <TableCell><Skeleton className="h-5 w-[100px]" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-[120px]" /></TableCell>
                  <TableCell><Skeleton className="h-5 w-[80px]" /></TableCell>
                  <TableCell><Skeleton className="h-6 w-[80px] rounded-full" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-[60px]" /></TableCell>
                  <TableCell className="text-right"><Skeleton className="h-8 w-8 ml-auto rounded-md" /></TableCell>
                </TableRow>
              ))
            )}
            
            {isError && (
              <TableRow>
                <TableCell colSpan={6} className="h-24 text-center text-destructive">
                  Failed to load releases. Please try again.
                </TableCell>
              </TableRow>
            )}

            {!isLoading && !isError && releases?.length === 0 && (
              <TableRow>
                <TableCell colSpan={6} className="h-48 text-center">
                  <div className="flex flex-col items-center justify-center text-muted-foreground">
                    <Package className="w-12 h-12 mb-4 opacity-20" />
                    <p className="text-lg font-medium text-foreground">No releases found</p>
                    <p className="text-sm">{canManage ? "Start by creating a new release." : "No releases have been published yet."}</p>
                  </div>
                </TableCell>
              </TableRow>
            )}

            {!isLoading && !isError && releases?.map((release) => (
              <TableRow key={release.id}>
                <TableCell>
                  <div className="font-mono text-sm font-medium">v{release.version}</div>
                  <div className="text-xs text-muted-foreground mt-0.5">
                    Build {release.build_number}
                    {release.is_latest && (
                      <span className="ml-2 text-green-500 inline-flex items-center">
                        <CheckCircle className="w-3 h-3 mr-1" /> Latest
                      </span>
                    )}
                  </div>
                </TableCell>
                <TableCell>
                  <div className="font-medium">{getProductName(release.product_id)}</div>
                </TableCell>
                <TableCell>
                  <Badge variant="secondary" className="font-mono text-xs">{release.channel}</Badge>
                </TableCell>
                <TableCell>
                  {getStatusBadge(release.status)}
                </TableCell>
                <TableCell>
                  <div className="flex items-center text-sm">
                    <Package className="w-4 h-4 mr-1 text-muted-foreground" />
                    {release.artifacts?.length || 0}
                  </div>
                </TableCell>
                <TableCell className="text-right">
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" className="h-8 w-8 p-0">
                        <span className="sr-only">Open menu</span>
                        <MoreHorizontal className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuLabel>Actions</DropdownMenuLabel>
                      <DropdownMenuItem asChild>
                        <Link href={`/releases/${release.id}`}>
                          <FileText className="w-4 h-4 mr-2" /> View Details
                        </Link>
                      </DropdownMenuItem>
                      <DropdownMenuSeparator />
                      {release.artifacts?.length > 0 && (
                        <DropdownMenuItem onClick={() => toast.info('Download functionality coming soon')}>
                          <Download className="w-4 h-4 mr-2" /> Download Artifacts
                        </DropdownMenuItem>
                      )}
                    </DropdownMenuContent>
                  </DropdownMenu>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
