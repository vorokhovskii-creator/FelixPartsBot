import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { toast } from 'sonner';
import { AxiosError } from 'axios';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import api from '@/lib/api';

const loginSchema = z.object({
  email: z.string().email('Некорректный email'),
  password: z.string().min(6, 'Пароль должен быть минимум 6 символов'),
});

type LoginForm = z.infer<typeof loginSchema>;

export default function MechanicLogin() {
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  
  const { register, handleSubmit, formState: { errors } } = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
  });

  useEffect(() => {
    const token = localStorage.getItem('mechanic_token');
    if (token) {
      navigate('/mechanic/dashboard');
      return;
    }

    // Check for deeplink token in URL params
    const deeplinkToken = searchParams.get('token');
    const redirectOrderId = searchParams.get('order');
    
    if (deeplinkToken) {
      handleDeeplinkLogin(deeplinkToken, redirectOrderId);
    }
  }, [navigate, searchParams]);

  const handleDeeplinkLogin = async (token: string, orderId: string | null) => {
    setIsLoading(true);
    
    try {
      const response = await api.post('/mechanic/token-login', { token });
      
      // Save token and mechanic data
      localStorage.setItem('mechanic_token', response.data.token);
      localStorage.setItem('mechanic', JSON.stringify(response.data.mechanic));
      
      toast.success('Вход выполнен успешно');
      
      // Redirect to order page if orderId provided
      if (orderId) {
        navigate(`/mechanic/orders/${orderId}`);
      } else {
        navigate('/mechanic/dashboard');
      }
    } catch (error) {
      if (error instanceof AxiosError && error.response?.data?.error) {
        toast.error(`Ошибка автологина: ${error.response.data.error}`);
      } else {
        toast.error('Ошибка автологина. Войдите вручную.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const onSubmit = async (data: LoginForm) => {
    setIsLoading(true);
    
    try {
      const response = await api.post('/mechanic/login', data);
      
      // Сохранить токен и данные механика
      localStorage.setItem('mechanic_token', response.data.token);
      localStorage.setItem('mechanic', JSON.stringify(response.data.mechanic));
      
      toast.success('Вход выполнен успешно');
      navigate('/mechanic/dashboard');
    } catch (error) {
      if (error instanceof AxiosError && error.response?.data?.error) {
        toast.error(error.response.data.error);
      } else {
        toast.error('Ошибка входа');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-1">
          <CardTitle className="text-2xl font-bold text-center">
            Felix Hub
          </CardTitle>
          <CardDescription className="text-center">
            Вход для механиков
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="ivan@felix.com"
                {...register('email')}
                className={errors.email ? 'border-red-500' : ''}
              />
              {errors.email && (
                <p className="text-sm text-red-500">{errors.email.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="password">Пароль</Label>
              <Input
                id="password"
                type="password"
                placeholder="••••••"
                {...register('password')}
                className={errors.password ? 'border-red-500' : ''}
              />
              {errors.password && (
                <p className="text-sm text-red-500">{errors.password.message}</p>
              )}
            </div>

            <Button 
              type="submit" 
              className="w-full touch-target"
              disabled={isLoading}
            >
              {isLoading ? 'Вход...' : 'Войти'}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
