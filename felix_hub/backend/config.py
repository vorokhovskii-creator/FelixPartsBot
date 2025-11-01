"""
Centralized configuration and feature flags for Felix Hub backend.

This module provides environment-based configuration with sensible defaults.
Feature flags default to OFF in production and ON in staging/development.
"""
import os
from dotenv import load_dotenv

load_dotenv()


def str_to_bool(value, default=False):
    """Convert string environment variable to boolean."""
    if value is None:
        return default
    return str(value).strip().lower() in ('1', 'true', 't', 'yes', 'y', 'on')


def get_environment():
    """Get current environment name."""
    return (
        os.getenv('ENVIRONMENT') or 
        os.getenv('APP_ENV') or 
        os.getenv('FLASK_ENV') or 
        'production'
    ).lower()


# Environment detection
ENVIRONMENT = get_environment()
IS_PRODUCTION = ENVIRONMENT == 'production'
IS_STAGING = ENVIRONMENT in ('staging', 'stage')
IS_DEVELOPMENT = ENVIRONMENT in ('development', 'dev', 'testing', 'test')

# Default for feature flags: OFF in production, ON in staging/dev
DEFAULT_FEATURE_FLAG = IS_STAGING or IS_DEVELOPMENT


# ============================================================================
# Feature Flags
# ============================================================================

# Car Number Field Feature
# Enables car number field in order forms
ENABLE_CAR_NUMBER = str_to_bool(
    os.getenv('ENABLE_CAR_NUMBER'), 
    default=DEFAULT_FEATURE_FLAG
)

# Allow any car number format (skip validation)
ALLOW_ANY_CAR_NUMBER = str_to_bool(
    os.getenv('ALLOW_ANY_CAR_NUMBER'), 
    default=False
)

# Part Categories Feature
# Enables categorized parts catalog view
ENABLE_PART_CATEGORIES = str_to_bool(
    os.getenv('ENABLE_PART_CATEGORIES'), 
    default=DEFAULT_FEATURE_FLAG
)

# Telegram Admin Notifications
# Sends notifications to admin chat when new orders are created
ENABLE_TG_ADMIN_NOTIFS = str_to_bool(
    os.getenv('ENABLE_TG_ADMIN_NOTIFS'), 
    default=DEFAULT_FEATURE_FLAG
)

# Telegram Mechanic Notifications
# Sends notifications to mechanics when order status changes
ENABLE_TG_MECH_NOTIFS = str_to_bool(
    os.getenv('ENABLE_TG_MECH_NOTIFS'), 
    default=DEFAULT_FEATURE_FLAG
)

# Mechanic Internationalization (i18n)
# Enables multi-language support in mechanic interface
ENABLE_MECH_I18N = str_to_bool(
    os.getenv('ENABLE_MECH_I18N'), 
    default=DEFAULT_FEATURE_FLAG
)

# UI Refresh Feature
# Enables modernized UI components and styling
ENABLE_UI_REFRESH = str_to_bool(
    os.getenv('ENABLE_UI_REFRESH'), 
    default=DEFAULT_FEATURE_FLAG
)


# ============================================================================
# Database Configuration
# ============================================================================

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///database.db')
# Railway provides DATABASE_URL with postgres://
# But SQLAlchemy 1.4+ requires postgresql://
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)


# ============================================================================
# Security Configuration
# ============================================================================

SECRET_KEY = os.getenv('SECRET_KEY') or os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')


# ============================================================================
# CORS Configuration
# ============================================================================

ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', '*').split(',')


# ============================================================================
# Telegram Bot Configuration
# ============================================================================

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN') or os.getenv('BOT_TOKEN') or os.getenv('TELEGRAM_TOKEN')
ADMIN_CHAT_IDS = os.getenv('ADMIN_CHAT_IDS', '').strip()
FRONTEND_URL = os.getenv('FRONTEND_URL', 'https://felix-hub.example.com')


# ============================================================================
# Logging
# ============================================================================

def get_feature_flags_status():
    """Return a dictionary of all feature flags and their current state."""
    return {
        'environment': ENVIRONMENT,
        'is_production': IS_PRODUCTION,
        'is_staging': IS_STAGING,
        'is_development': IS_DEVELOPMENT,
        'feature_flags': {
            'ENABLE_CAR_NUMBER': ENABLE_CAR_NUMBER,
            'ENABLE_PART_CATEGORIES': ENABLE_PART_CATEGORIES,
            'ENABLE_TG_ADMIN_NOTIFS': ENABLE_TG_ADMIN_NOTIFS,
            'ENABLE_TG_MECH_NOTIFS': ENABLE_TG_MECH_NOTIFS,
            'ENABLE_MECH_I18N': ENABLE_MECH_I18N,
            'ENABLE_UI_REFRESH': ENABLE_UI_REFRESH,
        }
    }


def log_feature_flags(logger):
    """Log current feature flag configuration."""
    status = get_feature_flags_status()
    logger.info(f"Environment: {status['environment']}")
    logger.info("Feature Flags:")
    for flag, value in status['feature_flags'].items():
        logger.info(f"  {flag}: {value}")
