'use client';

import React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';

import { planService } from '../planService';
import { capabilityService } from '@/features/capabilities/capabilityService';
import { Plan } from '../types';
import { Switch } from '@/components/ui/switch';
import { Skeleton } from '@/components/ui/skeleton';

interface PlanCapabilitiesProps {
  plan: Plan;
}

export function PlanCapabilities({ plan }: PlanCapabilitiesProps) {
  const queryClient = useQueryClient();

  const { data: allCapabilities, isLoading: isLoadingCapabilities } = useQuery({
    queryKey: ['capabilities', 'product', plan.product_id],
    queryFn: () => capabilityService.getProductCapabilities(plan.product_id),
  });

  const { data: planData, isLoading: isLoadingPlan } = useQuery({
    queryKey: ['plans', plan.id],
    queryFn: () => planService.getPlan(plan.id),
    initialData: plan,
  });

  const assignMutation = useMutation({
    mutationFn: (capabilityId: string) => planService.assignCapability(plan.id, capabilityId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['plans'] });
      queryClient.invalidateQueries({ queryKey: ['plans', plan.id] });
      toast.success('Capability assigned successfully');
    },
    onError: () => toast.error('Failed to assign capability'),
  });

  const removeMutation = useMutation({
    mutationFn: (capabilityId: string) => planService.removeCapability(plan.id, capabilityId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['plans'] });
      queryClient.invalidateQueries({ queryKey: ['plans', plan.id] });
      toast.success('Capability removed successfully');
    },
    onError: () => toast.error('Failed to remove capability'),
  });

  if (isLoadingCapabilities || isLoadingPlan) {
    return (
      <div className="space-y-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="flex items-center justify-between p-4 border rounded-lg">
            <div className="space-y-2">
              <Skeleton className="h-4 w-[150px]" />
              <Skeleton className="h-3 w-[250px]" />
            </div>
            <Skeleton className="h-6 w-10 rounded-full" />
          </div>
        ))}
      </div>
    );
  }

  const assignedCapabilityIds = new Set(planData.capabilities?.map(c => c.id) || []);

  const handleToggle = (capabilityId: string, isAssigned: boolean) => {
    if (isAssigned) {
      removeMutation.mutate(capabilityId);
    } else {
      assignMutation.mutate(capabilityId);
    }
  };

  return (
    <div className="space-y-4 max-h-[60vh] overflow-y-auto pr-2">
      {allCapabilities?.map((capability) => {
        const isAssigned = assignedCapabilityIds.has(capability.id);
        const isLoading = assignMutation.isPending || removeMutation.isPending;

        return (
          <div 
            key={capability.id} 
            className={`flex items-center justify-between p-4 border rounded-lg transition-colors ${
              isAssigned ? 'bg-primary/5 border-primary/20' : 'bg-card'
            }`}
          >
            <div>
              <h4 className="font-medium text-sm">{capability.name}</h4>
              <p className="text-xs text-muted-foreground mt-1">
                {capability.description || capability.slug}
              </p>
            </div>
            <Switch 
              checked={isAssigned} 
              disabled={isLoading}
              onCheckedChange={() => handleToggle(capability.id, isAssigned)} 
            />
          </div>
        );
      })}

      {allCapabilities?.length === 0 && (
        <div className="text-center py-8 text-muted-foreground">
          No capabilities are linked to this Product yet. You must link capabilities to the product first.
        </div>
      )}
    </div>
  );
}
