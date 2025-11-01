import api from '@/lib/api';
import type { Category, Part } from '@/types';

export const partsApi = {
  fetchCategories: async (): Promise<Category[]> => {
    const response = await api.get('/categories');
    return response.data;
  },

  fetchParts: async (categoryId?: number): Promise<Part[]> => {
    const response = await api.get('/parts', {
      params: categoryId ? { category_id: categoryId } : undefined,
    });
    return response.data;
  },

  fetchCategory: async (categoryId: number): Promise<Category> => {
    const response = await api.get(`/categories/${categoryId}`);
    return response.data;
  },

  fetchPart: async (partId: number): Promise<Part> => {
    const response = await api.get(`/parts/${partId}`);
    return response.data;
  },
};
