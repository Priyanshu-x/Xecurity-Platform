'use client';

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus, MoreHorizontal, Pencil, Ban, CreditCard, ExternalLink } from 'lucide-react';
import { toast } from 'sonner';

import { subscriptionService } from '@/features/subscriptions/subscriptionService';
import { Subscription, SubscriptionCreate, SubscriptionUpdate, SubscriptionStatus } from '@/features/subscriptions/types';
import { SubscriptionForm } from '@/features/subscriptions/components/SubscriptionForm';

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

export default function SubscriptionsPage() {
  const queryClient = useQueryClient();
  
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [editingSubscription, setEditingSubscription] = useState<Subscription | null>(null);
  const [cancelingSubscription, setCancelingSubscription] = useState<Subscription | null>(null);

  const { data: subscriptions, isLoading, isError } = useQuery({
    queryKey: ['subscriptions'],
    queryFn: () => subscriptionService.getSubscriptions(),
  });

  const createMutation = useMutation({
    mutationFn: (data: SubscriptionCreate) => subscriptionService.createSubscription(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['subscriptions'] });
      setIsCreateOpen(false);
      toast.success('Subscription created successfully');
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail?.message || 'Failed to create subscription');
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: SubscriptionUpdate }) => subscriptionService.updateSubscription(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['subscriptions'] });
      setEditingSubscription(null);
      toast.success('Subscription updated successfully');
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail?.message || 'Failed to update subscription');
    },
  });

  const cancelMutation = useMutation({
    mutationFn: (id: string) => subscriptionService.cancelSubscription(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['subscriptions'] });
      setCancelingSubscription(null);
      toast.success('Subscription cancelled successfully');
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail?.message || 'Failed to cancel subscription');
    },
  });

  const getStatusColor = (status: SubscriptionStatus) => {
    switch (status) {
      case SubscriptionStatus.ACTIVE: return 'bg-green-500/10 text-green-500 hover:bg-green-500/20';
      case SubscriptionStatus.TRIAL: return 'bg-blue-500/10 text-blue-500 hover:bg-blue-500/20';
      case SubscriptionStatus.EXPIRED: return 'bg-yellow-500/10 text-yellow-500 hover:bg-yellow-500/20';
      case SubscriptionStatus.CANCELLED: return 'bg-gray-500/10 text-gray-500 hover:bg-gray-500/20';
      case SubscriptionStatus.SUSPENDED: return 'bg-red-500/10 text-red-500 hover:bg-red-500/20';
      default: return 'bg-gray-500/10 text-gray-500';
    }
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'Never';
    return new Date(dateString).toLocaleDateString('en-GB', {
      day: '2-digit', month: 'short', year: 'numeric'
    });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Subscriptions</h1>
          <p className="text-muted-foreground">
            Manage customer subscriptions, plans, and billing lifecycles.
          </p>
        </div>
        
        <Dialog open={isCreateOpen} onOpenChange={setIsCreateOpen}>
          <DialogTrigger asChild><Button>
            <Plus className="w-4 h-4 mr-2" />
            Add Subscription
          </Button></DialogTrigger>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Create New Subscription</DialogTitle>
              <DialogDescription>
                Assign a plan to an organization to begin their subscription.
              </DialogDescription>
            </DialogHeader>
            <SubscriptionForm 
              onSubmit={(data) => createMutation.mutate(data as SubscriptionCreate)} 
              isSubmitting={createMutation.isPending}
            />
          </DialogContent>
        </Dialog>
      </div>

      <div className="border border-border/50 rounded-lg bg-card/50 backdrop-blur-sm overflow-hidden">
        <Table>
          <TableHeader className="bg-muted/50">
            <TableRow>
              <TableHead>Customer & Plan</TableHead>
              <TableHead>Lifecycle</TableHead>
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
                  <TableCell><Skeleton className="h-6 w-[80px] rounded-full" /></TableCell>
                  <TableCell className="text-right"><Skeleton className="h-8 w-8 ml-auto rounded-md" /></TableCell>
                </TableRow>
              ))
            )}
            
            {isError && (
              <TableRow>
                <TableCell colSpan={4} className="h-24 text-center text-destructive">
                  Failed to load subscriptions. Please try again.
                </TableCell>
              </TableRow>
            )}

            {!isLoading && !isError && subscriptions?.length === 0 && (
              <TableRow>
                <TableCell colSpan={4} className="h-48 text-center">
                  <div className="flex flex-col items-center justify-center text-muted-foreground">
                    <CreditCard className="w-12 h-12 mb-4 opacity-20" />
                    <p className="text-lg font-medium text-foreground">No subscriptions found</p>
                    <p className="text-sm">Start by subscribing an organization to a plan.</p>
                  </div>
                </TableCell>
              </TableRow>
            )}

            {!isLoading && !isError && subscriptions?.map((sub) => (
              <TableRow key={sub.id}>
                <TableCell>
                  <div className="font-semibold text-base">{sub.organization?.name || 'Unknown Organization'}</div>
                  <div className="text-sm text-muted-foreground mt-0.5">{sub.product_plan?.name || 'Unknown Plan'}</div>
                </TableCell>
                <TableCell className="text-sm text-muted-foreground">
                  <div>Started {formatDate(sub.starts_at)}</div>
                  <div>Expires {formatDate(sub.expires_at)}</div>
                </TableCell>
                <TableCell>
                  <Badge variant="outline" className={getStatusColor(sub.status)}>
                    {sub.status}
                  </Badge>
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
                        <Link href={`/subscriptions/${sub.id}`}>
                          <ExternalLink className="w-4 h-4 mr-2" /> View Details
                        </Link>
                      </DropdownMenuItem>
                      <DropdownMenuItem onClick={() => setEditingSubscription(sub)}>
                        <Pencil className="w-4 h-4 mr-2" /> Edit Status
                      </DropdownMenuItem>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem 
                        onClick={() => setCancelingSubscription(sub)}
                        disabled={sub.status === SubscriptionStatus.CANCELLED}
                        className="text-destructive focus:bg-destructive focus:text-destructive-foreground"
                      >
                        <Ban className="w-4 h-4 mr-2" /> Cancel Subscription
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
      <Dialog open={!!editingSubscription} onOpenChange={(open) => !open && setEditingSubscription(null)}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Edit Subscription</DialogTitle>
            <DialogDescription>
              Update the subscription details.
            </DialogDescription>
          </DialogHeader>
          {editingSubscription && (
            <SubscriptionForm 
              initialData={editingSubscription}
              onSubmit={(data) => updateMutation.mutate({ id: editingSubscription.id, data })}
              isSubmitting={updateMutation.isPending}
            />
          )}
        </DialogContent>
      </Dialog>

      {/* Cancel Confirmation Dialog */}
      <Dialog open={!!cancelingSubscription} onOpenChange={(open) => !open && setCancelingSubscription(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Cancel Subscription</DialogTitle>
            <DialogDescription>
              Are you sure you want to cancel the subscription for 
              <span className="font-bold text-foreground"> {cancelingSubscription?.organization?.name}</span>? 
              This will immediately revoke their access.
            </DialogDescription>
          </DialogHeader>
          <div className="flex justify-end space-x-2 pt-4">
            <Button variant="outline" onClick={() => setCancelingSubscription(null)}>
              Keep Active
            </Button>
            <Button 
              variant="destructive" 
              onClick={() => cancelingSubscription && cancelMutation.mutate(cancelingSubscription.id)}
              disabled={cancelMutation.isPending}
            >
              {cancelMutation.isPending ? 'Canceling...' : 'Cancel Subscription'}
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
