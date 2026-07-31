'use client';

import React, { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { CapabilityCreate, Capability } from '../types';
import { Button } from '@/components/ui/button';
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Switch } from '@/components/ui/switch';

const capabilitySchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  slug: z.string().min(2, 'Slug is required').regex(/^[a-z0-9-]+$/, 'Slug can only contain lowercase letters, numbers, and hyphens'),
  description: z.string().optional(),
  is_active: z.boolean().default(true),
});

export type CapabilityFormValues = z.infer<typeof capabilitySchema>;

interface CapabilityFormProps {
  initialData?: Capability;
  onSubmit: (data: CapabilityFormValues) => void;
  isSubmitting?: boolean;
}

export function CapabilityForm({ initialData, onSubmit, isSubmitting = false }: CapabilityFormProps) {
  const [isSlugManual, setIsSlugManual] = useState(!!initialData);

  const form = useForm<CapabilityFormValues>({
    resolver: zodResolver(capabilitySchema) as any,
    defaultValues: {
      name: initialData?.name || '',
      slug: initialData?.slug || '',
      description: initialData?.description || '',
      is_active: initialData?.is_active ?? true,
    },
  });

  const nameValue = form.watch('name');

  useEffect(() => {
    if (!isSlugManual && nameValue) {
      const generatedSlug = nameValue
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, '-')
        .replace(/(^-|-$)/g, '');
      
      form.setValue('slug', generatedSlug, { shouldValidate: true });
    }
  }, [nameValue, isSlugManual, form]);

  const handleSubmit = (data: CapabilityFormValues) => {
    // Clean empty strings to undefined
    const cleanedData = { ...data };
    if (cleanedData.description === '') {
      delete cleanedData.description;
    }
    onSubmit(cleanedData);
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(handleSubmit as any)} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <FormField
            control={form.control as any}
            name="name"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Name</FormLabel>
                <FormControl>
                  <Input placeholder="Read Audit Logs" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control as any}
            name="slug"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Slug</FormLabel>
                <FormControl>
                  <Input 
                    placeholder="audit-logs:read" 
                    {...field} 
                    onChange={(e) => {
                      setIsSlugManual(true);
                      field.onChange(e);
                    }}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>
        
        <FormField
          control={form.control as any}
          name="description"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Description</FormLabel>
              <FormControl>
                <Textarea placeholder="What does this capability allow a user to do?" className="resize-none" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control as any}
          name="is_active"
          render={({ field }) => (
            <FormItem className="flex flex-row items-center justify-between rounded-lg border border-border/50 bg-card/50 p-4 shadow-sm">
              <div className="space-y-0.5">
                <FormLabel className="text-base">Active Status</FormLabel>
                <FormDescription>
                  Determine if this capability is immediately enforceable.
                </FormDescription>
              </div>
              <FormControl>
                <Switch
                  checked={field.value}
                  onCheckedChange={field.onChange}
                />
              </FormControl>
            </FormItem>
          )}
        />

        <div className="flex justify-end pt-4">
          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Saving...' : initialData ? 'Update Capability' : 'Create Capability'}
          </Button>
        </div>
      </form>
    </Form>
  );
}
