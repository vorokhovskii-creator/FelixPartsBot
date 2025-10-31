import { useState, useEffect } from 'react';
import { Send } from 'lucide-react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { formatDistanceToNow } from 'date-fns';
import { ru } from 'date-fns/locale';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { toast } from 'sonner';
import api from '@/lib/api';
import type { Comment } from '@/types';

interface CommentsListProps {
  orderId: number;
  comments: Comment[];
  onCommentAdded: () => void;
}

const commentSchema = z.object({
  comment: z.string().min(1, 'Комментарий не может быть пустым'),
});

type CommentForm = z.infer<typeof commentSchema>;

export default function CommentsList({ orderId, comments, onCommentAdded }: CommentsListProps) {
  const [commentsList, setCommentsList] = useState<Comment[]>(comments);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
    watch,
  } = useForm<CommentForm>({
    resolver: zodResolver(commentSchema),
    defaultValues: {
      comment: '',
    },
  });

  const commentValue = watch('comment');

  useEffect(() => {
    setCommentsList(comments);
  }, [comments]);

  const onSubmit = async (data: CommentForm) => {
    try {
      await api.post(`/mechanic/orders/${orderId}/comments`, data);
      toast.success('Комментарий добавлен');
      reset();
      onCommentAdded();
    } catch (error: any) {
      toast.error(error.response?.data?.message || 'Ошибка добавления комментария');
    }
  };

  const getInitials = (name: string) => {
    const parts = name.trim().split(' ');
    if (parts.length >= 2) {
      return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
    }
    return name.substring(0, 2).toUpperCase();
  };

  const formatRelativeTime = (dateString: string) => {
    return formatDistanceToNow(new Date(dateString), { 
      addSuffix: true,
      locale: ru 
    });
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Комментарии ({commentsList.length})</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Форма добавления */}
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-3">
          <div className="space-y-2">
            <Textarea
              placeholder="Добавить комментарий..."
              {...register('comment')}
              rows={3}
              className="resize-none"
            />
            {errors.comment && (
              <p className="text-sm text-destructive">{errors.comment.message}</p>
            )}
          </div>
          <Button
            type="submit"
            disabled={isSubmitting || !commentValue.trim()}
            className="w-full sm:w-auto min-h-[44px]"
          >
            <Send className="mr-2 h-4 w-4" />
            Отправить
          </Button>
        </form>

        {/* Список комментариев */}
        {commentsList.length === 0 ? (
          <p className="text-sm text-muted-foreground text-center py-8">
            Комментариев пока нет. Будьте первым!
          </p>
        ) : (
          <div className="space-y-4 mt-6">
            {[...commentsList]
              .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
              .map((comment) => (
                <div key={comment.id} className="flex gap-3">
                  <Avatar className="h-10 w-10 flex-shrink-0">
                    <AvatarFallback className="bg-primary text-primary-foreground">
                      {getInitials(comment.mechanic_name)}
                    </AvatarFallback>
                  </Avatar>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <p className="font-semibold text-sm">
                        {comment.mechanic_name}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {formatRelativeTime(comment.created_at)}
                      </p>
                    </div>
                    <p className="text-sm mt-1 break-words">
                      {comment.comment}
                    </p>
                  </div>
                </div>
              ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
