import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import type { Comment } from '@/types';

interface CommentsListProps {
  orderId: number;
  comments: Comment[];
  onCommentAdded: () => void;
}

export default function CommentsList({ orderId, comments, onCommentAdded }: CommentsListProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Комментарии</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-muted-foreground">
          Функция комментариев будет реализована в следующей задаче
        </p>
        {comments.length > 0 && (
          <div className="mt-4 space-y-2">
            {comments.map((comment) => (
              <div key={comment.id} className="border-b pb-2">
                <p className="text-sm">{comment.comment}</p>
                <p className="text-xs text-muted-foreground mt-1">
                  {comment.mechanic_name}
                </p>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
