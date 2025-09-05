#!/usr/bin/env python3
"""
Quick launcher script for common operations
"""
import subprocess
import sys
import os

def run_command(command, description):
    """Run a command with description"""
    print(f"\n🚀 {description}")
    print(f"Running: {command}")
    print("-" * 50)
    
    try:
        result = subprocess.run(command, shell=True, check=True)
        print(f"✅ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with error: {e}")
        return False

def main():
    print("🔧 Glamira Scraper - Quick Launcher")
    print("="*50)
    
    options = {
        "1": ("python scripts/start_scraping.py", "Run batch scraping (testing)"),
        "2": ("python scripts/run_full_scraping.py", "Run full-scale scraping"),
        "3": ("python scripts/monitor.py", "Monitor scraping progress"),
        "4": ("python scripts/checkpoint_manager.py", "Manage checkpoint database"),
        "5": ("python tests/test_filtering.py", "Test field filtering"),
        "6": ("python tests/quick_test.py", "Quick validation test"),
        "7": ("python main.py", "Run main scraper"),
    }
    
    print("\nAvailable options:")
    for key, (command, description) in options.items():
        print(f"  {key}. {description}")
    
    print("\n  q. Quit")
    
    while True:
        choice = input("\nSelect an option (1-7, q): ").strip().lower()
        
        if choice == 'q':
            print("👋 Goodbye!")
            break
        elif choice in options:
            command, description = options[choice]
            run_command(command, description)
        else:
            print("❌ Invalid option. Please try again.")

if __name__ == "__main__":
    main()
