#!/bin/bash
#
# Production Feature Rollback Script
# Quickly disables all feature flags and optionally rolls back database migrations
#
# Usage: ./rollback_production_features.sh [--full|--partial flag1,flag2]
#        ./rollback_production_features.sh --migrations-only
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print section headers
print_header() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
}

# Function to print success
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Function to print error
print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to print warning
print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Function to print info
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Function to confirm action
confirm_action() {
    local prompt="$1"
    local default="${2:-n}"
    
    if [ "$default" = "y" ]; then
        prompt="$prompt [Y/n]: "
    else
        prompt="$prompt [y/N]: "
    fi
    
    read -p "$prompt" -n 1 -r
    echo
    
    if [ "$default" = "y" ]; then
        [[ ! $REPLY =~ ^[Nn]$ ]]
    else
        [[ $REPLY =~ ^[Yy]$ ]]
    fi
}

# Print rollback instructions for Render
print_render_instructions() {
    local service="$1"
    shift
    local flags=("$@")
    
    print_header "Rollback Instructions for $service"
    
    echo "Go to Render Dashboard:"
    echo "  https://dashboard.render.com"
    echo ""
    echo "Navigate to: $service → Environment"
    echo ""
    echo "Set the following environment variables to 'false':"
    echo ""
    
    for flag in "${flags[@]}"; do
        echo "  $flag=false"
    done
    
    echo ""
    echo "Then click 'Save Changes' - service will auto-restart"
    echo ""
}

# Print migration rollback instructions
print_migration_rollback_instructions() {
    print_header "Database Migration Rollback Instructions"
    
    echo "⚠️  WARNING: Rolling back migrations may cause data loss!"
    echo ""
    echo "Data that will be lost:"
    echo "  - Car numbers in orders (if 001 is rolled back)"
    echo "  - All categories and parts (if 002 is rolled back)"
    echo ""
    
    if ! confirm_action "Do you want to continue with migration rollback?" "n"; then
        print_info "Migration rollback cancelled"
        return 1
    fi
    
    echo ""
    echo "To rollback migrations on Render:"
    echo ""
    echo "1. Open Shell in Render Dashboard:"
    echo "   felix-hub-backend → Shell"
    echo ""
    echo "2. Navigate to backend directory:"
    echo "   cd /opt/render/project/src/felix_hub/backend"
    echo ""
    echo "3. Run rollback command:"
    echo "   python migrations/run_migrations.py rollback"
    echo ""
    echo "4. Verify rollback:"
    echo "   python migrations/run_migrations.py status"
    echo ""
    echo "Expected output:"
    echo "  No migrations found OR migrations show as not applied"
    echo ""
}

# Full rollback
full_rollback() {
    print_header "FULL ROLLBACK - All Feature Flags"
    
    print_warning "This will disable ALL feature flags in production"
    
    if ! confirm_action "Are you sure you want to perform a FULL rollback?" "n"; then
        print_info "Rollback cancelled"
        exit 0
    fi
    
    # Backend flags
    local backend_flags=(
        "ENABLE_CAR_NUMBER"
        "ENABLE_PART_CATEGORIES"
        "ENABLE_TG_ADMIN_NOTIFS"
        "ENABLE_TG_MECH_NOTIFS"
    )
    
    print_render_instructions "felix-hub-backend" "${backend_flags[@]}"
    
    # Frontend flags
    local frontend_flags=(
        "VITE_ENABLE_MECH_I18N"
        "VITE_ENABLE_UI_REFRESH"
    )
    
    print_render_instructions "felix-hub-mechanics-frontend" "${frontend_flags[@]}"
    
    # Ask about migrations
    echo ""
    if confirm_action "Do you also want to rollback database migrations?" "n"; then
        print_migration_rollback_instructions
    fi
    
    print_header "Verification Steps"
    echo "After rollback, verify:"
    echo ""
    echo "1. Wait 1-2 minutes for services to restart"
    echo ""
    echo "2. Check feature flags are disabled:"
    echo "   ./verify_production_rollout.sh"
    echo ""
    echo "3. Verify system health:"
    echo "   curl https://felix-hub-backend.onrender.com/health"
    echo ""
    echo "4. Check application logs for errors"
    echo ""
    
    print_success "Rollback instructions provided"
}

