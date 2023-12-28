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
    error_messages = ["PERMISSION_DENIED", "INVALID_ARGUMENT", "REQUEST_DENIED"]
    if any(error_message in response.text for error_message in error_messages):
        return "PERMISSION_DENIED"
    else:
        return response.text if verbose else "WORKED"

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

def test_google_places_api(api_key, verbose):
    url = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?key={api_key}&input=Museum%20of%20Contemporary%20Art%20Australia&inputtype=textquery"
    response = requests.get(url)
    return process_response(response, verbose)

def test_google_time_zone_api(api_key, verbose):
    url = f"https://maps.googleapis.com/maps/api/timezone/json?key={api_key}&location=34.052235,-118.243683&timestamp=1331161200"
    response = requests.get(url)
    return process_response(response, verbose)

def test_google_civic_information_api(api_key, verbose):
    url = f"https://www.googleapis.com/civicinfo/v2/representatives?key={api_key}&address=1600%20Amphitheatre%20Parkway%20Mountain%20View%2C%20CA%2094043"
    response = requests.get(url)
    return process_response(response, verbose)

def test_google_blogger_api(api_key, verbose):
    url = f"https://www.googleapis.com/blogger/v3/blogs/2399953?key={api_key}"
    response = requests.get(url)
    return process_response(response, verbose)

def test_google_fonts_api(api_key, verbose):
    url = f"https://www.googleapis.com/webfonts/v1/webfonts?key={api_key}"
    response = requests.get(url)
    return process_response(response, verbose)

def test_api_keys(api_keys, verbose):
    for key in api_keys:
        spacer = "─" * 60
        title = "Testing API Key:"
        top = len(title + key) + 3
        top2 = "─" * top
        print(f"╭{top2}╮")
        print(f"│ {title} {key} │")
        print(f"╰{top2}╯")

        def print_test_result(api_name, test_function):
            error_messages = ["PERMISSION_DENIED", "INVALID_ARGUMENT", "REQUEST_DENIED"]
            result = test_function(key, verbose)
            
            if result in error_messages:
                status = "❌ [DENIED]"
                print(f"{status} | {api_name}")
            else:
                status = "✅ [WORKED]"
                print(f"{status} | {api_name}")
                if verbose:
                    print(result)
            print(spacer)
            
        print_test_result("Google Natural Language API", test_google_natural_language_api)
        print_test_result("Google Maps Geocoding API", test_google_maps_geocoding_api)
        print_test_result("Google Books API", test_google_books_api)
        print_test_result("Google YouTube Data API", test_google_youtube_api)
        print_test_result("Google Custom Search API", test_google_custom_search_api)
        print_test_result("Google Translate API", test_google_translate_api)
        print_test_result("Google Places API", test_google_places_api)
        print_test_result("Google Time Zone API", test_google_time_zone_api)
        print_test_result("Google Civic Information API", test_google_civic_information_api)
        print_test_result("Google Blogger API", test_google_blogger_api)
        print_test_result("Google Fonts API", test_google_fonts_api)

        #print(spacer)

def main():
    try:
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
                print(f"[Total of keys]: {len(keys)}")
               
                test_api_keys(keys, args.verbose)

                #Debugging output
                '''
                print("Keys read from file:")
                for k in keys:
                    print(f"'{k}'")
                '''
        else:
            print("No API key or list provided. Use -k to provide a single key or -l to provide a list of keys.")
    
    except KeyboardInterrupt:
        print("\n[!] Exiting...")
        exit(0)

if __name__ == "__main__":
    banner()
    main()