#!/bin/bash

# Felix Hub System - Setup Validation Script
# This script checks if the system is properly configured and ready to run

echo "======================================"
echo "Felix Hub - Setup Validation"
echo "======================================"
echo ""

ERRORS=0
WARNINGS=0

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print success
success() {
    echo -e "${GREEN}✓${NC} $1"
}

# Function to print error
error() {
    echo -e "${RED}✗${NC} $1"
    ((ERRORS++))
}

# Function to print warning
warning() {
    echo -e "${YELLOW}⚠${NC} $1"
    ((WARNINGS++))
}

echo "1. Checking directory structure..."

if [ -d "felix_hub/backend" ]; then
    success "Backend directory exists"
else
    error "Backend directory not found"
fi

if [ -d "felix_hub/bot" ]; then
    success "Bot directory exists"
else
    error "Bot directory not found"
fi

echo ""
echo "2. Checking key Python files..."

FILES=(
    "felix_hub/backend/app.py"
    "felix_hub/backend/models.py"
    "felix_hub/backend/utils/notifier.py"
    "felix_hub/backend/utils/printer.py"
    "felix_hub/bot/bot.py"
    "felix_hub/bot/config.py"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        success "$file exists"
    else
        error "$file not found"
    fi
done

echo ""
echo "3. Checking Python syntax..."

cd felix_hub/backend
if python3 -m py_compile app.py 2>/dev/null; then
    success "app.py syntax valid"
else
    error "app.py has syntax errors"
fi

if python3 -m py_compile models.py 2>/dev/null; then
    success "models.py syntax valid"
else
    error "models.py has syntax errors"
fi

cd ../../felix_hub/bot
if python3 -m py_compile bot.py 2>/dev/null; then
    success "bot.py syntax valid"
else
    error "bot.py has syntax errors"
fi

cd ../..

echo ""
echo "4. Checking configuration files..."

if [ -f "felix_hub/backend/.env.example" ]; then
    success "Backend .env.example exists"
else
    error "Backend .env.example not found"
fi

if [ -f "felix_hub/bot/.env.example" ]; then
    success "Bot .env.example exists"
else
    error "Bot .env.example not found"
fi

if [ -f "felix_hub/backend/.env" ]; then
    success "Backend .env exists"
else
    warning "Backend .env not found - copy from .env.example"
fi

if [ -f "felix_hub/bot/.env" ]; then
    success "Bot .env exists"
else
    warning "Bot .env not found - copy from .env.example"
fi

echo ""
echo "5. Checking documentation..."

DOCS=(
    "README.md"
    "DEPLOYMENT.md"
    "TROUBLESHOOTING.md"
    "QUICKSTART.md"
)

for doc in "${DOCS[@]}"; do
    if [ -f "$doc" ]; then
        success "$doc exists"
    else
        warning "$doc not found"
    fi
done

echo ""
echo "6. Checking requirements files..."

if [ -f "felix_hub/backend/requirements.txt" ]; then
    success "Backend requirements.txt exists"
else
    error "Backend requirements.txt not found"
fi

if [ -f "felix_hub/bot/requirements.txt" ]; then
    success "Bot requirements.txt exists"
else
    error "Bot requirements.txt not found"
fi

echo ""
echo "7. Checking virtual environments..."

if [ -d "felix_hub/backend/venv" ]; then
    success "Backend venv exists"
else
    warning "Backend venv not found - run: python3 -m venv felix_hub/backend/venv"
fi

if [ -d "felix_hub/bot/venv" ]; then
    success "Bot venv exists"
else
    warning "Bot venv not found - run: python3 -m venv felix_hub/bot/venv"
fi

echo ""
echo "8. Checking .gitignore..."

if [ -f ".gitignore" ]; then
    success ".gitignore exists"
    if grep -q "\.env" .gitignore; then
        success ".env is in .gitignore"
    else
        error ".env not in .gitignore"
    fi
else
    error ".gitignore not found"
fi

echo ""
echo "======================================"
echo "Validation Summary"
echo "======================================"

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed!${NC}"
    echo "System is ready to run."
    echo ""
    echo "Next steps:"
    echo "1. Copy .env.example to .env in both backend and bot directories"
    echo "2. Edit .env files with your configuration"
    echo "3. Follow DEPLOYMENT.md or QUICKSTART.md to start the system"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠ Validation completed with $WARNINGS warning(s)${NC}"
    echo "System might work but check warnings above."
    exit 0
else
    echo -e "${RED}✗ Validation failed with $ERRORS error(s) and $WARNINGS warning(s)${NC}"
    echo "Please fix errors before running the system."
    exit 1
fi
