import pandas as pd
import requests
from bs4 import BeautifulSoup
import json
import re

def test_single_fetch():
    """Test fetching a single product to verify the scraper works"""
    domain = "glamira.com"
    product_id = "110474"
    url = f"https://{domain}/catalog/product/view/id/{product_id}"
    
    print(f"Testing URL: {url}")
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    })
    
    try:
        response = session.get(url, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for react_data patterns
            scripts = soup.find_all('script')
            print(f"Found {len(scripts)} script tags")
            
            react_data_found = False
            for i, script in enumerate(scripts):
                if script.string and 'react_data' in script.string:
                    print(f"Found react_data in script {i}")
                    react_data_found = True
                    # Try to extract the data
                    match = re.search(r'var\s+react_data\s*=\s*({.*?});', script.string, re.DOTALL)
                    if match:
                        try:
                            data = json.loads(match.group(1))
                            print("Successfully parsed react_data")
                            print(f"Keys in react_data: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                            return True
                        except json.JSONDecodeError as e:
                            print(f"JSON parse error: {e}")
            
            if not react_data_found:
                print("No react_data found in any script tag")
                # Check if there are any other relevant data patterns
                page_text = response.text
                if 'product' in page_text.lower():
                    print("Page contains 'product' text - might be a valid product page")
                else:
                    print("Page doesn't seem to contain product data")
        
        return False
    
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    test_single_fetch()
