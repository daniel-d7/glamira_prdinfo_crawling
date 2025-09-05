import requests
from bs4 import BeautifulSoup
import re
import json

def quick_test():
    """Quick test to see what's available on a Glamira product page"""
    url = "https://glamira.com/catalog/product/view/id/110474"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        print(f"Fetching: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all script tags
            scripts = soup.find_all('script')
            print(f"Total scripts found: {len(scripts)}")
            
            # Look for scripts with substantial content
            for i, script in enumerate(scripts):
                if script.string and len(script.string) > 200:
                    content = script.string[:500]  # First 500 chars
                    if any(keyword in content.lower() for keyword in ['product', 'react', 'data', 'json']):
                        print(f"\nScript {i} (first 500 chars):")
                        print(content)
                        print("..." if len(script.string) > 500 else "")
                        
                        # Check for JSON-like structures
                        if '{' in content and '}' in content:
                            print(f"Contains JSON-like structure")
            
            # Also check for input tags with data
            inputs = soup.find_all('input', {'name': re.compile(r'.*data.*|.*json.*|.*product.*', re.I)})
            if inputs:
                print(f"\nFound {len(inputs)} relevant input tags:")
                for inp in inputs:
                    print(f"Input: {inp.get('name')} = {inp.get('value', '')[:100]}...")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    quick_test()
