'use client';

import React, { useState } from 'react';
import { Plus, MoreHorizontal, Pencil, ServerOff, Server, ExternalLink } from 'lucide-react';
import { toast } from 'sonner';

import { useDeployments } from '@/features/deployments/hooks/useDeployments';
import { useCreateDeployment } from '@/features/deployments/hooks/useCreateDeployment';
import { useUpdateDeployment } from '@/features/deployments/hooks/useUpdateDeployment';
import { useArchiveDeployment } from '@/features/deployments/hooks/useArchiveDeployment';
import { Deployment, DeploymentCreate, DeploymentUpdate, DeploymentStatus, DeploymentEnvironment } from '@/features/deployments/types';
import { DeploymentForm } from '@/features/deployments/components/DeploymentForm';

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
import { Skeleton } from '@/components/ui/skeleton';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import Link from 'next/link';

export default function DeploymentsPage() {
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [editingDeployment, setEditingDeployment] = useState<Deployment | null>(null);
  const [deletingDeployment, setDeletingDeployment] = useState<Deployment | null>(null);

  const { data: deployments, isLoading, isError } = useDeployments();

  const createMutation = useCreateDeployment({
    onSuccess: () => {
      setIsCreateOpen(false);
      toast.success('Deployment created successfully');
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail?.message || 'Failed to create deployment');
    },
  });

  const updateMutation = useUpdateDeployment({
    onSuccess: () => {
      setEditingDeployment(null);
      toast.success('Deployment updated successfully');
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail?.message || 'Failed to update deployment');
    },
  });

  const deleteMutation = useArchiveDeployment({
    onSuccess: () => {
      setDeletingDeployment(null);
      toast.success('Deployment archived successfully');
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail?.message || 'Failed to archive deployment');
    },
  });

  const getEnvBadge = (env: DeploymentEnvironment) => {
    switch (env) {
      case DeploymentEnvironment.PRODUCTION: return <Badge variant="outline" className="bg-green-500/10 text-green-500 hover:bg-green-500/20"><span className="mr-1">🟢</span> Production</Badge>;
      case DeploymentEnvironment.STAGING: return <Badge variant="outline" className="bg-yellow-500/10 text-yellow-500 hover:bg-yellow-500/20"><span className="mr-1">🟡</span> Staging</Badge>;
      case DeploymentEnvironment.DEVELOPMENT: return <Badge variant="outline" className="bg-slate-500/10 text-slate-500 hover:bg-slate-500/20"><span className="mr-1">⚪</span> Development</Badge>;
      default: return <Badge variant="outline">{env}</Badge>;
    }
  };

  const getStatusBadge = (status: DeploymentStatus) => {
    switch (status) {
      case DeploymentStatus.RUNNING: return <Badge variant="outline" className="bg-green-500/10 text-green-500 hover:bg-green-500/20 border-green-500/20">Running</Badge>;
      case DeploymentStatus.PROVISIONING: return <Badge variant="outline" className="bg-blue-500/10 text-blue-500 hover:bg-blue-500/20 border-blue-500/20">Provisioning</Badge>;
      case DeploymentStatus.DEGRADED: return <Badge variant="outline" className="bg-yellow-500/10 text-yellow-500 hover:bg-yellow-500/20 border-yellow-500/20">Degraded</Badge>;
      case DeploymentStatus.STOPPED: return <Badge variant="outline" className="bg-orange-500/10 text-orange-500 hover:bg-orange-500/20 border-orange-500/20">Stopped</Badge>;
      case DeploymentStatus.OFFLINE: return <Badge variant="outline" className="bg-red-500/10 text-red-500 hover:bg-red-500/20 border-red-500/20">Offline</Badge>;
      case DeploymentStatus.DECOMMISSIONED: return <Badge variant="outline" className="bg-slate-500/10 text-slate-500 hover:bg-slate-500/20 border-slate-500/20">Decommissioned</Badge>;
      default: return <Badge variant="outline">{status}</Badge>;
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Deployments</h1>
          <p className="text-muted-foreground">
            Manage instances, environments, and track software versions.
          </p>
        </div>
        
        <Dialog open={isCreateOpen} onOpenChange={setIsCreateOpen}>
          <DialogTrigger render={<Button />}>
            <Plus className="w-4 h-4 mr-2" />
            Add Deployment
          </DialogTrigger>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Create New Deployment</DialogTitle>
              <DialogDescription>
                Register a new deployment instance for a customer.
              </DialogDescription>
            </DialogHeader>
            <DeploymentForm 
              onSubmit={(data) => createMutation.mutate(data as DeploymentCreate)} 
              isSubmitting={createMutation.isPending}
            />
          </DialogContent>
        </Dialog>
      </div>

      <div className="border border-border/50 rounded-lg bg-card/50 backdrop-blur-sm overflow-hidden">
        <Table>
          <TableHeader className="bg-muted/50">
            <TableRow>
              <TableHead>Deployment</TableHead>
              <TableHead>Customer & Product</TableHead>
              <TableHead>Environment</TableHead>
              <TableHead>Status</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading && (
              Array.from({ length: 3 }).map((_, i) => (
                <TableRow key={i}>
                  <TableCell>
                    <div className="space-y-2">
                      <Skeleton className="h-5 w-[150px]" />
                      <Skeleton className="h-4 w-[100px]" />
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="space-y-2">
                      <Skeleton className="h-4 w-[120px]" />
                      <Skeleton className="h-4 w-[120px]" />
                    </div>
                  </TableCell>
                  <TableCell><Skeleton className="h-6 w-[100px] rounded-full" /></TableCell>
                  <TableCell><Skeleton className="h-6 w-[80px] rounded-full" /></TableCell>
                  <TableCell className="text-right"><Skeleton className="h-8 w-8 ml-auto rounded-md" /></TableCell>
                </TableRow>
              ))
            )}
            
            {isError && (
              <TableRow>
                <TableCell colSpan={5} className="h-24 text-center text-destructive">
                  Failed to load deployments. Please try again.
                </TableCell>
              </TableRow>
            )}

            {!isLoading && !isError && deployments?.length === 0 && (
              <TableRow>
                <TableCell colSpan={5} className="h-48 text-center">
                  <div className="flex flex-col items-center justify-center text-muted-foreground">
                    <Server className="w-12 h-12 mb-4 opacity-20" />
                    <p className="text-lg font-medium text-foreground">No deployments found</p>
                    <p className="text-sm">Start by registering an instance.</p>
                  </div>
                </TableCell>
              </TableRow>
            )}

            {!isLoading && !isError && deployments?.map((deployment) => (
              <TableRow key={deployment.id}>
                <TableCell>
                  <div className="font-semibold text-base">{deployment.name}</div>
                  <div className="text-sm font-mono text-muted-foreground mt-0.5">
                    {deployment.current_release_version || 'No version recorded'}
                  </div>
                </TableCell>
                <TableCell>
                  <div className="font-medium">{deployment.organization?.name || 'Unknown Organization'}</div>
                  <div className="text-sm text-muted-foreground mt-0.5">{deployment.product?.name || 'Unknown Product'}</div>
                </TableCell>
                <TableCell>
                  {getEnvBadge(deployment.environment)}
                </TableCell>
                <TableCell>
                  {getStatusBadge(deployment.status)}
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
                        <Link href={`/deployments/${deployment.id}`}>
                          <ExternalLink className="w-4 h-4 mr-2" /> View Details
                        </Link>
                      </DropdownMenuItem>
                      <DropdownMenuItem onClick={() => setEditingDeployment(deployment)}>
                        <Pencil className="w-4 h-4 mr-2" /> Edit Deployment
                      </DropdownMenuItem>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem 
                        onClick={() => setDeletingDeployment(deployment)}
                        className="text-destructive focus:bg-destructive focus:text-destructive-foreground"
                      >
                        <ServerOff className="w-4 h-4 mr-2" /> Archive
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      {/* Edit Dialog */}
      <Dialog open={!!editingDeployment} onOpenChange={(open) => !open && setEditingDeployment(null)}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Edit Deployment</DialogTitle>
            <DialogDescription>
              Update the deployment environment, status, or name.
            </DialogDescription>
          </DialogHeader>
          {editingDeployment && (
            <DeploymentForm 
              initialData={editingDeployment}
              onSubmit={(data) => updateMutation.mutate({ id: editingDeployment.id, data })}
              isSubmitting={updateMutation.isPending}
            />
          )}
        </DialogContent>
      </Dialog>

      {/* Archive Confirmation Dialog */}
      <Dialog open={!!deletingDeployment} onOpenChange={(open) => !open && setDeletingDeployment(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Archive Deployment</DialogTitle>
            <DialogDescription>
              Are you sure you want to archive 
              <span className="font-bold text-foreground"> {deletingDeployment?.name}</span>? 
              This will decommission the instance and hide it from active views.
            </DialogDescription>
          </DialogHeader>
          <div className="flex justify-end space-x-2 pt-4">
            <Button variant="outline" onClick={() => setDeletingDeployment(null)}>
              Cancel
            </Button>
            <Button 
              variant="destructive" 
              onClick={() => deletingDeployment && deleteMutation.mutate(deletingDeployment.id)}
              disabled={deleteMutation.isPending}
            >
              {deleteMutation.isPending ? 'Archiving...' : 'Archive Deployment'}
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
