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
import { useTranslation } from 'react-i18next';
import LanguageSwitcher from '@/layout/LanguageSwitcher';

export default function MechanicLogin() {
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { t } = useTranslation();
  
  const loginSchema = z.object({
    email: z.string().email(t('login.errors.invalidPhone')),
    password: z.string().min(6, t('login.errors.invalidPassword')),
  });

  type LoginForm = z.infer<typeof loginSchema>;
  
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
      
      toast.success(t('login.deeplink.loggingInWithToken'));
      
      // Redirect to order page if orderId provided
      if (orderId) {
        navigate(`/mechanic/orders/${orderId}`);
      } else {
        navigate('/mechanic/dashboard');
      }
    } catch (error) {
      if (error instanceof AxiosError && error.response?.data?.error) {
        toast.error(`${t('login.errors.loginFailed')}: ${error.response.data.error}`);
      } else {
        toast.error(t('login.errors.loginFailed'));
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
      
      toast.success(t('login.loggingIn'));
      navigate('/mechanic/dashboard');
    } catch (error) {
      if (error instanceof AxiosError && error.response?.data?.error) {
        toast.error(error.response.data.error);
      } else {
        toast.error(t('login.errors.loginFailed'));
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-1">
          <div className="flex justify-between items-center">
            <CardTitle className="text-2xl font-bold">
              {t('header.appName')}
            </CardTitle>
            <LanguageSwitcher />
          </div>
          <CardDescription className="text-center">
            {t('login.title')}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email">{t('login.phoneLabel')}</Label>
              <Input
                id="email"
                type="email"
                placeholder={t('login.phonePlaceholder')}
                {...register('email')}
                className={errors.email ? 'border-red-500' : ''}
              />
              {errors.email && (
                <p className="text-sm text-red-500">{errors.email.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="password">{t('login.passwordLabel')}</Label>
              <Input
                id="password"
                type="password"
                placeholder={t('login.passwordPlaceholder')}
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
              {isLoading ? t('login.loggingIn') : t('login.loginButton')}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
