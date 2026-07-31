import React from 'react';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';

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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';

import { ReleaseChannel, ReleaseCreate } from '../types';

const releaseSchema = z.object({
  product_id: z.string().min(1, 'Product is required'),
  version: z.string().min(1, 'Version is required'),
  build_number: z.coerce.number().min(1, 'Build number must be greater than 0'),
  channel: z.nativeEnum(ReleaseChannel),
  mandatory: z.boolean().default(false),
});

type ReleaseFormValues = z.infer<typeof releaseSchema>;

interface ReleaseFormProps {
  products: { id: string; name: string }[];
  onSubmit: (data: ReleaseCreate) => void;
  isSubmitting?: boolean;
}

export function ReleaseForm({ products, onSubmit, isSubmitting }: ReleaseFormProps) {
  const form = useForm<ReleaseFormValues>({
    resolver: zodResolver(releaseSchema),
    defaultValues: {
      product_id: '',
      version: '',
      build_number: 1,
      channel: ReleaseChannel.STABLE,
      mandatory: false,
    },
  });

  const handleSubmit = (values: ReleaseFormValues) => {
    onSubmit({
      ...values,
      status: 'DRAFT' as any, // Simplified for now
      artifacts: [],
      is_latest: false,
    });
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-6">
        <FormField
          control={form.control}
          name="product_id"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Product</FormLabel>
              <Select onValueChange={field.onChange} defaultValue={field.value}>
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="Select a product" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  {products.map((p) => (
                    <SelectItem key={p.id} value={p.id}>
                      {p.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          )}
        />

        <div className="grid grid-cols-2 gap-4">
          <FormField
            control={form.control}
            name="version"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Version</FormLabel>
                <FormControl>
                  <Input placeholder="e.g. 1.0.0" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="build_number"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Build Number</FormLabel>
                <FormControl>
                  <Input type="number" placeholder="e.g. 1042" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>

        <FormField
          control={form.control}
          name="channel"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Channel</FormLabel>
              <Select onValueChange={field.onChange} defaultValue={field.value}>
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="Select channel" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  {Object.values(ReleaseChannel).map((channel) => (
                    <SelectItem key={channel} value={channel}>
                      {channel}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="mandatory"
          render={({ field }) => (
            <FormItem className="flex flex-row items-start space-x-3 space-y-0 rounded-md border p-4">
              <FormControl>
                <Switch
                  checked={field.value}
                  onCheckedChange={field.onChange}
                />
              </FormControl>
              <div className="space-y-1 leading-none">
                <FormLabel>
                  Mandatory Update
                </FormLabel>
                <FormDescription>
                  Require clients to install this update.
                </FormDescription>
              </div>
            </FormItem>
          )}
        />

        <Button type="submit" className="w-full" disabled={isSubmitting}>
          {isSubmitting ? 'Creating...' : 'Create Release'}
        </Button>
      </form>
    </Form>
  );
}
