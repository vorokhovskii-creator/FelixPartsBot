import { useState } from 'react';
import PartsPicker from './PartsPicker';

/**
 * Example usage of the PartsPicker component
 * This file demonstrates how to integrate the PartsPicker into your application
 */
export default function PartsPickerExample() {
  const [selectedPartIds, setSelectedPartIds] = useState<number[]>([]);

  const handleConfirm = (ids: number[]) => {
    console.log('Selected part IDs:', ids);
    // Here you would typically:
    // 1. Save the selection to state
    // 2. Navigate to next step
    // 3. Submit to backend
    alert(`Выбрано запчастей: ${ids.length}`);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="container max-w-2xl mx-auto">
        <h1 className="text-2xl font-bold mb-6">Пример использования PartsPicker</h1>
        
        <div className="bg-white rounded-lg shadow p-6">
          <PartsPicker
            selectedIds={selectedPartIds}
            onSelect={setSelectedPartIds}
            onConfirm={handleConfirm}
            multiSelect={true}
            showConfirmButton={true}
            confirmButtonText="Подтвердить выбор"
          />
        </div>

        <div className="mt-6 p-4 bg-blue-50 rounded-lg">
          <h3 className="font-semibold mb-2">Выбранные запчасти (ID):</h3>
          <p className="text-sm">
            {selectedPartIds.length > 0 
              ? selectedPartIds.join(', ') 
              : 'Пока ничего не выбрано'}
          </p>
        </div>
      </div>
    </div>
  );
}
