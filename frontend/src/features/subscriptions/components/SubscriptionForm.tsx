'use client';

import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Check, ChevronsUpDown } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';

import { cn } from '@/lib/utils';
import { SubscriptionCreate, Subscription, SubscriptionStatus } from '../types';
import { organizationService } from '@/features/organizations/organizationService';
import { planService } from '@/features/plans/planService';

import { Button } from '@/components/ui/button';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
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

const subscriptionSchema = z.object({
  organization_id: z.string().min(1, 'Organization is required'),
  product_plan_id: z.string().min(1, 'Plan is required'),
  status: z.nativeEnum(SubscriptionStatus).optional(),
  starts_at: z.string().optional(),
  expires_at: z.string().optional(),
  notes: z.string().optional(),
});

export type SubscriptionFormValues = z.infer<typeof subscriptionSchema>;

interface SubscriptionFormProps {
  initialData?: Subscription;
  onSubmit: (data: SubscriptionFormValues) => void;
  isSubmitting?: boolean;
}

export function SubscriptionForm({ initialData, onSubmit, isSubmitting = false }: SubscriptionFormProps) {
  const [openOrg, setOpenOrg] = useState(false);
  const [openPlan, setOpenPlan] = useState(false);

  // Parallel fetching as requested
  const { data: organizations, isLoading: isLoadingOrgs } = useQuery({
    queryKey: ['organizations'],
    queryFn: () => organizationService.getOrganizations(),
  });

  const { data: plans, isLoading: isLoadingPlans } = useQuery({
    queryKey: ['plans'],
    queryFn: () => planService.getPlans(),
  });

  const form = useForm<SubscriptionFormValues>({
    resolver: zodResolver(subscriptionSchema),
    defaultValues: {
      organization_id: initialData?.organization_id || '',
      product_plan_id: initialData?.product_plan_id || '',
      status: initialData?.status || SubscriptionStatus.ACTIVE,
      starts_at: initialData?.starts_at ? new Date(initialData.starts_at).toISOString().slice(0, 16) : '',
      expires_at: initialData?.expires_at ? new Date(initialData.expires_at).toISOString().slice(0, 16) : '',
      notes: initialData?.notes || '',
    },
  });

  const handleSubmit = (data: SubscriptionFormValues) => {
    const cleanedData = { ...data };
    if (!cleanedData.starts_at) delete cleanedData.starts_at;
    if (!cleanedData.expires_at) delete cleanedData.expires_at;
    if (cleanedData.notes === '') delete cleanedData.notes;
    
    // Convert datetime-local string to ISO format if provided
    if (cleanedData.starts_at) {
      cleanedData.starts_at = new Date(cleanedData.starts_at).toISOString();
    }
    if (cleanedData.expires_at) {
      cleanedData.expires_at = new Date(cleanedData.expires_at).toISOString();
    }

    onSubmit(cleanedData);
  };

  const isEditing = !!initialData;

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4">
        
        <div className="grid grid-cols-2 gap-4">
          {/* Organization Combobox */}
          <FormField
            control={form.control}
            name="organization_id"
            render={({ field }) => (
              <FormItem className="flex flex-col">
                <FormLabel>Organization</FormLabel>
                <Popover open={openOrg} onOpenChange={setOpenOrg}>
                  <PopoverTrigger asChild>
                    <FormControl>
                      <Button
                        variant="outline"
                        role="combobox"
                        aria-expanded={openOrg}
                        className={cn(
                          "justify-between w-full font-normal",
                          !field.value && "text-muted-foreground"
                        )}
                        disabled={isEditing || isLoadingOrgs}
                      >
                        {field.value
                          ? organizations?.find((org) => org.id === field.value)?.name
                          : isLoadingOrgs ? "Loading..." : "Select organization"}
                        <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
                      </Button>
                    </FormControl>
                  </PopoverTrigger>
                  <PopoverContent className="w-full p-0">
                    <Command>
                      <CommandInput placeholder="Search organization..." />
                      <CommandList>
                        <CommandEmpty>No organization found.</CommandEmpty>
                        <CommandGroup>
                          {organizations?.map((org) => (
                            <CommandItem
                              key={org.id}
                              value={org.name}
                              onSelect={() => {
                                form.setValue("organization_id", org.id);
                                setOpenOrg(false);
                              }}
                            >
                              <Check
                                className={cn(
                                  "mr-2 h-4 w-4",
                                  org.id === field.value ? "opacity-100" : "opacity-0"
                                )}
                              />
                              {org.name}
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

          {/* Plan Combobox */}
          <FormField
            control={form.control}
            name="product_plan_id"
            render={({ field }) => (
              <FormItem className="flex flex-col">
                <FormLabel>Plan</FormLabel>
                <Popover open={openPlan} onOpenChange={setOpenPlan}>
                  <PopoverTrigger asChild>
                    <FormControl>
                      <Button
                        variant="outline"
                        role="combobox"
                        aria-expanded={openPlan}
                        className={cn(
                          "justify-between w-full font-normal",
                          !field.value && "text-muted-foreground"
                        )}
                        disabled={isEditing || isLoadingPlans}
                      >
                        {field.value
                          ? plans?.find((plan) => plan.id === field.value)?.name
                          : isLoadingPlans ? "Loading..." : "Select plan"}
                        <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
                      </Button>
                    </FormControl>
                  </PopoverTrigger>
                  <PopoverContent className="w-full p-0">
                    <Command>
                      <CommandInput placeholder="Search plan..." />
                      <CommandList>
                        <CommandEmpty>No plan found.</CommandEmpty>
                        <CommandGroup>
                          {plans?.map((plan) => (
                            <CommandItem
                              key={plan.id}
                              value={plan.name}
                              onSelect={() => {
                                form.setValue("product_plan_id", plan.id);
                                setOpenPlan(false);
                              }}
                            >
                              <Check
                                className={cn(
                                  "mr-2 h-4 w-4",
                                  plan.id === field.value ? "opacity-100" : "opacity-0"
                                )}
                              />
                              {plan.name}
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
        </div>

        {isEditing && (
          <FormField
            control={form.control}
            name="status"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Status</FormLabel>
                <Select onValueChange={field.onChange} defaultValue={field.value}>
                  <FormControl>
                    <SelectTrigger>
                      <SelectValue placeholder="Select a status" />
                    </SelectTrigger>
                  </FormControl>
                  <SelectContent>
                    {Object.values(SubscriptionStatus).map((status) => (
                      <SelectItem key={status} value={status}>
                        {status}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <FormMessage />
              </FormItem>
            )}
          />
        )}

        <div className="grid grid-cols-2 gap-4">
          <FormField
            control={form.control}
            name="starts_at"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Start Date</FormLabel>
                <FormControl>
                  <Input type="datetime-local" {...field} disabled={isEditing} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="expires_at"
            render={({ field }) => (
              <FormItem>
                <FormLabel>End Date (Optional)</FormLabel>
                <FormControl>
                  <Input type="datetime-local" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>

        <FormField
          control={form.control}
          name="notes"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Notes (Optional)</FormLabel>
              <FormControl>
                <Textarea placeholder="Any manual notes for this subscription" className="resize-none" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <div className="flex justify-end pt-4">
          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Saving...' : initialData ? 'Update Subscription' : 'Create Subscription'}
          </Button>
        </div>
      </form>
    </Form>
  );
}
