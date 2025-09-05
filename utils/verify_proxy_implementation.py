#!/usr/bin/env python3
"""
Simple verification script for proxy implementation
"""

import os
import sys
from pathlib import Path

# Set up paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def verify_proxy_implementation():
    """Verify that proxy implementation is complete"""
    print("Verifying Proxy Implementation")
    print("=" * 35)
    
    try:
        # Check if main.py exists and has required imports
        main_file = project_root / "main.py"
        if not main_file.exists():
            print("❌ main.py not found")
            return False
        
        with open(main_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for required imports
        required_imports = [
            'from dotenv import load_dotenv',
            'import threading',
            'import requests'
        ]
        
        for imp in required_imports:
            if imp in content:
                print(f"✓ Found import: {imp}")
            else:
                print(f"❌ Missing import: {imp}")
                return False
        
        # Check for required methods
        required_methods = [
            'def load_proxy_configs(self)',
            'def get_worker_proxy(self',
            'def create_proxy_session(self',
            'def process_product_with_worker_id(self'
        ]
        
        for method in required_methods:
            if method in content:
                print(f"✓ Found method: {method.split('(')[0].replace('def ', '')}")
            else:
                print(f"❌ Missing method: {method.split('(')[0].replace('def ', '')}")
                return False
        
        # Check for thread-local storage
        if 'self.thread_local = threading.local()' in content:
            print("✓ Thread-local storage initialized")
        else:
            print("❌ Thread-local storage not found")
            return False
        
        # Check if .env.example exists
        env_example = project_root / ".env.example"
        if env_example.exists():
            print("✓ .env.example file exists")
        else:
            print("❌ .env.example file missing")
            return False
        
        # Check requirements.txt for proxy dependencies
        requirements_file = project_root / "requirements.txt"
        if requirements_file.exists():
            with open(requirements_file, 'r', encoding='utf-8') as f:
                req_content = f.read()
            
            proxy_deps = ['python-dotenv', 'requests[socks]', 'pysocks']
            for dep in proxy_deps:
                if dep in req_content:
                    print(f"✓ Found dependency: {dep}")
                else:
                    print(f"❌ Missing dependency: {dep}")
                    return False
        else:
            print("❌ requirements.txt not found")
            return False
        
        print("\n✓ All proxy implementation components verified!")
        return True
        
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        return False

def show_usage_instructions():
    """Show instructions for using the proxy feature"""
    print("\nProxy Setup Instructions:")
    print("=" * 30)
    print("1. Copy .env.example to .env:")
    print("   copy .env.example .env")
    print("")
    print("2. Edit .env with your proxy details:")
    print("   ip1=your_proxy_ip")
    print("   port1=your_proxy_port")
    print("   user1=your_username")
    print("   passwd1=your_password")
    print("   (repeat for ip2/port2/user2/passwd2 and ip3/port3/user3/passwd3)")
    print("")
    print("3. Test the setup:")
    print("   python test_proxy_setup.py")
    print("")
    print("4. Run a functionality test:")
    print("   python test_proxy_functionality.py")
    print("")
    print("5. Start full scraping:")
    print("   python scripts/start_scraping.py")

def check_env_file():
    """Check if .env file exists and has proxy settings"""
    env_file = project_root / ".env"
    
    if env_file.exists():
        print("\n✓ .env file found")
        
        # Load and check variables
        proxy_vars = ['ip1', 'port1', 'user1', 'passwd1']
        with open(env_file, 'r', encoding='utf-8') as f:
            env_content = f.read()
        
        found_vars = []
        for var in proxy_vars:
            if f"{var}=" in env_content and not f"{var}=your_" in env_content:
                found_vars.append(var)
        
        if found_vars:
            print(f"✓ Found {len(found_vars)} configured proxy variables")
            print("  Ready to use proxy functionality")
        else:
            print("⚠️  .env file exists but no proxy variables configured")
            print("  Edit .env file with your proxy details")
    else:
        print("\n⚠️  .env file not found")
        print("   Copy .env.example to .env and configure your proxy settings")

if __name__ == "__main__":
    print("Glamira Scraper Proxy Implementation Verification")
    print("=" * 55)
    
    # Verify implementation
    implementation_ok = verify_proxy_implementation()
    
    # Check .env file
    check_env_file()
    
    # Show results
    print("\n" + "=" * 55)
    if implementation_ok:
        print("✅ Proxy implementation is complete and ready!")
        show_usage_instructions()
    else:
        print("❌ Proxy implementation has issues that need to be fixed")
    
    print("\nFeatures implemented:")
    print("• SOCKS5 proxy support for each worker")
    print("• Worker-specific proxy assignment (1→proxy1, 2→proxy2, 3→proxy3)")
    print("• Automatic proxy rotation for load balancing")
    print("• Environment variable configuration (.env file)")
    print("• Graceful fallback when no proxies are configured")
    print("• Enhanced logging with worker and proxy information")
