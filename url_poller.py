#!/usr/bin/env python3
"""
URL Polling Script
Polls a list of URLs to check if they are responding or not.
Input: Dictionary of URLs with optional custom names/descriptions.
"""

import requests
import time
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Tuple, Optional
import sys

class URLPoller:
    def __init__(self, timeout: int = 10, max_workers: int = 5):
        """
        Initialize the URL poller.
        
        Args:
            timeout: Request timeout in seconds
            max_workers: Maximum number of concurrent threads
        """
        self.timeout = timeout
        self.max_workers = max_workers
        self.session = requests.Session()
        # Set a user agent to avoid being blocked
        self.session.headers.update({
            'User-Agent': 'URL-Poller/1.0 (Health Check Bot)'
        })
    
    def check_url(self, name: str, url: str) -> Dict:
        """
        Check a single URL and return its status.
        
        Args:
            name: Name/identifier for the URL
            url: URL to check
            
        Returns:
            Dictionary with check results
        """
        result = {
            'name': name,
            'url': url,
            'status': 'unknown',
            'status_code': None,
            'response_time': None,
            'error': None,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            start_time = time.time()
            response = self.session.get(url, timeout=self.timeout, allow_redirects=True)
            end_time = time.time()
            
            result['status_code'] = response.status_code
            result['response_time'] = round((end_time - start_time) * 1000, 2)  # in milliseconds
            
            if response.status_code == 200:
                result['status'] = 'up'
            elif 300 <= response.status_code < 400:
                result['status'] = 'redirect'
            elif 400 <= response.status_code < 500:
                result['status'] = 'client_error'
            elif 500 <= response.status_code < 600:
                result['status'] = 'server_error'
            else:
                result['status'] = 'unknown'
                
        except requests.exceptions.Timeout:
            result['status'] = 'timeout'
            result['error'] = f'Request timed out after {self.timeout} seconds'
        except requests.exceptions.ConnectionError:
            result['status'] = 'connection_error'
            result['error'] = 'Failed to connect to the server'
        except requests.exceptions.RequestException as e:
            result['status'] = 'error'
            result['error'] = str(e)
        except Exception as e:
            result['status'] = 'error'
            result['error'] = f'Unexpected error: {str(e)}'
            
        return result
    
    def poll_urls(self, urls: Dict[str, str]) -> List[Dict]:
        """
        Poll multiple URLs concurrently.
        
        Args:
            urls: Dictionary where keys are names and values are URLs
            
        Returns:
            List of dictionaries with results for each URL
        """
        results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all URL checks
            future_to_url = {
                executor.submit(self.check_url, name, url): (name, url)
                for name, url in urls.items()
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_url):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    name, url = future_to_url[future]
                    results.append({
                        'name': name,
                        'url': url,
                        'status': 'error',
                        'status_code': None,
                        'response_time': None,
                        'error': f'Future execution error: {str(e)}',
                        'timestamp': datetime.now().isoformat()
                    })
        
        return sorted(results, key=lambda x: x['name'])
    
    def print_results(self, results: List[Dict], show_details: bool = True):
        """
        Print the polling results in a formatted way.
        
        Args:
            results: List of result dictionaries
            show_details: Whether to show detailed information
        """
        print(f"\n{'='*80}")
        print(f"URL POLLING RESULTS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*80}")
        
        up_count = sum(1 for r in results if r['status'] == 'up')
        total_count = len(results)
        
        print(f"Summary: {up_count}/{total_count} URLs are responding")
        print()
        
        # Status symbols
        status_symbols = {
            'up': '✅',
            'down': '❌',
            'timeout': '⏰',
            'connection_error': '🔌',
            'redirect': '↗️',
            'client_error': '4️⃣',
            'server_error': '5️⃣',
            'error': '❌',
            'unknown': '❓'
        }
        
        for result in results:
            symbol = status_symbols.get(result['status'], '❓')
            print(f"{symbol} {result['name']:<30} | {result['url']:<50}")
            
            if show_details:
                if result['status_code']:
                    print(f"   Status Code: {result['status_code']}")
                if result['response_time']:
                    print(f"   Response Time: {result['response_time']}ms")
                if result['error']:
                    print(f"   Error: {result['error']}")
                print()

def main():
    # Example URL dictionary
    # You can modify this or load from a file
    urls = [
    {"url": "https://www.google.com", "caption": "Google"},
    {"url": "https://www.amazon.com", "caption": "Amazon"},
    {"url": "https://www.github.com", "caption": "Github"},
]
    
    # Initialize poller
    poller = URLPoller(timeout=10, max_workers=5)
    
    print("Starting URL polling...")
    print(f"Checking {len(urls)} URLs with {poller.max_workers} concurrent workers")
    
    # Poll URLs
    urls_dict = {}
    for item in urls:
        url = item['url']
        caption = item['caption']
        urls_dict[caption] = url
    print(urls_dict)
    results = poller.poll_urls(urls_dict)
    
    # Print results
    poller.print_results(results)
    
    # Optionally save results to JSON file
    output_file = f"url_poll_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {output_file}")
    
    # Return exit code based on results
    failed_count = sum(1 for r in results if r['status'] not in ['up', 'redirect'])
    return failed_count

def load_urls_from_file(filename: str) -> Dict[str, str]:
    """
    Load URLs from a JSON file.
    
    Expected format:
    {
        "name1": "https://example1.com",
        "name2": "https://example2.com"
    }
    """
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in file '{filename}'")
        sys.exit(1)

if __name__ == "__main__":
    # Example of how to use with command line arguments
    if len(sys.argv) > 1:
        # Load URLs from file if provided
        urls = load_urls_from_file(sys.argv[1])
        urls_dict = {}
        for item in urls:
            url = item['url']
            caption = item['caption']
            urls_dict[caption] = url
        print(urls_dict)
        poller = URLPoller(timeout=10, max_workers=5)
        results = poller.poll_urls(urls_dict)
        poller.print_results(results)
        
        # Save results
        output_file = f"url_poll_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to: {output_file}")
    else:
        # Run with example URLs
        exit_code = main()
        sys.exit(exit_code)
