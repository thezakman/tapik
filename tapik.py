#!/usr/bin/env python3.11
#import webbrowser
import requests
import argparse
import json
import warnings
from urllib3.exceptions import InsecureRequestWarning

# Suprimir apenas o NotOpenSSLWarning
warnings.filterwarnings("ignore", category=InsecureRequestWarning)

VERSION = "v0.8.1"

def banner():
    banner = f"""
    
 _              _ _    
| | @thezakman (_) | {VERSION}
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

#"1. APIKey Google Apis Consumersearch 5$ Per 1000 Request"
def test_google_maps_api_Consumersearch(api_key, verbose):
    url = f"https://www.googleapis.com/customsearch/v1?cx=017576662512468239146:omuauf_lfve&q=lectures&key={api_key}"
    response = requests.get(url)
    return process_response(response, verbose)

#"2. APIKey Staticmap $2 Per 1000 Request"
def test_google_maps_api_Staticmap(api_key, verbose):
    url = f"https://maps.googleapis.com/maps/api/staticmap?center=45%2C10&zoom=7&size=400x400&key={api_key}"
    response = requests.get(url)
    # Check if the response is an image
    if response.headers['Content-Type'].startswith('image/'):
        if verbose:
            #webbrowser.open(response.url)
            return f"[!] Image URL: {response.url}"
    return process_response(response, verbose)


#"3. APIKey Streetview $7 Per 1000 Request"
def test_google_maps_api_Streetview(api_key, verbose):
#   url = f"https://maps.googleapis.com/maps/api/streetview?size=400x400&location=46.414382,10.013988&key={api_key}"
    url = f"https://maps.googleapis.com/maps/api/streetview?size=400x400&location=40.720032,-73.988354&fov=90&heading=235&pitch=10&key={api_key}"
    response = requests.get(url)
    # Check if the response is an image
    if response.headers['Content-Type'].startswith('image/'):
        if verbose:
            #webbrowser.open(response.url)
            return f"[!] Image URL: {response.url}"
    return process_response(response, verbose)

#"4. APIKey Direction $10 Per 1000 Request"
def test_google_maps_api_Directions(api_key, verbose):
    url = f"https://maps.googleapis.com/maps/api/directions/json?origin=Disneyland&destination=Universal+Studios+Hollywood4&key={api_key}"
    response = requests.get(url)
    return process_response(response, verbose)

#"5. APIKey Geocode $10 Per 1000 Request"
def test_google_maps_api_geocode(api_key, verbose):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?key={api_key}&address=Brazil"
    response = requests.get(url)
    return process_response(response, verbose)

#"6. APIKey Distance Matrix $10 Per 1000 Request"
def test_google_maps_api_Distancematrix(api_key, verbose):
    url = f"https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&origins=40.6655101,-73.89188969999998&destinations=40.6905615%2C-73.9976592%7C40.6905615%2C-73.9976592%7C40.6905615%2C-73.9976592%7C40.6905615%2C-73.9976592%7C40.6905615%2C-73.9976592%7C40.6905615%2C-73.9976592%7C40.659569%2C-73.933783%7C40.729029%2C-73.851524%7C40.6860072%2C-73.6334271%7C40.598566%2C-73.7527626%7C40.659569%2C-73.933783%7C40.729029%2C-73.851524%7C40.6860072%2C-73.6334271%7C40.598566%2C-73.7527626&key={api_key}"
    response = requests.get(url)
    return process_response(response, verbose)
    
#"7. APIKey Find Place From Text $17 Per 1000 Request"
def test_google_maps_api_Findplacefromtext(api_key, verbose):
    url = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input=Restaurante+Quinta+Brasil&inputtype=textquery&fields=photos,formatted_address,name,rating,opening_hours,geometry&key={api_key}"
    response = requests.get(url)
    return process_response(response, verbose)

#"8. APIKey Autocomplete $3 Per 1000 Request"
def test_google_maps_api_Autocomplete(api_key, verbose):
    url = f"https://maps.googleapis.com/maps/api/place/autocomplete/json?input=Bingh&types=%28cities%29&key={api_key}"
    response = requests.get(url)
    return process_response(response, verbose)

#"9. APIKey Elevation $5 Per 1000 Request"
def test_google_maps_api_elevation(api_key, verbose):
    url = f"https://maps.googleapis.com/maps/api/elevation/json?locations=39.7391536,-104.9847034&key={api_key}"
    response = requests.get(url)
    return process_response(response, verbose)

#"10. APIKey Timezone $5 Per 1000 Request"
def test_google_maps_api_Timezone(api_key, verbose):
#   url = f"https://maps.googleapis.com/maps/api/timezone/json?key={api_key}&location=34.052235,-118.243683&timestamp=1331161200"
    url = f"https://maps.googleapis.com/maps/api/timezone/json?location=39.6034810,-119.6822510&timestamp=1331161200&key={api_key}"
    response = requests.get(url)
    return process_response(response, verbose)

#"11. APIKey Nearest Roards $10 Per 1000 Request"
def test_google_maps_api_NearestRoads(api_key, verbose):
    url = f"https://roads.googleapis.com/v1/nearestRoads?points=60.170880,24.942795|60.170879,24.942796|60.170877,24.942796&key={api_key}"
    response = requests.get(url)
    return process_response(response, verbose)

#"12. APIKey Geolocation $5 Per 1000 Request"
def test_google_maps_api_geolocate(api_key, verbose):
    url = f"https://www.googleapis.com/geolocation/v1/geolocate?key={api_key}"
    headers = {'Content-Type': 'application/json'}

    data = {
        "homeMobileCountryCode": 310,
        "homeMobileNetworkCode": 410,
        "radioType": "gsm",
        "carrier": "Vodafone",
        "considerIp": True
    }
    response = requests.post(url, json=data, headers=headers)
    return process_response(response, verbose)

#"13. APIKey Route to Traveled $10 Per 1000 Request"
def test_google_maps_api_SnapToRoads(api_key, verbose):
    url = f"https://roads.googleapis.com/v1/snapToRoads?path=-35.27801,149.12958|-35.28032,149.12907&interpolate=true&key={api_key}"
    response = requests.get(url)
    return process_response(response, verbose)

#"14. APIKey Speed Limit Roads $20 Per 1000 Request"
def test_google_maps_api_SpeedLimits(api_key, verbose):
    url = f"https://roads.googleapis.com/v1/speedLimits?path=38.75807927603043,-9.03741754643809&key={api_key}"
    response = requests.get(url)
    return process_response(response, verbose)

#"15. APIKey Place Detail $17 Per 1000 Request"
def test_google_maps_api_place_detais(api_key, verbose):
    url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id=ChIJN1t_tDeuEmsRUsoyG83frY4&fields=name,rating,formatted_phone_number&key={api_key}"
    response = requests.get(url)
    return process_response(response, verbose)

#"16. Tests the Google Natural Language API"
def test_google_natural_language_api(api_key, verbose):
    url = "https://language.googleapis.com/v1/documents:analyzeEntities"
    headers = {"X-Goog-Api-Key": api_key, "Content-Type": "application/json"}
    data = {"document": {"content": "The rain in Spain stays mainly in the plain.", "type": "PLAIN_TEXT"}}
    response = requests.post(url, json=data, headers=headers)
    return process_response(response, verbose)

#"17. Tests the Google Books API"
def test_google_books_api(api_key, verbose):
    url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:0735619670&key={api_key}"
    response = requests.get(url)
    return process_response(response, verbose)

#"18. Tests the Google YouTube API"
def test_google_youtube_api(api_key, verbose):
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q=python%20programming&key={api_key}"
    response = requests.get(url)
    return process_response(response, verbose)

#"19. Tests the Google Search API"
def test_google_custom_search_api(api_key, verbose):
    url = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx=017576662512468239146:omuauf_lfve&q=lectures"
    response = requests.get(url)
    return process_response(response, verbose)

#"20. Tests the Google Translate API"
def test_google_translate_api(api_key, verbose):
    url = "https://translation.googleapis.com/language/translate/v2/detect"
    headers = {"X-Goog-Api-Key": api_key, "Content-Type": "application/json"}
    data = {"q": "Hola, ¿cómo estás?"} # Cabrón!
    response = requests.post(url, json=data, headers=headers)
    return process_response(response, verbose)

#"21. Tests the Google Civic API"
def test_google_civic_information_api(api_key, verbose):
    url = f"https://www.googleapis.com/civicinfo/v2/representatives?key={api_key}&address=1600%20Amphitheatre%20Parkway%20Mountain%20View%2C%20CA%2094043"
    response = requests.get(url)
    return process_response(response, verbose)

#"22. Tests the Google Blogger API"
def test_google_blogger_api(api_key, verbose):
    url = f"https://www.googleapis.com/blogger/v3/blogs/2399953?key={api_key}"
    response = requests.get(url)
    return process_response(response, verbose)

#"23. Tests the Google WebFonts API"
def test_google_fonts_api(api_key, verbose):
    url = f"https://www.googleapis.com/webfonts/v1/webfonts?key={api_key}"
    response = requests.get(url)
    return process_response(response, verbose)

#"24. Tests the Google Cloud Storage API"
def test_google_cloud_storage_api(api_key, verbose):
    url = f"https://www.googleapis.com/storage/v1/b/myproject/iam?key={api_key}" #myproject
    response = requests.get(url)
    return process_response(response, verbose)

#"25. Tests the Google Drive API"
def test_google_drive_api(api_key, verbose):
    url = f"https://www.googleapis.com/drive/v3/files?key={api_key}"
    response = requests.get(url)
    return process_response(response, verbose)

#"26. Tests the Google Sheet API"
def test_google_sheets_api(api_key, verbose):
    url = f"https://sheets.googleapis.com/v4/spreadsheets/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/values/Class%20Data?key={api_key}"
    response = requests.get(url)
    return process_response(response, verbose)

#"27. Tests the Google Vision API"
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
                    {"type": "DOCUMENT_TEXT_DETECTION"}  
                    # Tipo de análise: FACE_DETECTION, LABEL_DETECTION, LANDMARK_DETECTION
                    # LOGO_DETECTION, SAFE_SEARCH_DETECTION, IMAGE_PROPERTIES, CROP_HINTS, WEB_DETECTION
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

        # Google Maps
        print_test_result("Google Maps API - Autocomplete", test_google_maps_api_Autocomplete)
        print_test_result("Google Maps API - Consumer Search", test_google_maps_api_Consumersearch)
        print_test_result("Google Maps API - Directions", test_google_maps_api_Directions)
        print_test_result("Google Maps API - Distance Matrix", test_google_maps_api_Distancematrix)
        print_test_result("Google Maps API - Elevation", test_google_maps_api_elevation)
        print_test_result("Google Maps API - Find Place From Text", test_google_maps_api_Findplacefromtext)
        print_test_result("Google Maps API - Geolocation", test_google_maps_api_geolocate)
        print_test_result("Google Maps API - Nearest Roads", test_google_maps_api_NearestRoads)
        print_test_result("Google Maps API - Places Details", test_google_maps_api_place_detais)
        print_test_result("Google Maps API - Snap To Roads", test_google_maps_api_SnapToRoads)
        print_test_result("Google Maps API - Speed Limit Roads", test_google_maps_api_SpeedLimits)
        print_test_result("Google Maps API - StaticMap", test_google_maps_api_Staticmap)
        print_test_result("Google Maps API - StreetView", test_google_maps_api_Streetview)
        print_test_result("Google Maps API - Timezone", test_google_maps_api_Timezone)

        # Extra Apis
        print_test_result("Google Blogger API", test_google_blogger_api)
        print_test_result("Google Books API", test_google_books_api)
        print_test_result("Google Civic Information API", test_google_civic_information_api)
        print_test_result("Google Custom Search API", test_google_custom_search_api)
        print_test_result("Google Fonts API", test_google_fonts_api)
        print_test_result("Google Natural Language API", test_google_natural_language_api)
        print_test_result("Google Translate API", test_google_translate_api)
        print_test_result("Google YouTube Data API", test_google_youtube_api)
        
        print_test_result("Google Drive API", test_google_drive_api)
        print_test_result("Google Sheets API", test_google_sheets_api)
        print_test_result("Google Vision API", test_google_vision_api)

        ''' Neet to invest more into this'''
        #print_test_result("Google Cloud Storage API", test_google_cloud_storage_api)
    
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