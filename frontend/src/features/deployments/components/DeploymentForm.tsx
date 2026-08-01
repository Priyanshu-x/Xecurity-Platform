'use client';

import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Check, ChevronsUpDown } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';

import { cn } from '@/lib/utils';
import { DeploymentCreate, Deployment, DeploymentEnvironment, DeploymentStatus } from '../types';
import { organizationService } from '@/features/organizations/organizationService';
import { productService } from '@/features/products/productService';

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

const deploymentSchema = z.object({
  name: z.string().min(2, 'Name is required'),
  organization_id: z.string().min(1, 'Organization is required'),
  product_id: z.string().min(1, 'Product is required'),
  environment: z.nativeEnum(DeploymentEnvironment).optional(),
  status: z.nativeEnum(DeploymentStatus).optional(),
});

export type DeploymentFormValues = z.infer<typeof deploymentSchema>;

interface DeploymentFormProps {
  initialData?: Deployment;
  onSubmit: (data: DeploymentFormValues) => void;
  isSubmitting?: boolean;
}

export function DeploymentForm({ initialData, onSubmit, isSubmitting = false }: DeploymentFormProps) {
  const [openOrg, setOpenOrg] = useState(false);
  const [openProduct, setOpenProduct] = useState(false);

  // Parallel fetching as requested
  const { data: organizations, isLoading: isLoadingOrgs } = useQuery({
    queryKey: ['organizations'],
    queryFn: () => organizationService.getOrganizations(),
  });

  const { data: products, isLoading: isLoadingProducts } = useQuery({
    queryKey: ['products'],
    queryFn: () => productService.getProducts(),
  });

  const form = useForm<DeploymentFormValues>({
    resolver: zodResolver(deploymentSchema),
    defaultValues: {
      name: initialData?.name || '',
      organization_id: initialData?.organization_id || '',
      product_id: initialData?.product_id || '',
      environment: initialData?.environment || DeploymentEnvironment.PRODUCTION,
      status: initialData?.status || DeploymentStatus.PROVISIONING,
    },
  });

  const isEditing = !!initialData;

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        
        <FormField
          control={form.control}
          name="name"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Deployment Name</FormLabel>
              <FormControl>
                <Input placeholder="e.g. Production US-East" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <div className="grid grid-cols-2 gap-4">
          {/* Organization Combobox */}
          <FormField
            control={form.control}
            name="organization_id"
            render={({ field }) => (
              <FormItem className="flex flex-col mt-2">
                <FormLabel className="mb-2">Organization</FormLabel>
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

          {/* Product Combobox */}
          <FormField
            control={form.control}
            name="product_id"
            render={({ field }) => (
              <FormItem className="flex flex-col mt-2">
                <FormLabel className="mb-2">Product</FormLabel>
                <Popover open={openProduct} onOpenChange={setOpenProduct}>
                  <PopoverTrigger asChild>
                    <FormControl>
                      <Button
                        variant="outline"
                        role="combobox"
                        aria-expanded={openProduct}
                        className={cn(
                          "justify-between w-full font-normal",
                          !field.value && "text-muted-foreground"
                        )}
                        disabled={isEditing || isLoadingProducts}
                      >
                        {field.value
                          ? products?.find((p) => p.id === field.value)?.name
                          : isLoadingProducts ? "Loading..." : "Select product"}
                        <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
                      </Button>
                    </FormControl>
                  </PopoverTrigger>
                  <PopoverContent className="w-full p-0">
                    <Command>
                      <CommandInput placeholder="Search product..." />
                      <CommandList>
                        <CommandEmpty>No product found.</CommandEmpty>
                        <CommandGroup>
                          {products?.map((p) => (
                            <CommandItem
                              key={p.id}
                              value={p.name}
                              onSelect={() => {
                                form.setValue("product_id", p.id);
                                setOpenProduct(false);
                              }}
                            >
                              <Check
                                className={cn(
                                  "mr-2 h-4 w-4",
                                  p.id === field.value ? "opacity-100" : "opacity-0"
                                )}
                              />
                              {p.name}
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

        <div className="grid grid-cols-2 gap-4">
          <FormField
            control={form.control}
            name="environment"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Environment</FormLabel>
                <Select onValueChange={field.onChange} value={field.value}>
                  <FormControl>
                    <SelectTrigger>
                      <SelectValue placeholder="Select environment" />
                    </SelectTrigger>
                  </FormControl>
                  <SelectContent>
                    {Object.values(DeploymentEnvironment).map((env) => (
                      <SelectItem key={env} value={env}>
                        {env}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <FormMessage />
              </FormItem>
            )}
          />

          {isEditing && (
            <FormField
              control={form.control}
              name="status"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Status</FormLabel>
                  <Select onValueChange={field.onChange} value={field.value}>
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select status" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      {Object.values(DeploymentStatus).map((status) => (
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
        </div>

        <div className="flex justify-end pt-4">
          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Saving...' : initialData ? 'Update Deployment' : 'Create Deployment'}
          </Button>
        </div>
      </form>
    </Form>
  );
}
