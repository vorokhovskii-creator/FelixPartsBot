#!/bin/bash
#
# Production Rollout Verification Script
# Verifies that all feature flags are enabled and working correctly
#
# Usage: ./verify_production_rollout.sh [--backend-url URL] [--frontend-url URL]
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default URLs
BACKEND_URL="${BACKEND_URL:-https://felix-hub-backend.onrender.com}"
FRONTEND_URL="${FRONTEND_URL:-https://felix-hub-mechanics-frontend.onrender.com}"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --backend-url)
            BACKEND_URL="$2"
            shift 2
            ;;
        --frontend-url)
            FRONTEND_URL="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [--backend-url URL] [--frontend-url URL]"
            echo ""
            echo "Options:"
            echo "  --backend-url URL    Backend URL (default: https://felix-hub-backend.onrender.com)"
            echo "  --frontend-url URL   Frontend URL (default: https://felix-hub-mechanics-frontend.onrender.com)"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

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

# Check if required commands exist
check_dependencies() {
    print_header "Checking Dependencies"
    
    local missing_deps=()
    
    if ! command -v curl &> /dev/null; then
        missing_deps+=("curl")
    fi
    
    if ! command -v jq &> /dev/null; then
        print_warning "jq not found - JSON output will be raw"
    fi
    
    if [ ${#missing_deps[@]} -gt 0 ]; then
        print_error "Missing required dependencies: ${missing_deps[*]}"
        echo "Please install them and try again."
        exit 1
    fi
    
    print_success "All required dependencies found"
}

# Check backend health
check_backend_health() {
    print_header "Backend Health Check"
    
    print_info "Checking: $BACKEND_URL/health"
    
    local response=$(curl -s -w "\n%{http_code}" "$BACKEND_URL/health" 2>&1)
    local http_code=$(echo "$response" | tail -n 1)
    local body=$(echo "$response" | head -n -1)
    
    if [ "$http_code" = "200" ]; then
        print_success "Backend is healthy (HTTP $http_code)"
        echo "Response: $body"
    else
        print_error "Backend health check failed (HTTP $http_code)"
        echo "Response: $body"
        return 1
    fi
}

# Check frontend accessibility
check_frontend_health() {
    print_header "Frontend Health Check"
    
    print_info "Checking: $FRONTEND_URL"
    
    local http_code=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL")
    
    if [ "$http_code" = "200" ]; then
        print_success "Frontend is accessible (HTTP $http_code)"
    else
        print_error "Frontend check failed (HTTP $http_code)"
        return 1
    fi
}

# Check feature flags
check_feature_flags() {
    print_header "Feature Flags Status"
    
    print_info "Checking: $BACKEND_URL/api/config/feature-flags"
    
    local response=$(curl -s "$BACKEND_URL/api/config/feature-flags" 2>&1)
    
    if [ $? -ne 0 ]; then
        print_error "Failed to fetch feature flags"
        return 1
    fi
    
    echo "Response: $response"
    echo ""
    
    # Check each feature flag
    local all_enabled=true
    
    if command -v jq &> /dev/null; then
        # Use jq for parsing
        local flags=("ENABLE_CAR_NUMBER" "ENABLE_PART_CATEGORIES" "ENABLE_TG_ADMIN_NOTIFS" "ENABLE_TG_MECH_NOTIFS" "ENABLE_MECH_I18N" "ENABLE_UI_REFRESH")
        
        for flag in "${flags[@]}"; do
            local value=$(echo "$response" | jq -r ".$flag")
            
            if [ "$value" = "true" ]; then
                print_success "$flag: enabled"
            elif [ "$value" = "false" ]; then
                print_warning "$flag: disabled"
                all_enabled=false
            else
                print_error "$flag: unknown status ($value)"
                all_enabled=false
            fi
        done
    else
        # Manual parsing without jq
        if echo "$response" | grep -q '"ENABLE_CAR_NUMBER".*true'; then
            print_success "ENABLE_CAR_NUMBER: enabled"
        else
            print_warning "ENABLE_CAR_NUMBER: disabled or not found"
            all_enabled=false
        fi
        
        if echo "$response" | grep -q '"ENABLE_PART_CATEGORIES".*true'; then
            print_success "ENABLE_PART_CATEGORIES: enabled"
        else
            print_warning "ENABLE_PART_CATEGORIES: disabled or not found"
            all_enabled=false
        fi
        
        if echo "$response" | grep -q '"ENABLE_TG_ADMIN_NOTIFS".*true'; then
            print_success "ENABLE_TG_ADMIN_NOTIFS: enabled"
        else
            print_warning "ENABLE_TG_ADMIN_NOTIFS: disabled or not found"
            all_enabled=false
        fi
        
        if echo "$response" | grep -q '"ENABLE_TG_MECH_NOTIFS".*true'; then
            print_success "ENABLE_TG_MECH_NOTIFS: enabled"
        else
            print_warning "ENABLE_TG_MECH_NOTIFS: disabled or not found"
            all_enabled=false
        fi
        
        if echo "$response" | grep -q '"ENABLE_MECH_I18N".*true'; then
            print_success "ENABLE_MECH_I18N: enabled"
        else
            print_warning "ENABLE_MECH_I18N: disabled or not found"
            all_enabled=false
        fi
        
        if echo "$response" | grep -q '"ENABLE_UI_REFRESH".*true'; then
            print_success "ENABLE_UI_REFRESH: enabled"
        else
            print_warning "ENABLE_UI_REFRESH: disabled or not found"
            all_enabled=false
        fi
    fi
    
    echo ""
    if [ "$all_enabled" = true ]; then
        print_success "All feature flags are enabled"
    else
        print_warning "Some feature flags are not enabled"
    fi
}

# Check API endpoints
check_api_endpoints() {
    print_header "API Endpoints Verification"
    
    # Check orders endpoint
    print_info "Checking: $BACKEND_URL/api/orders"
    local http_code=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/api/orders")
    
    if [ "$http_code" = "200" ] || [ "$http_code" = "401" ]; then
        print_success "Orders endpoint accessible (HTTP $http_code)"
    else
        print_error "Orders endpoint failed (HTTP $http_code)"
    fi
    
    # Check categories endpoint (if ENABLE_PART_CATEGORIES is on)
    print_info "Checking: $BACKEND_URL/api/categories"
    local http_code=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/api/categories")
    
    if [ "$http_code" = "200" ]; then
        print_success "Categories endpoint accessible (HTTP $http_code)"
    elif [ "$http_code" = "404" ]; then
        print_warning "Categories endpoint not found (ENABLE_PART_CATEGORIES may be off)"
    else
        print_error "Categories endpoint failed (HTTP $http_code)"
    fi
    
    # Check parts endpoint
    print_info "Checking: $BACKEND_URL/api/parts"
    local http_code=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/api/parts")
    
    if [ "$http_code" = "200" ]; then
        print_success "Parts endpoint accessible (HTTP $http_code)"
    elif [ "$http_code" = "404" ]; then
        print_warning "Parts endpoint not found (ENABLE_PART_CATEGORIES may be off)"
    else
        print_error "Parts endpoint failed (HTTP $http_code)"
    fi
}

# Check response time
check_response_time() {
    print_header "Response Time Check"
    
    print_info "Measuring response time for: $BACKEND_URL/api/orders"
    
    local start=$(date +%s%N)
    curl -s "$BACKEND_URL/api/orders" > /dev/null 2>&1
    local end=$(date +%s%N)
    
    local duration_ns=$((end - start))
    local duration_ms=$((duration_ns / 1000000))
    
    echo "Response time: ${duration_ms}ms"
    
    if [ $duration_ms -lt 1000 ]; then
        print_success "Response time is good (< 1s)"
    elif [ $duration_ms -lt 2000 ]; then
        print_warning "Response time is acceptable (< 2s)"
    else
        print_error "Response time is slow (> 2s)"
    fi
}

# Check database migrations
check_migrations() {
    print_header "Database Schema Verification"
    
    print_info "Note: This check requires database access"
    print_info "To verify migrations, run on the server:"
    echo ""
    echo "  python migrations/run_migrations.py status"
    echo ""
    print_info "Expected migrations:"
    echo "  - 001_add_car_number_column.py"
    echo "  - 002_create_categories_parts_tables.py"
}

# Summary
print_summary() {
    print_header "Verification Summary"
    
    echo "Backend URL: $BACKEND_URL"
    echo "Frontend URL: $FRONTEND_URL"
    echo ""
    echo "For full rollout procedure, see: PRODUCTION_ROLLOUT_PLAN.md"
    echo "For quick reference, see: ROLLOUT_QUICK_REFERENCE.md"
    echo ""
    
    print_info "Next steps:"
    echo "  1. Review feature flags status above"
    echo "  2. If not all enabled, follow the rollout plan"
    echo "  3. Run smoke tests (see SMOKE_TEST_CHECKLIST.md)"
    echo "  4. Monitor for 24 hours"
    echo ""
}

# Main execution
main() {
    echo ""
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║   Production Rollout Verification Script                  ║"
    echo "║   Felix Hub System                                         ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
    
    check_dependencies
    
    local all_passed=true
    
    check_backend_health || all_passed=false
    check_frontend_health || all_passed=false
    check_feature_flags || all_passed=false
    check_api_endpoints || all_passed=false
    check_response_time || all_passed=false
    check_migrations
    
    print_summary
    
    if [ "$all_passed" = true ]; then
        print_success "All checks passed!"
        exit 0
    else
        print_warning "Some checks failed or warnings present"
        exit 1
    fi
}

# Run main function
main
