## URL Checker
simple tool to check if a url is responding or not along with time taken for response 
the status is stored as a json file additionally which can be consumed 

## Usage

Create a file with all urls to validate using the format
```
[
    {"url": "https://www.google.com", "caption": "Google"},
    {"url": "https://www.amazon.com", "caption": "Amazon"},
    {"url": "https://www.github.com", "caption": "Github"},
    {"url": "https://www.meta.com", "caption": "Meta"},
]
```

further use that as an input argument to the script `url_poller.py` 

```
python3 url_poller.py url_list
```

### Outputs

The below will be in STDOUT but the same captured as a json file stored

================================================================================
URL POLLING RESULTS - 2025-09-07 12:20:14
================================================================================
Summary: 4/4 URLs are responding

✅ Amazon                         | https://www.amazon.com
   Status Code: 200
   Response Time: 107.94ms

✅ Github                         | https://www.github.com
   Status Code: 200
   Response Time: 211.22ms

✅ Google                         | https://www.google.com
   Status Code: 200
   Response Time: 132.67ms

✅ Meta                           | https://www.meta.com
   Status Code: 200
   Response Time: 649.4ms
