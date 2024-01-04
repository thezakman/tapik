#!/usr/bin/env python3

import requests
import argparse
import json

def banner():
    banner = """
    
 _              _ _    
| | @thezakman (_) | v0.4   
| |_ __ _ _ __  _| | __
| __/ _` | '_ \| | |/ /
| || (_| | |_) | |   < 
 \__\__,_| .__/|_|_|\_\\
   - TEST| |API KEYS -          
         |_|
    """
    print(banner)

def process_response(response, verbose):
    error_messages = ["PERMISSION_DENIED", "INVALID_ARGUMENT", "REQUEST_DENIED", "REJECTED", "BLOCKED", "BAD REQUEST"]
    for error_message in error_messages:
        if error_message in response.text.upper():
            return error_message  # Return the specific error message
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

def test_google_street_view_static_api(api_key, verbose):
    url = f"https://maps.googleapis.com/maps/api/streetview?size=400x400&location=46.414382,10.013988&key={api_key}"
    response = requests.get(url)
    return process_response(response, verbose)

def test_google_cloud_storage_api(api_key, verbose):
    url = f"https://www.googleapis.com/storage/v1/b/myproject/iam?key={api_key}" #myproject
    response = requests.get(url)
    return process_response(response, verbose)

def test_google_drive_api(api_key, verbose):
    url = f"https://www.googleapis.com/drive/v3/files?key={api_key}"
    response = requests.get(url)
    return process_response(response, verbose)

def test_google_sheets_api(api_key, verbose):
    url = f"https://sheets.googleapis.com/v4/spreadsheets/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/values/Class%20Data?key={api_key}"
    response = requests.get(url)
    return process_response(response, verbose)

def test_google_vision_api(api_key, verbose):
    url = "https://vision.googleapis.com/v1/images:annotate"
    headers = {"X-Goog-Api-Key": api_key, "Content-Type": "application/json"}
    data = {
        "requests": [
            {
                "image": {
                    "source": {
                        "imageUri": "https://64.media.tumblr.com/fc25fe4f65bc3d59cd7d51c98978bbc1/018960ee17970ed1-29/s128x128u_c1/a52339ef99aa53482b6719e226b03f47a87cee31.pnj"  # URL da imagem
                    }
                },
                "features": [
                    {"type": "LABEL_DETECTION"}  # Tipo de análise, e.g., detecção de rótulos
                ]
            }
        ]
    }
    response = requests.post(url, json=data, headers=headers)
    return process_response(response, verbose)


def test_api_keys(api_keys, verbose, output_file=None):
    api_results = {}
    for key in api_keys:
        api_results[key] = {}
        spacer = "─" * 60
        title = "Testing API Key:"
        top = len(title + key) + 3
        top2 = "─" * top
        print(f"╭{top2}╮")
        print(f"│ {title} {key} │")
        print(f"╰{top2}╯")

        def print_test_result(api_name, test_function):
            error_messages = ["PERMISSION_DENIED", "INVALID_ARGUMENT", "REQUEST_DENIED", "REJECTED", "BLOCKED", "BAD REQUEST"]
            result = test_function(key, verbose)
            
            if result in error_messages:
                status = f"❌ [{result}]"
                print(f"{status} | {api_name}")
            else:
                status = "✅ [WORKED]"
                print(f"{status} | {api_name}")
                api_results[key][api_name] = result
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
        print_test_result("Google Street View Static API", test_google_street_view_static_api)
        print_test_result("Google Cloud Storage API", test_google_cloud_storage_api)
        print_test_result("Google Drive API", test_google_drive_api)
        print_test_result("Google Sheets API", test_google_sheets_api)
        print_test_result("Google Vision API", test_google_vision_api)
    
    if output_file and api_results:
        with open(output_file, 'w') as file:
            json.dump(api_results, file, indent=4)
        print(f"[!] Results saved to: {output_file}")

def main():
    try:
        parser = argparse.ArgumentParser(description='Test Google API keys')
        parser.add_argument('-k', '--key', help='Single API key to test')
        parser.add_argument('-l', '--list', help='File containing list of API keys, one per line')
        parser.add_argument('-v', '--verbose', action='store_true', help='Print full responses for successful tests')
        parser.add_argument('-o', '--output', help='Output file to save the results')

        args = parser.parse_args()

        if args.key:
            test_api_keys([args.key], args.verbose, args.output)
        elif args.list:
            with open(args.list, 'r') as file:
                keys = file.read().splitlines()
                print(f"[Total of keys]: {len(keys)}")               
                test_api_keys(keys, args.verbose, args.output)
        else:
            print("No API key or list provided. Use -k to provide a single key or -l to provide a list of keys.")
    
    except KeyboardInterrupt:
        print("\n[!] Exiting...")
        exit(0)

if __name__ == "__main__":
    banner()
    main()