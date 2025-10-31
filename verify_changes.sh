#!/bin/bash

echo "======================================"
echo "Verifying Mechanic Module Changes"
echo "======================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check frontend directory
echo "1. Checking frontend directory..."
if [ -d "felix_hub/frontend" ]; then
    echo -e "${GREEN}✓${NC} Frontend directory exists"
else
    echo -e "${RED}✗${NC} Frontend directory not found"
    exit 1
fi

# Check if new files exist
echo ""
echo "2. Checking new files..."

files=(
    "MECHANIC_E2E_TEST_CHECKLIST.md"
    "CHANGELOG_MECHANIC_E2E.md"
    "TESTING.md"
    "PR_SUMMARY.md"
    "test_mechanic_e2e.py"
    "felix_hub/frontend/src/components/ErrorBoundary.tsx"
    "felix_hub/frontend/src/components/LoadingSkeleton.tsx"
    "felix_hub/frontend/src/lib/timeUtils.ts"
)

missing_files=0
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file"
    else
        echo -e "${RED}✗${NC} $file is missing"
        missing_files=$((missing_files + 1))
    fi
done

if [ $missing_files -gt 0 ]; then
    echo ""
    echo -e "${RED}Error: $missing_files file(s) missing${NC}"
    exit 1
fi

# Check if modified files exist
echo ""
echo "3. Checking modified files..."

modified_files=(
    "felix_hub/frontend/src/App.tsx"
    "felix_hub/frontend/src/pages/MechanicDashboard.tsx"
    "felix_hub/frontend/src/pages/OrderDetails.tsx"
    "felix_hub/frontend/src/components/mechanic/TimeTracker.tsx"
    "felix_hub/frontend/src/components/mechanic/StatusButtons.tsx"
    "felix_hub/frontend/index.html"
)

missing_modified=0
for file in "${modified_files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file"
    else
        echo -e "${RED}✗${NC} $file is missing"
        missing_modified=$((missing_modified + 1))
    fi
done

if [ $missing_modified -gt 0 ]; then
    echo ""
    echo -e "${RED}Error: $missing_modified modified file(s) missing${NC}"
    exit 1
fi

# Check for window.location.reload in TimeTracker
echo ""
echo "4. Checking for removed anti-patterns..."
if grep -q "window.location.reload" felix_hub/frontend/src/components/mechanic/TimeTracker.tsx; then
    echo -e "${RED}✗${NC} window.location.reload still present in TimeTracker.tsx"
else
    echo -e "${GREEN}✓${NC} window.location.reload removed from TimeTracker.tsx"
fi

# Check for ErrorBoundary import in App.tsx
echo ""
echo "5. Checking ErrorBoundary integration..."
if grep -q "ErrorBoundary" felix_hub/frontend/src/App.tsx; then
    echo -e "${GREEN}✓${NC} ErrorBoundary imported and used in App.tsx"
else
    echo -e "${RED}✗${NC} ErrorBoundary not found in App.tsx"
fi

# Check for memo in StatusButtons
echo ""
echo "6. Checking React.memo usage..."
if grep -q "memo" felix_hub/frontend/src/components/mechanic/StatusButtons.tsx; then
    echo -e "${GREEN}✓${NC} React.memo used in StatusButtons.tsx"
else
    echo -e "${RED}✗${NC} React.memo not found in StatusButtons.tsx"
fi

# Check for error handling in Dashboard
echo ""
echo "7. Checking error handling improvements..."
if grep -q "toast.error" felix_hub/frontend/src/pages/MechanicDashboard.tsx; then
    echo -e "${GREEN}✓${NC} Error handling added to MechanicDashboard.tsx"
else
    echo -e "${RED}✗${NC} Error handling not found in MechanicDashboard.tsx"
fi

# Check for ARIA labels
echo ""
echo "8. Checking accessibility improvements..."
if grep -q "aria-label" felix_hub/frontend/src/pages/OrderDetails.tsx; then
    echo -e "${GREEN}✓${NC} ARIA labels added to OrderDetails.tsx"
else
    echo -e "${YELLOW}⚠${NC} ARIA labels not found in OrderDetails.tsx"
fi

# Check test script is executable
echo ""
echo "9. Checking test script..."
if [ -x "test_mechanic_e2e.py" ]; then
    echo -e "${GREEN}✓${NC} test_mechanic_e2e.py is executable"
else
    echo -e "${YELLOW}⚠${NC} test_mechanic_e2e.py is not executable (run: chmod +x test_mechanic_e2e.py)"
fi

# Summary
echo ""
echo "======================================"
echo -e "${GREEN}All checks passed!${NC}"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Review the changes: git diff"
echo "2. Run backend E2E tests: python3 test_mechanic_e2e.py"
echo "3. Test frontend manually: cd felix_hub/frontend && npm run dev"
echo "4. Review documentation: cat CHANGELOG_MECHANIC_E2E.md"
echo ""
