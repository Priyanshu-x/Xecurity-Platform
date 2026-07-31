'use client';

import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Check, ChevronsUpDown } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';

import { cn } from '@/lib/utils';
import { LicenseIssue } from '../types';
import { subscriptionService } from '@/features/subscriptions/subscriptionService';
import { deploymentService } from '@/features/deployments/deploymentService';
import { queryKeys } from '@/lib/api/queryKeys';

import { Button } from '@/components/ui/button';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from '@/components/ui/command';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import { Textarea } from '@/components/ui/textarea';

const licenseIssueSchema = z.object({
  deployment_id: z.string().min(1, 'Deployment is required'),
  subscription_id: z.string().min(1, 'Subscription is required'),
  notes: z.string().optional(),
});

export type LicenseIssueFormValues = z.infer<typeof licenseIssueSchema>;

interface LicenseIssueFormProps {
  onSubmit: (deploymentId: string, data: LicenseIssue) => void;
  isSubmitting?: boolean;
}

export function LicenseIssueForm({ onSubmit, isSubmitting = false }: LicenseIssueFormProps) {
  const [openDeployment, setOpenDeployment] = useState(false);
  const [openSubscription, setOpenSubscription] = useState(false);

  const { data: deployments, isLoading: isLoadingDeployments } = useQuery({
    queryKey: queryKeys.deployments.all(),
    queryFn: () => deploymentService.getDeployments(),
  });

  const { data: subscriptions, isLoading: isLoadingSubscriptions } = useQuery({
    queryKey: queryKeys.subscriptions.all(),
    queryFn: () => subscriptionService.getSubscriptions(),
  });

  const form = useForm<LicenseIssueFormValues>({
    resolver: zodResolver(licenseIssueSchema),
    defaultValues: {
      deployment_id: '',
      subscription_id: '',
      notes: '',
    },
  });

  const handleSubmit = (values: LicenseIssueFormValues) => {
    onSubmit(values.deployment_id, {
      subscription_id: values.subscription_id,
      notes: values.notes,
    });
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4">
        
        {/* Deployment Combobox */}
        <FormField
          control={form.control}
          name="deployment_id"
          render={({ field }) => (
            <FormItem className="flex flex-col">
              <FormLabel className="mb-2">Target Deployment</FormLabel>
              <Popover open={openDeployment} onOpenChange={setOpenDeployment}>
                <PopoverTrigger asChild>
                  <FormControl>
                    <Button
                      variant="outline"
                      role="combobox"
                      aria-expanded={openDeployment}
                      className={cn(
                        "justify-between w-full font-normal",
                        !field.value && "text-muted-foreground"
                      )}
                      disabled={isLoadingDeployments}
                    >
                      {field.value
                        ? deployments?.find((d) => d.id === field.value)?.name
                        : isLoadingDeployments ? "Loading..." : "Select deployment"}
                      <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
                    </Button>
                  </FormControl>
                </PopoverTrigger>
                <PopoverContent className="w-full p-0">
                  <Command>
                    <CommandInput placeholder="Search deployment..." />
                    <CommandList>
                      <CommandEmpty>No deployment found.</CommandEmpty>
                      <CommandGroup>
                        {deployments?.map((d) => (
                          <CommandItem
                            key={d.id}
                            value={d.name}
                            onSelect={() => {
                              form.setValue("deployment_id", d.id);
                              setOpenDeployment(false);
                            }}
                          >
                            <Check
                              className={cn(
                                "mr-2 h-4 w-4",
                                d.id === field.value ? "opacity-100" : "opacity-0"
                              )}
                            />
                            {d.name}
                          </CommandItem>
                        ))}
                      </CommandGroup>
                    </CommandList>
                  </Command>
                </PopoverContent>
              </Popover>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Subscription Combobox */}
        <FormField
          control={form.control}
          name="subscription_id"
          render={({ field }) => (
            <FormItem className="flex flex-col">
              <FormLabel className="mb-2">Source Subscription</FormLabel>
              <Popover open={openSubscription} onOpenChange={setOpenSubscription}>
                <PopoverTrigger asChild>
                  <FormControl>
                    <Button
                      variant="outline"
                      role="combobox"
                      aria-expanded={openSubscription}
                      className={cn(
                        "justify-between w-full font-normal",
                        !field.value && "text-muted-foreground"
                      )}
                      disabled={isLoadingSubscriptions}
                    >
                      {field.value
                        ? (() => {
                            const sub = subscriptions?.find((s) => s.id === field.value);
                            return sub ? `${sub.organization?.name} - ${sub.product_plan?.name}` : 'Selected';
                          })()
                        : isLoadingSubscriptions ? "Loading..." : "Select subscription"}
                      <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
                    </Button>
                  </FormControl>
                </PopoverTrigger>
                <PopoverContent className="w-full p-0">
                  <Command>
                    <CommandInput placeholder="Search subscription..." />
                    <CommandList>
                      <CommandEmpty>No subscription found.</CommandEmpty>
                      <CommandGroup>
                        {subscriptions?.map((s) => (
                          <CommandItem
                            key={s.id}
                            value={`${s.organization?.name} ${s.product_plan?.name}`}
                            onSelect={() => {
                              form.setValue("subscription_id", s.id);
                              setOpenSubscription(false);
                            }}
                          >
                            <Check
                              className={cn(
                                "mr-2 h-4 w-4",
                                s.id === field.value ? "opacity-100" : "opacity-0"
                              )}
                            />
                            {s.organization?.name} - {s.product_plan?.name}
                          </CommandItem>
                        ))}
                      </CommandGroup>
                    </CommandList>
                  </Command>
                </PopoverContent>
              </Popover>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="notes"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Notes (Optional)</FormLabel>
              <FormControl>
                <Textarea placeholder="Any issuance notes..." {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <div className="flex justify-end pt-4">
          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Issuing...' : 'Issue License'}
          </Button>
        </div>
      </form>
    </Form>
  );
}
