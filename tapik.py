#!/usr/bin/env python3

import requests
import argparse

def banner():
    banner = """
    
 _              _ _    
| | @thezakman (_) |   
| |_ __ _ _ __  _| | __
| __/ _` | '_ \| | |/ /
| || (_| | |_) | |   < 
 \__\__,_| .__/|_|_|\_\\
         | |           
  - TEST |_| API KEYS           
    """
    print(banner)

def process_response(response, verbose):
    if "PERMISSION_DENIED" in response.text:
        return "PERMISSION_DENIED"
    else:
        return "WORKED" if not verbose else response.text

def test_google_natural_language_api(api_key, verbose):
    url = "https://language.googleapis.com/v1/documents:analyzeEntities"
    headers = {"X-Goog-Api-Key": api_key, "Content-Type": "application/json"}
    data = {"document": {"content": "The rain in Spain stays mainly in the plain.", "type": "PLAIN_TEXT"}}
    response = requests.post(url, json=data, headers=headers)
    return process_response(response, verbose)

def test_google_maps_geocoding_api(api_key, verbose):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?key={api_key}&address=Brazil"
    response = requests.get(url)
    return process_response(response, verbose)

def test_google_books_api(api_key, verbose):
    url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:0735619670&key={api_key}"
    response = requests.get(url)
    return process_response(response, verbose)

def test_google_youtube_api(api_key, verbose):
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q=python%20programming&key={api_key}"
    response = requests.get(url)
    return process_response(response, verbose)

def test_google_custom_search_api(api_key, verbose):
    url = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx=017576662512468239146:omuauf_lfve&q=lectures"
    response = requests.get(url)
    return process_response(response, verbose)

def test_google_translate_api(api_key, verbose):
    url = "https://translation.googleapis.com/language/translate/v2/detect"
    headers = {"X-Goog-Api-Key": api_key, "Content-Type": "application/json"}
    data = {"q": "Hola, ¿cómo estás?"} # Cabrón!
    response = requests.post(url, json=data, headers=headers)
    return process_response(response, verbose)



def test_api_keys(api_keys, verbose):
    for key in api_keys:
        spacer = "─"*50
        title = "Testing API Key:"
        top = len(title+key)+3
        top2 = "─"*top
        print (f"╭{top2}╮")
        print(f"│ {title} {key} │")
        print (f"╰{top2}╯")

        print(spacer)
        print("[*] | Google Natural Language API:", test_google_natural_language_api(key, verbose))
        print(spacer)
        print("[*] | Google Maps Geocoding API:", test_google_maps_geocoding_api(key, verbose))
        print(spacer)
        print("[*] | Google Books API:", test_google_books_api(key, verbose))
        print(spacer)
        print("[*] | Google YouTube Data API:", test_google_youtube_api(key, verbose))
        print(spacer)
        print("[*] | Google Custom Search API:", test_google_custom_search_api(key, verbose))
        print(spacer)
        print("[*] | Google Translate API:", test_google_translate_api(key, verbose))
        
        print(spacer)

def main():
    parser = argparse.ArgumentParser(description='Test Google API keys')
    parser.add_argument('-k', '--key', help='Single API key to test')
    parser.add_argument('-l', '--list', help='File containing list of API keys, one per line')
    parser.add_argument('-v', '--verbose', action='store_true', help='Print full responses for successful tests')

    args = parser.parse_args()

    if args.key:
        test_api_keys([args.key], args.verbose)
    elif args.list:
        with open(args.list, 'r') as file:
            keys = file.read().splitlines()
            test_api_keys(keys, args.verbose)
    else:
        print("No API key or list provided. Use -k to provide a single key or -l to provide a list of keys.")

if __name__ == "__main__":
    banner()
    main()
