import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
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
import { UserRole, UserCreate, UserUpdate, User } from '../types';
import { Switch } from '@/components/ui/switch';

const userSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(6, 'Password must be at least 6 characters').optional().or(z.literal('')),
  role: z.nativeEnum(UserRole),
  is_active: z.boolean(),
});

type UserFormValues = z.infer<typeof userSchema>;

interface UserFormProps {
  initialData?: User;
  onSubmit: (data: UserCreate | UserUpdate) => void;
  isLoading?: boolean;
}

export function UserForm({ initialData, onSubmit, isLoading }: UserFormProps) {
  const isEditing = !!initialData;
  
  const form = useForm<UserFormValues>({
    resolver: zodResolver(userSchema),
    defaultValues: {
      email: initialData?.email || '',
      password: '',
      role: initialData?.role || UserRole.VIEWER,
      is_active: initialData?.is_active ?? true,
    },
  });

  const handleSubmit = (values: UserFormValues) => {
    if (isEditing) {
      // Editing
      const updateData: UserUpdate = {
        role: values.role,
        is_active: values.is_active,
      };
      if (values.password && values.password.length > 0) {
        updateData.password = values.password;
      }
      onSubmit(updateData);
    } else {
      // Creating
      if (!values.password) {
        form.setError('password', { message: 'Password is required for new users' });
        return;
      }
      const createData: UserCreate = {
        email: values.email,
        password: values.password,
        role: values.role,
        is_active: values.is_active,
      };
      onSubmit(createData);
    }
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4">
        <FormField
          control={form.control}
          name="email"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Email</FormLabel>
              <FormControl>
                <Input placeholder="user@example.com" {...field} disabled={isEditing} />
              </FormControl>
              <FormDescription>
                {isEditing ? "Email cannot be changed after creation." : "The user's login email."}
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="password"
          render={({ field }) => (
            <FormItem>
              <FormLabel>{isEditing ? 'New Password (Optional)' : 'Password'}</FormLabel>
              <FormControl>
                <Input type="password" placeholder="********" {...field} />
              </FormControl>
              <FormDescription>
                {isEditing ? "Leave blank to keep the current password." : "Set an initial password for the user."}
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="role"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Role</FormLabel>
              <Select onValueChange={field.onChange} value={field.value}>
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="Select a role" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  <SelectItem value={UserRole.VIEWER}>Viewer</SelectItem>
                  <SelectItem value={UserRole.SUPPORT}>Support</SelectItem>
                  <SelectItem value={UserRole.ADMIN}>Admin</SelectItem>
                  <SelectItem value={UserRole.OWNER}>Owner</SelectItem>
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="is_active"
          render={({ field }) => (
            <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4">
              <div className="space-y-0.5">
                <FormLabel className="text-base">Active Status</FormLabel>
                <FormDescription>
                  Whether the user can log in to the platform.
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
          <Button type="submit" disabled={isLoading}>
            {isLoading ? 'Saving...' : isEditing ? 'Save Changes' : 'Create User'}
          </Button>
        </div>
      </form>
    </Form>
  );
}
