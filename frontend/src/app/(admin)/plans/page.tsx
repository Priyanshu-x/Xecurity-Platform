'use client';

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus, MoreHorizontal, Pencil, Archive, CheckSquare, Layers } from 'lucide-react';
import { toast } from 'sonner';

import { planService } from '@/features/plans/planService';
import { Plan, PlanCreate, PlanUpdate, PlanTier, PlanStatus } from '@/features/plans/types';
import { PlanForm } from '@/features/plans/components/PlanForm';
import { PlanCapabilities } from '@/features/plans/components/PlanCapabilities';

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
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';

export default function PlansPage() {
  const queryClient = useQueryClient();
  
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [editingPlan, setEditingPlan] = useState<Plan | null>(null);
  const [archivingPlan, setArchivingPlan] = useState<Plan | null>(null);
  const [capabilitiesPlan, setCapabilitiesPlan] = useState<Plan | null>(null);

  const { data: plans, isLoading, isError } = useQuery({
    queryKey: ['plans'],
    queryFn: () => planService.getPlans(),
  });

  const createMutation = useMutation({
    mutationFn: (data: PlanCreate) => planService.createPlan(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['plans'] });
      setIsCreateOpen(false);
      toast.success('Plan created successfully');
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail?.message || 'Failed to create plan');
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: PlanUpdate }) => planService.updatePlan(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['plans'] });
      setEditingPlan(null);
      toast.success('Plan updated successfully');
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail?.message || 'Failed to update plan');
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => planService.updatePlan(id, { status: PlanStatus.DEPRECATED }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['plans'] });
      setArchivingPlan(null);
      toast.success('Plan archived successfully');
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail?.message || 'Failed to archive plan');
    },
  });

  const getTierColor = (tier: PlanTier) => {
    switch (tier) {
      case PlanTier.ENTERPRISE: return 'bg-purple-500/10 text-purple-500 border-purple-500/20';
      case PlanTier.PROFESSIONAL: return 'bg-blue-500/10 text-blue-500 border-blue-500/20';
      case PlanTier.COMMUNITY: return 'bg-green-500/10 text-green-500 border-green-500/20';
      case PlanTier.GOVERNMENT: return 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20';
      default: return 'bg-gray-500/10 text-gray-500';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Plans</h1>
          <p className="text-muted-foreground">
            Create plans to bundle capabilities and set limits for your products.
          </p>
        </div>
        
        <Dialog open={isCreateOpen} onOpenChange={setIsCreateOpen}>
          <DialogTrigger render={<Button />}>
            <Plus className="w-4 h-4 mr-2" />
            Add Plan
          </DialogTrigger>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Create New Plan</DialogTitle>
              <DialogDescription>
                Define a new subscription plan for a product.
              </DialogDescription>
            </DialogHeader>
            <PlanForm 
              onSubmit={(data) => createMutation.mutate(data as PlanCreate)} 
              isSubmitting={createMutation.isPending}
            />
          </DialogContent>
        </Dialog>
      </div>

      <div className="border border-border/50 rounded-lg bg-card/50 backdrop-blur-sm overflow-hidden">
        <Table>
          <TableHeader className="bg-muted/50">
            <TableRow>
              <TableHead>Plan</TableHead>
              <TableHead>Tier</TableHead>
              <TableHead>Limits</TableHead>
              <TableHead>Status</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading && (
              Array.from({ length: 3 }).map((_, i) => (
                <TableRow key={i}>
                  <TableCell><Skeleton className="h-4 w-[200px]" /></TableCell>
                  <TableCell><Skeleton className="h-6 w-[100px] rounded-full" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-[150px]" /></TableCell>
                  <TableCell><Skeleton className="h-6 w-[80px] rounded-full" /></TableCell>
                  <TableCell className="text-right"><Skeleton className="h-8 w-8 ml-auto rounded-md" /></TableCell>
                </TableRow>
              ))
            )}
            
            {isError && (
              <TableRow>
                <TableCell colSpan={5} className="h-24 text-center text-destructive">
                  Failed to load plans. Please try again.
                </TableCell>
              </TableRow>
            )}

            {!isLoading && !isError && plans?.length === 0 && (
              <TableRow>
                <TableCell colSpan={5} className="h-48 text-center">
                  <div className="flex flex-col items-center justify-center text-muted-foreground">
                    <Layers className="w-12 h-12 mb-4 opacity-20" />
                    <p className="text-lg font-medium text-foreground">No plans found</p>
                    <p className="text-sm">Get started by creating your first subscription plan.</p>
                  </div>
                </TableCell>
              </TableRow>
            )}

            {!isLoading && !isError && plans?.map((plan) => (
              <TableRow key={plan.id}>
                <TableCell className="font-medium">
                  {plan.name}
                  {plan.description && (
                    <p className="text-xs text-muted-foreground mt-1 truncate max-w-xs">{plan.description}</p>
                  )}
                </TableCell>
                <TableCell>
                  <Badge variant="outline" className={getTierColor(plan.tier)}>
                    {plan.tier}
                  </Badge>
                </TableCell>
                <TableCell className="text-sm text-muted-foreground space-y-1">
                  <div>Users: {plan.max_users === null ? 'Unlimited' : plan.max_users}</div>
                  <div>Devices: {plan.max_devices === null ? 'Unlimited' : plan.max_devices}</div>
                </TableCell>
                <TableCell>
                  {plan.status === PlanStatus.ACTIVE ? (
                    <Badge variant="outline" className="bg-green-500/10 text-green-500 hover:bg-green-500/20">
                      Active
                    </Badge>
                  ) : (
                    <Badge variant="outline" className="bg-gray-500/10 text-gray-500 hover:bg-gray-500/20">
                      Deprecated
                    </Badge>
                  )}
                </TableCell>
                <TableCell className="text-right">
                  <DropdownMenu>
                    <DropdownMenuTrigger render={<Button variant="ghost" className="h-8 w-8 p-0" />}>
                      <span className="sr-only">Open menu</span>
                      <MoreHorizontal className="h-4 w-4" />
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuLabel>Actions</DropdownMenuLabel>
                      <DropdownMenuItem onClick={() => setCapabilitiesPlan(plan)}>
                        <CheckSquare className="w-4 h-4 mr-2" /> Assign Capabilities
                      </DropdownMenuItem>
                      <DropdownMenuItem onClick={() => setEditingPlan(plan)}>
                        <Pencil className="w-4 h-4 mr-2" /> Edit
                      </DropdownMenuItem>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem 
                        onClick={() => setArchivingPlan(plan)}
                        disabled={plan.status === PlanStatus.DEPRECATED}
                        className="text-destructive focus:bg-destructive focus:text-destructive-foreground"
                      >
                        <Archive className="w-4 h-4 mr-2" /> Archive
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
      <Dialog open={!!editingPlan} onOpenChange={(open) => !open && setEditingPlan(null)}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Edit Plan</DialogTitle>
            <DialogDescription>
              Make changes to {editingPlan?.name}.
            </DialogDescription>
          </DialogHeader>
          {editingPlan && (
            <PlanForm 
              initialData={editingPlan}
              onSubmit={(data) => updateMutation.mutate({ id: editingPlan.id, data })}
              isSubmitting={updateMutation.isPending}
            />
          )}
        </DialogContent>
      </Dialog>

      {/* Capabilities Assignment Dialog */}
      <Dialog open={!!capabilitiesPlan} onOpenChange={(open) => !open && setCapabilitiesPlan(null)}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>Assign Capabilities</DialogTitle>
            <DialogDescription>
              Select the features that are included in the {capabilitiesPlan?.name} plan.
            </DialogDescription>
          </DialogHeader>
          {capabilitiesPlan && (
            <PlanCapabilities plan={capabilitiesPlan} />
          )}
        </DialogContent>
      </Dialog>

      {/* Archive Confirmation Dialog */}
      <Dialog open={!!archivingPlan} onOpenChange={(open) => !open && setArchivingPlan(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Archive Plan</DialogTitle>
            <DialogDescription>
              Are you sure you want to archive 
              <span className="font-bold text-foreground"> {archivingPlan?.name}</span>? 
              This will prevent any new subscriptions to this plan.
            </DialogDescription>
          </DialogHeader>
          <div className="flex justify-end space-x-2 pt-4">
            <Button variant="outline" onClick={() => setArchivingPlan(null)}>
              Cancel
            </Button>
            <Button 
              variant="destructive" 
              onClick={() => archivingPlan && deleteMutation.mutate(archivingPlan.id)}
              disabled={deleteMutation.isPending}
            >
              {deleteMutation.isPending ? 'Archiving...' : 'Archive Plan'}
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
