import { Card, CardContent } from '@/components/ui/card';

export function DashboardSkeleton() {
  return (
    <div className="container max-w-4xl mx-auto px-4 py-6">
      {/* Stats skeleton */}
      <div className="grid grid-cols-3 gap-3 mb-6">
        {[1, 2, 3].map((i) => (
          <Card key={i}>
            <CardContent className="p-4">
              <div className="flex flex-col items-center text-center animate-pulse">
                <div className="h-8 w-8 bg-gray-200 rounded mb-2"></div>
                <div className="h-6 w-12 bg-gray-200 rounded mb-1"></div>
                <div className="h-3 w-16 bg-gray-200 rounded"></div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Filters skeleton */}
      <div className="h-10 bg-gray-200 rounded mb-6 animate-pulse"></div>

      {/* Orders skeleton */}
      <div className="space-y-3">
        {[1, 2, 3].map((i) => (
          <Card key={i}>
            <CardContent className="p-4 animate-pulse">
              <div className="flex items-start justify-between mb-2">
                <div>
                  <div className="h-5 w-24 bg-gray-200 rounded mb-2"></div>
                  <div className="h-4 w-32 bg-gray-200 rounded"></div>
                </div>
                <div className="h-6 w-16 bg-gray-200 rounded"></div>
              </div>
              <div className="space-y-2">
                <div className="h-4 w-full bg-gray-200 rounded"></div>
                <div className="h-4 w-3/4 bg-gray-200 rounded"></div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}

export function OrderDetailsSkeleton() {
  return (
    <div className="container max-w-4xl mx-auto px-4 py-6 space-y-4">
      <Card>
        <CardContent className="p-4 animate-pulse">
          <div className="space-y-3">
            <div className="h-4 w-1/3 bg-gray-200 rounded"></div>
            <div className="h-6 w-1/2 bg-gray-200 rounded"></div>
            <div className="h-4 w-2/3 bg-gray-200 rounded"></div>
          </div>
        </CardContent>
      </Card>

      <div className="h-12 bg-gray-200 rounded animate-pulse"></div>
      <div className="h-10 bg-gray-200 rounded animate-pulse"></div>

      <Card>
        <CardContent className="p-4 animate-pulse space-y-3">
          <div className="h-4 w-full bg-gray-200 rounded"></div>
          <div className="h-4 w-full bg-gray-200 rounded"></div>
          <div className="h-4 w-3/4 bg-gray-200 rounded"></div>
        </CardContent>
      </Card>
    </div>
  );
}

export function ProfileSkeleton() {
  return (
    <div className="container max-w-4xl mx-auto px-4 py-6 space-y-6">
      <Card>
        <CardContent className="p-6 animate-pulse">
          <div className="flex items-center gap-4 mb-6">
            <div className="h-20 w-20 bg-gray-200 rounded-full"></div>
            <div>
              <div className="h-6 w-32 bg-gray-200 rounded mb-2"></div>
              <div className="h-4 w-20 bg-gray-200 rounded"></div>
            </div>
          </div>
          <div className="space-y-4">
            <div className="h-4 w-1/4 bg-gray-200 rounded"></div>
            <div className="h-10 w-full bg-gray-200 rounded"></div>
            <div className="h-4 w-1/4 bg-gray-200 rounded"></div>
            <div className="h-10 w-full bg-gray-200 rounded"></div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
