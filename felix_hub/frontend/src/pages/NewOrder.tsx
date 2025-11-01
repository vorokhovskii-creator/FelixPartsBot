import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { toast } from 'sonner';
import api from '@/lib/api';
import CategorySelector from '@/components/mechanic/order-wizard/CategorySelector';
import PartsSelector from '@/components/mechanic/order-wizard/PartsSelector';
import VinInput from '@/components/mechanic/order-wizard/VinInput';
import OriginalitySelector from '@/components/mechanic/order-wizard/OriginalitySelector';
import PhotoUpload from '@/components/mechanic/order-wizard/PhotoUpload';
import OrderConfirmation from '@/components/mechanic/order-wizard/OrderConfirmation';

const WIZARD_STEPS = {
  CATEGORY: 1,
  PARTS: 2,
  CAR_NUMBER: 3,
  ORIGINALITY: 4,
  PHOTO: 5,
  CONFIRMATION: 6,
} as const;

type WizardStep = typeof WIZARD_STEPS[keyof typeof WIZARD_STEPS];

export default function NewOrder() {
  const navigate = useNavigate();
  const [step, setStep] = useState<WizardStep>(WIZARD_STEPS.CATEGORY);
  
  const [categoryId, setCategoryId] = useState<number | null>(null);
  const [selectedPartIds, setSelectedPartIds] = useState<number[]>([]);
  const [carNumber, setCarNumber] = useState('');
  const [partType, setPartType] = useState<'original' | 'analog' | 'any'>('original');
  const [photo, setPhoto] = useState<string | null>(null);

  const nextStep = () => setStep((prev) => (prev + 1) as WizardStep);
  const prevStep = () => setStep((prev) => (prev - 1) as WizardStep);

  const handleSubmit = async () => {
    try {
      const formData = new FormData();
      formData.append('category_id', categoryId!.toString());
      formData.append('part_ids', JSON.stringify(selectedPartIds));
      formData.append('car_number', carNumber);
      formData.append('part_type', partType);
      
      if (photo) {
        const blob = await fetch(photo).then((r) => r.blob());
        formData.append('photo', blob, 'order-photo.jpg');
      }

      await api.post('/mechanic/orders', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      toast.success('Заказ создан успешно!');
      navigate('/mechanic/dashboard');
      
    } catch (error: any) {
      toast.error(error.response?.data?.error || 'Ошибка создания заказа');
      throw error;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white border-b sticky top-0 z-10">
        <div className="px-4 py-3">
          <div className="flex items-center justify-between mb-2">
            <button onClick={() => navigate('/mechanic/dashboard')}>
              <ArrowLeft className="h-5 w-5" />
            </button>
            <h1 className="font-semibold">Новый заказ</h1>
            <div className="w-5" />
          </div>
          
          <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
            <div 
              className="h-full bg-blue-600 transition-all duration-300"
              style={{ width: `${(step / 6) * 100}%` }}
            />
          </div>
          <p className="text-xs text-gray-500 text-center mt-1">
            Шаг {step} из 6
          </p>
        </div>
      </div>

      <div className="container max-w-2xl mx-auto px-4 py-6">
        {step === WIZARD_STEPS.CATEGORY && (
          <CategorySelector
            selected={categoryId}
            onSelect={(id) => {
              setCategoryId(id);
              nextStep();
            }}
          />
        )}

        {step === WIZARD_STEPS.PARTS && (
          <PartsSelector
            categoryId={categoryId!}
            selectedIds={selectedPartIds}
            onSelect={setSelectedPartIds}
            onNext={nextStep}
            onBack={prevStep}
          />
        )}

        {step === WIZARD_STEPS.CAR_NUMBER && (
          <VinInput
            value={carNumber}
            onChange={setCarNumber}
            onNext={nextStep}
            onBack={prevStep}
          />
        )}

        {step === WIZARD_STEPS.ORIGINALITY && (
          <OriginalitySelector
            selected={partType}
            onSelect={(type) => {
              setPartType(type);
              nextStep();
            }}
            onBack={prevStep}
          />
        )}

        {step === WIZARD_STEPS.PHOTO && (
          <PhotoUpload
            photo={photo}
            onUpload={setPhoto}
            onNext={nextStep}
            onBack={prevStep}
          />
        )}

        {step === WIZARD_STEPS.CONFIRMATION && (
          <OrderConfirmation
            categoryId={categoryId!}
            partIds={selectedPartIds}
            carNumber={carNumber}
            partType={partType}
            photo={photo}
            onSubmit={handleSubmit}
            onBack={prevStep}
          />
        )}
      </div>
    </div>
  );
}
