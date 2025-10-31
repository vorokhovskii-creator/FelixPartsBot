#!/usr/bin/env python3
"""
Test script to verify SPA redirect configuration is correct.
"""
import os
import sys
from pathlib import Path

def test_redirects_file_exists():
    """Test that _redirects file exists in public directory"""
    redirects_path = Path("felix_hub/frontend/public/_redirects")
    if not redirects_path.exists():
        print(f"❌ FAIL: {redirects_path} does not exist")
        return False
    print(f"✅ PASS: {redirects_path} exists")
    return True

def test_redirects_content():
    """Test that _redirects file has correct content"""
    redirects_path = Path("felix_hub/frontend/public/_redirects")
    expected_content = "/*    /index.html   200"
    
    with open(redirects_path, 'r') as f:
        content = f.read().strip()
    
    if content != expected_content:
        print(f"❌ FAIL: _redirects content is incorrect")
        print(f"  Expected: '{expected_content}'")
        print(f"  Got:      '{content}'")
        return False
    print(f"✅ PASS: _redirects content is correct")
    return True

def test_render_yaml_routes():
    """Test that render.yaml has correct route configuration"""
    render_yaml_path = Path("render.yaml")
    
    with open(render_yaml_path, 'r') as f:
        content = f.read()
    
    required_elements = [
        "routes:",
        "type: rewrite",
        "source: /*",
        "destination: /index.html"
    ]
    
    for element in required_elements:
        if element not in content:
            print(f"❌ FAIL: render.yaml missing: '{element}'")
            return False
    
    print(f"✅ PASS: render.yaml has correct routes configuration")
    return True

def test_vite_config():
    """Test that vite.config.ts exists and doesn't override publicDir"""
    vite_config_path = Path("felix_hub/frontend/vite.config.ts")
    
    if not vite_config_path.exists():
        print(f"❌ FAIL: {vite_config_path} does not exist")
        return False
    
    with open(vite_config_path, 'r') as f:
        content = f.read()
    
    # If publicDir is set to something other than 'public', that's a problem
    if "publicDir:" in content and "publicDir: 'public'" not in content:
        print(f"❌ FAIL: vite.config.ts has custom publicDir that may not include public/")
        return False
    
    print(f"✅ PASS: vite.config.ts is correctly configured")
    return True

def test_app_uses_browser_router():
    """Test that App.tsx uses BrowserRouter"""
    app_path = Path("felix_hub/frontend/src/App.tsx")
    
    with open(app_path, 'r') as f:
        content = f.read()
    
    if "BrowserRouter" not in content:
        print(f"❌ FAIL: App.tsx does not use BrowserRouter")
        return False
    
    if "HashRouter" in content:
        print(f"❌ FAIL: App.tsx uses HashRouter instead of BrowserRouter")
        return False
    
    print(f"✅ PASS: App.tsx uses BrowserRouter")
    return True

def main():
    """Run all tests"""
    print("=" * 60)
    print("SPA Redirects Configuration Tests")
    print("=" * 60)
    print()
    
    tests = [
        ("_redirects file exists", test_redirects_file_exists),
        ("_redirects content is correct", test_redirects_content),
        ("render.yaml routes configuration", test_render_yaml_routes),
        ("vite.config.ts is correct", test_vite_config),
        ("App.tsx uses BrowserRouter", test_app_uses_browser_router),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"Testing: {name}")
        results.append(test_func())
        print()
    
    print("=" * 60)
    print(f"Results: {sum(results)}/{len(results)} tests passed")
    print("=" * 60)
    
    if all(results):
        print("\n🎉 All tests passed! SPA redirects are configured correctly.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the configuration.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
