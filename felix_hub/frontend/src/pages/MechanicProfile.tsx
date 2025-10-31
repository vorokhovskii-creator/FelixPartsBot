import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Clock, CheckCircle, TrendingUp, Wrench, Edit, LogOut } from 'lucide-react';
import api from '@/lib/api';
import type { Mechanic, MechanicAllTimeStats } from '@/types';

export default function MechanicProfile() {
  const [mechanic, setMechanic] = useState<Mechanic | null>(null);
  const [stats, setStats] = useState<MechanicAllTimeStats | null>(null);
  const [editMode, setEditMode] = useState(false);
  const [phone, setPhone] = useState('');
  const [isChangingPassword, setIsChangingPassword] = useState(false);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchProfile();
    fetchStats();
  }, []);

  const fetchProfile = async () => {
    try {
      const response = await api.get('/mechanic/me');
      setMechanic(response.data);
      setPhone(response.data.phone || '');
      setLoading(false);
    } catch (error) {
      console.error('Error fetching profile:', error);
      toast.error('Ошибка загрузки профиля');
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await api.get('/mechanic/stats', {
        params: { all_time: 'true' }
      });
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('ru-RU', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const formatHours = (minutes: number) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours}ч ${mins}м`;
  };

  const formatMinutes = (minutes: number) => {
    if (minutes < 60) {
      return `${Math.round(minutes)}м`;
    }
    const hours = Math.floor(minutes / 60);
    const mins = Math.round(minutes % 60);
    return mins > 0 ? `${hours}ч ${mins}м` : `${hours}ч`;
  };

  const handleSaveProfile = async () => {
    try {
      const response = await api.patch('/mechanic/profile', { phone });
      setMechanic(response.data);
      
      // Обновить localStorage
      const savedMechanic = localStorage.getItem('mechanic');
      if (savedMechanic) {
        const mechanicData = JSON.parse(savedMechanic);
        mechanicData.phone = phone;
        localStorage.setItem('mechanic', JSON.stringify(mechanicData));
      }
      
      toast.success('Профиль обновлён');
      setEditMode(false);
    } catch (error: any) {
      toast.error(error.response?.data?.error || 'Ошибка обновления профиля');
    }
  };

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const formData = new FormData(e.target as HTMLFormElement);
    const data = {
      current_password: formData.get('currentPassword'),
      new_password: formData.get('newPassword'),
      confirm_password: formData.get('confirmPassword')
    };
    
    // Проверка совпадения на клиенте
    if (data.new_password !== data.confirm_password) {
      toast.error('Пароли не совпадают');
      return;
    }
    
    setIsChangingPassword(true);
    try {
      await api.post('/mechanic/change-password', data);
      toast.success('Пароль успешно изменён');
      (e.target as HTMLFormElement).reset();
    } catch (error: any) {
      toast.error(error.response?.data?.error || 'Ошибка смены пароля');
    } finally {
      setIsChangingPassword(false);
    }
  };

  const handleLogout = () => {
    if (confirm('Вы уверены, что хотите выйти?')) {
      localStorage.removeItem('mechanic_token');
      localStorage.removeItem('mechanic');
      navigate('/mechanic/login');
    }
  };

  if (loading) {
    return (
      <div className="container max-w-4xl mx-auto px-4 py-6">
        <div className="text-center py-8 text-gray-500">Загрузка...</div>
      </div>
    );
  }

  if (!mechanic) {
    return (
      <div className="container max-w-4xl mx-auto px-4 py-6">
        <div className="text-center py-8 text-gray-500">Профиль не найден</div>
      </div>
    );
  }

  return (
    <div className="container max-w-4xl mx-auto px-4 py-6 space-y-6">
      {/* Карточка профиля */}
      <Card>
        <CardHeader>
          <CardTitle>Профиль механика</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-4 mb-6">
            <Avatar className="h-20 w-20">
              <AvatarFallback className="text-2xl bg-blue-100 text-blue-600">
                {getInitials(mechanic.name)}
              </AvatarFallback>
            </Avatar>
            <div>
              <h2 className="text-2xl font-bold">{mechanic.name}</h2>
              <Badge variant={mechanic.active ? "default" : "secondary"}>
                {mechanic.active ? "Активен" : "Неактивен"}
              </Badge>
            </div>
          </div>

          <div className="space-y-3">
            <div>
              <Label className="text-sm text-gray-600">Email</Label>
              <p className="font-medium">{mechanic.email}</p>
            </div>

            {editMode ? (
              <div>
                <Label htmlFor="phone">Телефон</Label>
                <Input 
                  id="phone"
                  type="tel"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  placeholder="Введите номер телефона"
                />
              </div>
            ) : (
              <div>
                <Label className="text-sm text-gray-600">Телефон</Label>
                <p className="font-medium">{mechanic.phone || 'Не указан'}</p>
              </div>
            )}

            {mechanic.specialty && (
              <div>
                <Label className="text-sm text-gray-600">Специализация</Label>
                <p className="font-medium">{mechanic.specialty}</p>
              </div>
            )}

            {mechanic.created_at && (
              <div>
                <Label className="text-sm text-gray-600">Дата регистрации</Label>
                <p className="font-medium">{formatDate(mechanic.created_at)}</p>
              </div>
            )}
          </div>

          <div className="flex gap-2 mt-6">
            {editMode ? (
              <>
                <Button onClick={handleSaveProfile}>Сохранить</Button>
                <Button 
                  variant="outline" 
                  onClick={() => {
                    setEditMode(false);
                    setPhone(mechanic.phone || '');
                  }}
                >
                  Отмена
                </Button>
              </>
            ) : (
              <Button onClick={() => setEditMode(true)}>
                <Edit className="h-4 w-4 mr-2" />
                Редактировать
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Смена пароля */}
      <Card>
        <CardHeader>
          <CardTitle>Смена пароля</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleChangePassword} className="space-y-4">
            <div>
              <Label htmlFor="currentPassword">Текущий пароль</Label>
              <Input 
                id="currentPassword"
                name="currentPassword"
                type="password"
                required
              />
            </div>

            <div>
              <Label htmlFor="newPassword">Новый пароль</Label>
              <Input 
                id="newPassword"
                name="newPassword"
                type="password"
                minLength={6}
                required
              />
              <p className="text-xs text-gray-500 mt-1">
                Минимум 6 символов
              </p>
            </div>

            <div>
              <Label htmlFor="confirmPassword">Подтвердите пароль</Label>
              <Input 
                id="confirmPassword"
                name="confirmPassword"
                type="password"
                required
              />
            </div>

            <Button type="submit" disabled={isChangingPassword}>
              {isChangingPassword ? 'Изменение...' : 'Сменить пароль'}
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Общая статистика */}
      {stats && (
        <Card>
          <CardHeader>
            <CardTitle>Общая статистика</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4">
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <Clock className="h-8 w-8 mx-auto mb-2 text-blue-600" />
                <p className="text-2xl font-bold">{formatHours(stats.total_minutes)}</p>
                <p className="text-sm text-gray-600">Всего отработано</p>
              </div>

              <div className="text-center p-4 bg-green-50 rounded-lg">
                <CheckCircle className="h-8 w-8 mx-auto mb-2 text-green-600" />
                <p className="text-2xl font-bold">{stats.total_completed}</p>
                <p className="text-sm text-gray-600">Завершено заказов</p>
              </div>

              <div className="text-center p-4 bg-orange-50 rounded-lg">
                <TrendingUp className="h-8 w-8 mx-auto mb-2 text-orange-600" />
                <p className="text-2xl font-bold">{formatMinutes(stats.avg_order_time)}</p>
                <p className="text-sm text-gray-600">Среднее время заказа</p>
              </div>

              <div className="text-center p-4 bg-purple-50 rounded-lg">
                <Wrench className="h-8 w-8 mx-auto mb-2 text-purple-600" />
                <p className="text-2xl font-bold">{stats.active_orders}</p>
                <p className="text-sm text-gray-600">В работе</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Выход */}
      <Card>
        <CardContent className="p-4">
          <Button 
            variant="destructive" 
            className="w-full"
            onClick={handleLogout}
          >
            <LogOut className="h-4 w-4 mr-2" />
            Выйти из аккаунта
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