# Partial rollback
partial_rollback() {
    local flags_to_disable="$1"
    
    print_header "PARTIAL ROLLBACK - Selected Flags"
    
    print_info "Flags to disable: $flags_to_disable"
    
    if ! confirm_action "Continue with partial rollback?" "n"; then
        print_info "Rollback cancelled"
        exit 0
    fi
    
    IFS=',' read -ra FLAGS_ARRAY <<< "$flags_to_disable"
    
    local backend_flags=()
    local frontend_flags=()
    
    for flag in "${FLAGS_ARRAY[@]}"; do
        flag=$(echo "$flag" | xargs) # trim whitespace
        
        case $flag in
            ENABLE_CAR_NUMBER|ENABLE_PART_CATEGORIES|ENABLE_TG_ADMIN_NOTIFS|ENABLE_TG_MECH_NOTIFS)
                backend_flags+=("$flag")
                ;;
            ENABLE_MECH_I18N|ENABLE_UI_REFRESH)
                frontend_flags+=("VITE_$flag")
                ;;
            VITE_*)
                frontend_flags+=("$flag")
                ;;
            *)
                print_error "Unknown flag: $flag"
                ;;
        esac
    done
    
    if [ ${#backend_flags[@]} -gt 0 ]; then
        print_render_instructions "felix-hub-backend" "${backend_flags[@]}"
    fi
    
    if [ ${#frontend_flags[@]} -gt 0 ]; then
        print_render_instructions "felix-hub-mechanics-frontend" "${frontend_flags[@]}"
    fi
    
    print_success "Partial rollback instructions provided"
}

# Migrations only rollback
migrations_only_rollback() {
    print_header "MIGRATIONS ROLLBACK ONLY"
    
    print_migration_rollback_instructions
}

# Show help
show_help() {
    echo "Production Feature Rollback Script"
    echo ""
    echo "Usage:"
    echo "  $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --full                     Disable all feature flags"
    echo "  --partial FLAG1,FLAG2,...  Disable specific flags only"
    echo "  --migrations-only          Rollback database migrations only"
    echo "  -h, --help                 Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --full"
    echo "  $0 --partial ENABLE_TG_ADMIN_NOTIFS,ENABLE_TG_MECH_NOTIFS"
    echo "  $0 --migrations-only"
    echo ""
    echo "Available flags:"
    echo "  Backend:"
    echo "    - ENABLE_CAR_NUMBER"
    echo "    - ENABLE_PART_CATEGORIES"
    echo "    - ENABLE_TG_ADMIN_NOTIFS"
    echo "    - ENABLE_TG_MECH_NOTIFS"
    echo ""
    echo "  Frontend:"
    echo "    - ENABLE_MECH_I18N (or VITE_ENABLE_MECH_I18N)"
    echo "    - ENABLE_UI_REFRESH (or VITE_ENABLE_UI_REFRESH)"
    echo ""
}

# Show rollback checklist
show_checklist() {
    print_header "Post-Rollback Checklist"
    
    echo "After performing rollback, verify:"
    echo ""
    echo "□ Services restarted successfully"
    echo "□ Feature flags show as disabled"
    echo "□ Health check passes"
    echo "□ Existing orders still accessible"
    echo "□ Admin panel functional"
    echo "□ Mechanic interface functional"
    echo "□ No errors in application logs"
    echo "□ Database connections stable"
    echo "□ Users notified of rollback (if needed)"
    echo ""
    echo "Monitoring period:"
    echo "  - First 30 minutes: Check every 5 minutes"
    echo "  - Next 2 hours: Check every 30 minutes"
    echo "  - Document the incident and reason for rollback"
    echo ""
}

# Main execution
main() {
    echo ""
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║   Production Feature Rollback Script                      ║"
    echo "║   Felix Hub System                                         ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
    
    # Check if running in production context
    print_warning "This script provides instructions for rollback in production"
    print_warning "It does NOT automatically change environment variables"
    print_warning "You must manually update Render Dashboard settings"
    echo ""
    
    # Parse arguments
    if [ $# -eq 0 ]; then
        show_help
        exit 0
    fi
    
    case "$1" in
        --full)
            full_rollback
            ;;
        --partial)
            if [ -z "$2" ]; then
                print_error "Error: --partial requires a comma-separated list of flags"
                echo ""
                show_help
                exit 1
            fi
            partial_rollback "$2"
            ;;
        --migrations-only)
            migrations_only_rollback
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
    
    show_checklist
    
    echo ""
    print_info "For detailed rollback procedures, see: PRODUCTION_ROLLOUT_PLAN.md"
    echo ""
}

# Run main function
main "$@"
