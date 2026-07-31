'use client';

import React from 'react';
import { useParams } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { CreditCard, ShieldCheck, Key, FileText, Activity } from 'lucide-react';

import { subscriptionService } from '@/features/subscriptions/subscriptionService';
import { Badge } from '@/components/ui/badge';
import { SubscriptionStatus } from '@/features/subscriptions/types';
import { EntityDetailsLayout } from '@/components/layout/EntityDetailsLayout';

export default function SubscriptionDetailsPage() {
  const params = useParams();
  const id = params.id as string;

  const { data: subscription, isLoading, isError } = useQuery({
    queryKey: ['subscription', id],
    queryFn: () => subscriptionService.getSubscription(id),
  });

  if (isLoading) {
    return <div className="p-8 text-center text-muted-foreground animate-pulse">Loading subscription details...</div>;
  }

  if (isError || !subscription) {
    return <div className="p-8 text-center text-destructive">Failed to load subscription.</div>;
  }

  const getStatusColor = (status: SubscriptionStatus) => {
    switch (status) {
      case SubscriptionStatus.ACTIVE: return 'bg-green-500/10 text-green-500 border-green-500/20';
      case SubscriptionStatus.TRIAL: return 'bg-blue-500/10 text-blue-500 border-blue-500/20';
      case SubscriptionStatus.EXPIRED: return 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20';
      case SubscriptionStatus.CANCELLED: return 'bg-gray-500/10 text-gray-500 border-gray-500/20';
      case SubscriptionStatus.SUSPENDED: return 'bg-red-500/10 text-red-500 border-red-500/20';
      default: return 'bg-gray-500/10 text-gray-500';
    }
  };

  const tabs = [
    { name: 'Overview', icon: FileText, current: true },
    { name: 'Deployments', icon: ShieldCheck, current: false, isSoon: true },
    { name: 'Licenses', icon: Key, current: false, isSoon: true },
    { name: 'Billing', icon: CreditCard, current: false, isSoon: true },
    { name: 'Activity', icon: Activity, current: false, isSoon: true },
  ];

  return (
    <EntityDetailsLayout
      title={subscription.organization?.name || 'Unknown Organization'}
      subtitle={subscription.product_plan?.name || 'Unknown Plan'}
      badges={
        <Badge variant="outline" className={getStatusColor(subscription.status)}>
          {subscription.status}
        </Badge>
      }
      tabs={tabs}
      sidebar={
        <div className="border border-border/50 rounded-lg p-6 bg-card/50">
          <h3 className="text-lg font-medium mb-4">Plan Limits</h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Max Users</span>
              <span className="font-medium">{subscription.product_plan?.max_users || 'Unlimited'}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Max Devices</span>
              <span className="font-medium">{subscription.product_plan?.max_devices || 'Unlimited'}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Trial Days</span>
              <span className="font-medium">{subscription.product_plan?.trial_days || '0'}</span>
            </div>
          </div>
        </div>
      }
    >
      <div className="border border-border/50 rounded-lg p-6 bg-card/50">
        <h3 className="text-lg font-medium mb-4">Subscription Overview</h3>
        <div className="grid grid-cols-2 gap-6">
          <div>
            <p className="text-sm font-medium text-muted-foreground">Start Date</p>
            <p className="mt-1 text-base">
              {new Date(subscription.starts_at).toLocaleDateString('en-GB', {
                day: 'numeric', month: 'long', year: 'numeric',
              })}
            </p>
          </div>
          <div>
            <p className="text-sm font-medium text-muted-foreground">Expiration Date</p>
            <p className="mt-1 text-base">
              {subscription.expires_at 
                ? new Date(subscription.expires_at).toLocaleDateString('en-GB', {
                    day: 'numeric', month: 'long', year: 'numeric',
                  })
                : 'Never expires'
              }
            </p>
          </div>
        </div>
        
        {subscription.notes && (
          <div className="mt-6">
            <p className="text-sm font-medium text-muted-foreground">Notes</p>
            <p className="mt-1 text-base whitespace-pre-wrap">{subscription.notes}</p>
          </div>
        )}
      </div>
    </EntityDetailsLayout>
  );
}
