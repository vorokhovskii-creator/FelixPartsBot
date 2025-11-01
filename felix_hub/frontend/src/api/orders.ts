import api from '@/lib/api';
import type { Order, OrderDetails } from '@/types';

export const REFETCH_INTERVAL = 30000;

export interface FetchOrdersParams {
  status?: string;
}

export const ordersApi = {
  fetchOrders: async (params?: FetchOrdersParams): Promise<Order[]> => {
    const response = await api.get('/mechanic/orders', { params });
    return response.data;
  },

  fetchOrderDetails: async (id: string | number): Promise<OrderDetails> => {
    const response = await api.get(`/mechanic/orders/${id}`);
    return response.data;
  },

  updateOrderStatus: async (id: string | number, status: string): Promise<void> => {
    await api.patch(`/mechanic/orders/${id}/status`, { status });
  },
};

export const setupPolling = (
  callback: () => void | Promise<void>,
  interval: number = REFETCH_INTERVAL
): (() => void) => {
  let intervalId: number | null = null;
  let isActive = true;

  const startPolling = () => {
    if (intervalId) return;
    
    intervalId = setInterval(() => {
      if (isActive && !document.hidden) {
        callback();
      }
    }, interval) as unknown as number;
  };

  const stopPolling = () => {
    if (intervalId) {
      clearInterval(intervalId);
      intervalId = null;
    }
  };

  const handleVisibilityChange = () => {
    if (!document.hidden) {
      callback();
    }
  };

  const handleFocus = () => {
    callback();
  };

  startPolling();
  window.addEventListener('visibilitychange', handleVisibilityChange);
  window.addEventListener('focus', handleFocus);

  return () => {
    stopPolling();
    isActive = false;
    window.removeEventListener('visibilitychange', handleVisibilityChange);
    window.removeEventListener('focus', handleFocus);
  };
};
