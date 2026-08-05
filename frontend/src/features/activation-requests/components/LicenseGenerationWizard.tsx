import { useState } from 'react';
import { useGenerateLicenseRequest } from '../hooks/useGenerateLicenseRequest';
import { useQuery } from '@tanstack/react-query';
import { queryKeys } from '@/lib/api/queryKeys';
import { api } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';

export function LicenseGenerationWizard({ requestId, onClose }: { requestId: string, onClose: () => void }) {
  const [step, setStep] = useState(1);
  const [orgId, setOrgId] = useState('');
  const [productId, setProductId] = useState('');
  const [planId, setPlanId] = useState('');
  const [licenseType, setLicenseType] = useState('SUBSCRIPTION');
  const [validity, setValidity] = useState<number | undefined>(12);
  
  const generateMutation = useGenerateLicenseRequest(requestId);
  
  // Mock fetching for simplicity
  const { data: orgs } = useQuery({ queryKey: queryKeys.organizations.all(), queryFn: () => api.get('/organizations/').then(r => r.data) });
  const { data: products } = useQuery({ queryKey: queryKeys.products.all(), queryFn: () => api.get('/products/').then(r => r.data) });
  const { data: plans } = useQuery({ queryKey: queryKeys.plans.all(), queryFn: () => api.get('/plans').then(r => r.data) });

  const handleGenerate = async () => {
    if (!orgId || !productId) return;
    
    try {
      await generateMutation.mutateAsync({
        organization_id: orgId,
        product_id: productId,
        plan_id: planId || undefined,
        license_type: licenseType,
        validity_months: validity
      });
      onClose();
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center">
      <Card className="w-full max-w-2xl p-6 shadow-lg border">
        <h2 className="text-2xl font-bold mb-4">License Generation Wizard</h2>
        
        {step === 1 && (
          <div className="space-y-4">
            <h3 className="text-lg font-medium">Step 1: Select Organization & Product</h3>
            <div className="space-y-2">
              <label className="text-sm font-medium">Organization</label>
              <select className="w-full p-2 border rounded-md bg-background text-foreground" value={orgId} onChange={e => setOrgId(e.target.value)}>
                <option value="">Select Organization</option>
                {orgs?.map((o: any) => <option key={o.id} value={o.id}>{o.name}</option>)}
              </select>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Product</label>
              <select className="w-full p-2 border rounded-md bg-background text-foreground" value={productId} onChange={e => setProductId(e.target.value)}>
                <option value="">Select Product</option>
                {products?.map((p: any) => <option key={p.id} value={p.id}>{p.name}</option>)}
              </select>
            </div>
            <div className="flex justify-end space-x-2 mt-6">
              <Button variant="outline" onClick={onClose}>Cancel</Button>
              <Button onClick={() => setStep(2)} disabled={!orgId || !productId}>Next</Button>
            </div>
          </div>
        )}

        {step === 2 && (
          <div className="space-y-4">
            <h3 className="text-lg font-medium">Step 2: License Details</h3>
            <div className="space-y-2">
              <label className="text-sm font-medium">License Type</label>
              <select className="w-full p-2 border rounded-md bg-background text-foreground" value={licenseType} onChange={e => setLicenseType(e.target.value)}>
                <option value="TRIAL">Trial</option>
                <option value="PROFESSIONAL">Professional</option>
                <option value="ENTERPRISE">Enterprise</option>
                <option value="LIFETIME">Lifetime</option>
                <option value="CUSTOM">Custom</option>
              </select>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Validity (Months)</label>
              <input type="number" className="w-full p-2 border rounded-md bg-background text-foreground" value={validity || ''} onChange={e => setValidity(Number(e.target.value) || undefined)} />
            </div>
            <div className="flex justify-end items-center space-x-2 mt-6">
              {generateMutation.isError && (
                <div className="text-destructive text-sm mr-auto font-medium">
                  Failed to generate license: {(generateMutation.error as any)?.response?.data?.detail || generateMutation.error?.message}
                </div>
              )}
              <Button variant="outline" onClick={() => setStep(1)}>Back</Button>
              <Button onClick={handleGenerate} disabled={generateMutation.isPending}>
                {generateMutation.isPending ? "Generating..." : "Generate License"}
              </Button>
            </div>
          </div>
        )}
      </Card>
    </div>
  );
}
