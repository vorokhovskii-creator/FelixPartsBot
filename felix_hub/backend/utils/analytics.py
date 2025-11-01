"""
Analytics and metrics tracking for monitoring and observability.
"""
import logging
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Optional, Dict, List
from sqlalchemy import func, and_

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Collect and calculate metrics for monitoring."""
    
    def __init__(self, db_session):
        """
        Initialize metrics collector.
        
        Args:
            db_session: SQLAlchemy database session
        """
        self.db = db_session
    
    def get_orders_per_day(self, days: int = 30) -> Dict[str, int]:
        """
        Get order count per day for the last N days.
        
        Args:
            days: Number of days to look back
            
        Returns:
            Dict mapping date strings (YYYY-MM-DD) to order counts
        """
        try:
            from models import Order
            
            end_date = datetime.utcnow().date()
            start_date = end_date - timedelta(days=days)
            
            results = self.db.query(
                func.date(Order.created_at).label('date'),
                func.count(Order.id).label('count')
            ).filter(
                Order.created_at >= start_date
            ).group_by(
                func.date(Order.created_at)
            ).order_by(
                func.date(Order.created_at).desc()
            ).all()
            
            # Convert to dict with string keys
            return {
                str(row.date): row.count
                for row in results
            }
        except Exception as e:
            logger.error(f"Error getting orders per day: {e}")
            return {}
    
    def get_status_change_counts(self, days: int = 7) -> Dict[str, int]:
        """
        Get count of status changes by status for recent orders.
        This estimates status changes by counting orders in each status
        that were updated in the last N days.
        
        Args:
            days: Number of days to look back
            
        Returns:
            Dict mapping status to count
        """
        try:
            from models import Order
            
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            results = self.db.query(
                Order.status,
                func.count(Order.id).label('count')
            ).filter(
                Order.updated_at >= cutoff_date
            ).group_by(
                Order.status
            ).all()
            
            return {
                row.status: row.count
                for row in results
            }
        except Exception as e:
            logger.error(f"Error getting status change counts: {e}")
            return {}
    
    def get_notification_success_rate(self, hours: int = 24) -> Dict[str, float]:
        """
        Calculate notification success rate by notification type.
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            Dict with success rates and counts by notification type
        """
        try:
            from models import NotificationLog
            
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            results = self.db.query(
                NotificationLog.notification_type,
                func.count(NotificationLog.id).label('total'),
                func.sum(func.cast(NotificationLog.success, type_=func.Integer)).label('successful')
            ).filter(
                NotificationLog.sent_at >= cutoff_time
            ).group_by(
                NotificationLog.notification_type
            ).all()
            
            metrics = {}
            for row in results:
                total = row.total or 0
                successful = row.successful or 0
                rate = (successful / total * 100) if total > 0 else 100.0
                
                metrics[row.notification_type] = {
                    'success_rate': round(rate, 2),
                    'total': total,
                    'successful': successful,
                    'failed': total - successful
                }
            
            # Calculate overall success rate
            total_all = sum(m['total'] for m in metrics.values())
            successful_all = sum(m['successful'] for m in metrics.values())
            overall_rate = (successful_all / total_all * 100) if total_all > 0 else 100.0
            
            metrics['overall'] = {
                'success_rate': round(overall_rate, 2),
                'total': total_all,
                'successful': successful_all,
                'failed': total_all - successful_all
            }
            
            return metrics
        except Exception as e:
            logger.error(f"Error calculating notification success rate: {e}")
            return {'overall': {'success_rate': 0, 'total': 0, 'successful': 0, 'failed': 0}}
    
    def get_notification_failures(self, hours: int = 1, limit: int = 100) -> List[Dict]:
        """
        Get recent notification failures for debugging.
        
        Args:
            hours: Number of hours to look back
            limit: Maximum number of failures to return
            
        Returns:
            List of failure records
        """
        try:
            from models import NotificationLog
            
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            failures = self.db.query(NotificationLog).filter(
                and_(
                    NotificationLog.sent_at >= cutoff_time,
                    NotificationLog.success == False
                )
            ).order_by(
                NotificationLog.sent_at.desc()
            ).limit(limit).all()
            
            return [
                {
                    'id': f.id,
                    'notification_type': f.notification_type,
                    'order_id': f.order_id,
                    'mechanic_id': f.mechanic_id,
                    'telegram_id': f.telegram_id,
                    'sent_at': f.sent_at.isoformat(),
                    'error_message': f.error_message
                }
                for f in failures
            ]
        except Exception as e:
            logger.error(f"Error getting notification failures: {e}")
            return []
    
    def get_error_rate(self, minutes: int = 60) -> Dict[str, any]:
        """
        Calculate error rate from application logs (if stored).
        This is a placeholder for future implementation with proper error tracking.
        
        Args:
            minutes: Time window in minutes
            
        Returns:
            Dict with error rate metrics
        """
        # This would require error logging to database
        # For now, return placeholder
        return {
            'error_rate': 0,
            'total_requests': 0,
            'errors': 0,
            'note': 'Error tracking not yet implemented'
        }
    
    def get_daily_summary(self) -> Dict:
        """
        Get comprehensive daily summary of key metrics.
        
        Returns:
            Dict with various daily metrics
        """
        try:
            from models import Order, NotificationLog
            
            today = datetime.utcnow().date()
            today_start = datetime.combine(today, datetime.min.time())
            
            # Orders today
            orders_today = self.db.query(func.count(Order.id)).filter(
                Order.created_at >= today_start
            ).scalar() or 0
            
            # Orders by status today
            status_counts = dict(
                self.db.query(Order.status, func.count(Order.id))
                .filter(Order.created_at >= today_start)
                .group_by(Order.status)
                .all()
            )
            
            # Notifications today
            notifications_today = self.db.query(func.count(NotificationLog.id)).filter(
                NotificationLog.sent_at >= today_start
            ).scalar() or 0
            
            # Notification success rate today
            notif_success = self.db.query(
                func.count(NotificationLog.id).label('total'),
                func.sum(func.cast(NotificationLog.success, type_=func.Integer)).label('successful')
            ).filter(
                NotificationLog.sent_at >= today_start
            ).first()
            
            total_notifs = notif_success.total or 0
            successful_notifs = notif_success.successful or 0
            notif_success_rate = (successful_notifs / total_notifs * 100) if total_notifs > 0 else 100.0
            
            return {
                'date': str(today),
                'orders': {
                    'total': orders_today,
                    'by_status': status_counts
                },
                'notifications': {
                    'total': total_notifs,
                    'successful': successful_notifs,
                    'failed': total_notifs - successful_notifs,
                    'success_rate': round(notif_success_rate, 2)
                }
            }
        except Exception as e:
            logger.error(f"Error generating daily summary: {e}")
            return {}
    
    def get_alert_conditions(self) -> List[Dict]:
        """
        Check for alert conditions that require attention.
        
        Returns:
            List of active alerts
        """
        alerts = []
        
        try:
            # Check notification failure rate (last hour)
            notif_metrics = self.get_notification_success_rate(hours=1)
            overall = notif_metrics.get('overall', {})
            
            if overall.get('total', 0) > 0:
                success_rate = overall.get('success_rate', 100)
                if success_rate < 99.0:  # Alert if success rate < 99%
                    alerts.append({
                        'severity': 'warning' if success_rate >= 95 else 'critical',
                        'type': 'notification_failure_rate',
                        'message': f"Notification success rate is {success_rate}% (threshold: 99%)",
                        'details': overall
                    })
            
            # Check for stuck orders (in "новый" status for > 24 hours)
            from models import Order
            day_ago = datetime.utcnow() - timedelta(hours=24)
            stuck_orders = self.db.query(func.count(Order.id)).filter(
                and_(
                    Order.status == 'новый',
                    Order.created_at < day_ago
                )
            ).scalar() or 0
            
            if stuck_orders > 0:
                alerts.append({
                    'severity': 'warning',
                    'type': 'stuck_orders',
                    'message': f"{stuck_orders} orders stuck in 'новый' status for > 24h",
                    'count': stuck_orders
                })
            
            # Check recent notification failures
            failures = self.get_notification_failures(hours=1)
            if len(failures) >= 10:
                alerts.append({
                    'severity': 'critical',
                    'type': 'notification_failure_spike',
                    'message': f"{len(failures)} notification failures in the last hour",
                    'count': len(failures)
                })
            
        except Exception as e:
            logger.error(f"Error checking alert conditions: {e}")
            alerts.append({
                'severity': 'error',
                'type': 'metrics_error',
                'message': f"Error checking metrics: {str(e)}"
            })
        
        return alerts
