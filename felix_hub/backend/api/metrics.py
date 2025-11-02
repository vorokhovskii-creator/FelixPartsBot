"""
Metrics and monitoring API endpoints.
"""
import logging
from flask import Blueprint, jsonify, request
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models import db
from utils.analytics import MetricsCollector
from utils.circuit_breaker import get_all_circuit_breakers

logger = logging.getLogger(__name__)

metrics_bp = Blueprint('metrics', __name__, url_prefix='/api/metrics')


@metrics_bp.route('/orders/daily', methods=['GET'])
def get_daily_orders():
    """
    Get order count per day for the last N days.
    
    Query params:
        days: Number of days to look back (default: 30)
    """
    try:
        days = request.args.get('days', 30, type=int)
        if days < 1 or days > 365:
            return jsonify({'error': 'days must be between 1 and 365'}), 400
        
        collector = MetricsCollector(db.session)
        data = collector.get_orders_per_day(days=days)
        
        return jsonify({
            'days': days,
            'orders_per_day': data
        }), 200
    except Exception as e:
        logger.error(f"Error getting daily orders: {e}")
        return jsonify({'error': 'Failed to fetch daily orders'}), 500


@metrics_bp.route('/status-changes', methods=['GET'])
def get_status_changes():
    """
    Get count of status changes for recent orders.
    
    Query params:
        days: Number of days to look back (default: 7)
    """
    try:
        days = request.args.get('days', 7, type=int)
        if days < 1 or days > 90:
            return jsonify({'error': 'days must be between 1 and 90'}), 400
        
        collector = MetricsCollector(db.session)
        data = collector.get_status_change_counts(days=days)
        
        return jsonify({
            'days': days,
            'status_changes': data
        }), 200
    except Exception as e:
        logger.error(f"Error getting status changes: {e}")
        return jsonify({'error': 'Failed to fetch status changes'}), 500


@metrics_bp.route('/notifications/success-rate', methods=['GET'])
def get_notification_success_rate():
    """
    Get notification success rate by type.
    
    Query params:
        hours: Number of hours to look back (default: 24)
    """
    try:
        hours = request.args.get('hours', 24, type=int)
        if hours < 1 or hours > 168:  # Max 1 week
            return jsonify({'error': 'hours must be between 1 and 168'}), 400
        
        collector = MetricsCollector(db.session)
        data = collector.get_notification_success_rate(hours=hours)
        
        return jsonify({
            'hours': hours,
            'notification_metrics': data
        }), 200
    except Exception as e:
        logger.error(f"Error getting notification success rate: {e}")
        return jsonify({'error': 'Failed to fetch notification success rate'}), 500


@metrics_bp.route('/notifications/failures', methods=['GET'])
def get_notification_failures():
    """
    Get recent notification failures.
    
    Query params:
        hours: Number of hours to look back (default: 1)
        limit: Maximum number of failures to return (default: 100)
    """
    try:
        hours = request.args.get('hours', 1, type=int)
        limit = request.args.get('limit', 100, type=int)
        
        if hours < 1 or hours > 168:
            return jsonify({'error': 'hours must be between 1 and 168'}), 400
        if limit < 1 or limit > 1000:
            return jsonify({'error': 'limit must be between 1 and 1000'}), 400
        
        collector = MetricsCollector(db.session)
        failures = collector.get_notification_failures(hours=hours, limit=limit)
        
        return jsonify({
            'hours': hours,
            'limit': limit,
            'count': len(failures),
            'failures': failures
        }), 200
    except Exception as e:
        logger.error(f"Error getting notification failures: {e}")
        return jsonify({'error': 'Failed to fetch notification failures'}), 500


@metrics_bp.route('/summary', methods=['GET'])
def get_summary():
    """
    Get comprehensive daily summary of key metrics.
    """
    try:
        collector = MetricsCollector(db.session)
        summary = collector.get_daily_summary()
        
        return jsonify(summary), 200
    except Exception as e:
        logger.error(f"Error getting daily summary: {e}")
        return jsonify({'error': 'Failed to fetch daily summary'}), 500


@metrics_bp.route('/alerts', methods=['GET'])
def get_alerts():
    """
    Check for alert conditions that require attention.
    """
    try:
        collector = MetricsCollector(db.session)
        alerts = collector.get_alert_conditions()
        
        # Determine overall health status
        critical_alerts = [a for a in alerts if a.get('severity') == 'critical']
        warning_alerts = [a for a in alerts if a.get('severity') == 'warning']
        
        status = 'healthy'
        if critical_alerts:
            status = 'critical'
        elif warning_alerts:
            status = 'warning'
        
        return jsonify({
            'status': status,
            'alert_count': len(alerts),
            'critical_count': len(critical_alerts),
            'warning_count': len(warning_alerts),
            'alerts': alerts
        }), 200
    except Exception as e:
        logger.error(f"Error checking alerts: {e}")
        return jsonify({
            'status': 'error',
            'error': 'Failed to check alert conditions'
        }), 500


@metrics_bp.route('/circuit-breakers', methods=['GET'])
def get_circuit_breaker_status():
    """
    Get status of all circuit breakers.
    """
    try:
        breakers = get_all_circuit_breakers()
        
        breaker_data = {}
        for name, breaker in breakers.items():
            breaker_data[name] = breaker.get_metrics()
        
        return jsonify({
            'circuit_breakers': breaker_data
        }), 200
    except Exception as e:
        logger.error(f"Error getting circuit breaker status: {e}")
        return jsonify({'error': 'Failed to fetch circuit breaker status'}), 500


@metrics_bp.route('/dashboard', methods=['GET'])
def get_dashboard():
    """
    Get comprehensive dashboard data with all key metrics.
    """
    try:
        collector = MetricsCollector(db.session)
        
        # Gather all metrics
        daily_summary = collector.get_daily_summary()
        orders_per_day = collector.get_orders_per_day(days=7)
        status_changes = collector.get_status_change_counts(days=7)
        notif_success = collector.get_notification_success_rate(hours=24)
        alerts = collector.get_alert_conditions()
        
        # Circuit breaker status
        breakers = get_all_circuit_breakers()
        breaker_data = {name: breaker.get_metrics() for name, breaker in breakers.items()}
        
        # Determine overall health
        critical_alerts = [a for a in alerts if a.get('severity') == 'critical']
        warning_alerts = [a for a in alerts if a.get('severity') == 'warning']
        
        health_status = 'healthy'
        if critical_alerts:
            health_status = 'critical'
        elif warning_alerts:
            health_status = 'warning'
        
        return jsonify({
            'health_status': health_status,
            'timestamp': daily_summary.get('date'),
            'daily_summary': daily_summary,
            'orders_last_7_days': orders_per_day,
            'status_changes_last_7_days': status_changes,
            'notification_success_rate_24h': notif_success,
            'alerts': {
                'count': len(alerts),
                'critical': len(critical_alerts),
                'warnings': len(warning_alerts),
                'items': alerts
            },
            'circuit_breakers': breaker_data
        }), 200
    except Exception as e:
        logger.error(f"Error generating dashboard: {e}")
        return jsonify({'error': 'Failed to generate dashboard data'}), 500
