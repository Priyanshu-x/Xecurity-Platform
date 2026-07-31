import React from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';

export interface TabItem {
  name: string;
  icon: React.ElementType;
  current: boolean;
  isSoon?: boolean;
  onClick?: () => void;
}

interface EntityDetailsLayoutProps {
  title: string;
  subtitle?: string;
  breadcrumbs?: React.ReactNode;
  badges?: React.ReactNode;
  actions?: React.ReactNode;
  tabs: TabItem[];
  children: React.ReactNode;
  sidebar?: React.ReactNode;
  onBack?: () => void;
}

export function EntityDetailsLayout({
  title,
  subtitle,
  breadcrumbs,
  badges,
  actions,
  tabs,
  children,
  sidebar,
  onBack,
}: EntityDetailsLayoutProps) {
  const router = useRouter();
  
  const handleBack = () => {
    if (onBack) {
      onBack();
    } else {
      router.back();
    }
  };

  return (
    <div className="space-y-6">
      {breadcrumbs && (
        <div className="mb-2">
          {breadcrumbs}
        </div>
      )}
      
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button variant="ghost" size="icon" onClick={handleBack}>
            <ArrowLeft className="w-5 h-5" />
          </Button>
          <div>
            <div className="flex items-center space-x-3">
              <h1 className="text-3xl font-bold tracking-tight">{title}</h1>
              {badges}
            </div>
            {subtitle && (
              <p className="text-muted-foreground mt-1 text-lg">
                {subtitle}
              </p>
            )}
          </div>
        </div>
        
        {actions && (
          <div className="flex items-center space-x-2">
            {actions}
          </div>
        )}
      </div>

      <div className="border-b border-border">
        <nav className="-mb-px flex space-x-8 overflow-x-auto" aria-label="Tabs">
          {tabs.map((tab) => (
            <button
              key={tab.name}
              onClick={tab.onClick}
              disabled={tab.isSoon}
              className={`
                whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center
                ${tab.current
                  ? 'border-primary text-primary'
                  : 'border-transparent text-muted-foreground hover:text-foreground hover:border-border'
                }
                ${tab.isSoon ? 'cursor-not-allowed opacity-70' : 'cursor-pointer'}
              `}
            >
              <tab.icon className={`mr-2 h-4 w-4 ${tab.current ? 'text-primary' : 'text-muted-foreground'}`} />
              {tab.name}
              {tab.isSoon && (
                <span className="ml-2 bg-muted text-muted-foreground text-xs py-0.5 px-2 rounded-full">
                  Soon
                </span>
              )}
            </button>
          ))}
        </nav>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 pt-4">
        <div className="lg:col-span-2 space-y-6">
          {children}
        </div>

        {sidebar && (
          <div className="lg:col-span-1 space-y-6">
            {sidebar}
          </div>
        )}
      </div>
    </div>
  );
}
