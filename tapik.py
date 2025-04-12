#!/usr/bin/env python3.11
import requests
import argparse
import json
import warnings
import logging
import time
from dataclasses import dataclass
from typing import Dict, List, Optional
from urllib3.exceptions import InsecureRequestWarning
from colorama import init, Fore, Back, Style

# Initialize colorama (required for Windows)
init(autoreset=True)

class Colors:
    """Define colors and styles for terminal output"""
    HEADER = Fore.CYAN
    SUCCESS = Fore.GREEN
    ERROR = Fore.RED
    WARNING = Fore.YELLOW
    INFO = Fore.BLUE
    RESET = Style.RESET_ALL
    BOLD = Style.BRIGHT

# Suppress InsecureRequestWarning to keep output clean
warnings.filterwarnings("ignore", category=InsecureRequestWarning)

VERSION = "v0.8.7"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

@dataclass
class ApiTestResult:
    """Stores the result of an API test"""
    api_name: str
    status: bool
    message: str
    response_data: Optional[str] = None

class RateLimiter:
    """Implements rate limiting for API requests"""
    def __init__(self, calls: int = 1, period: int = 1):
        self.calls = calls
        self.period = period
        self.timestamps = []

    def wait(self):
        """Waits if necessary to respect the rate limit"""
        now = time.time()
        self.timestamps = [t for t in self.timestamps if now - t <= self.period]
        
        if len(self.timestamps) >= self.calls:
            sleep_time = self.timestamps[0] + self.period - now
            if (sleep_time > 0):
                time.sleep(sleep_time)
        
        self.timestamps.append(now)

class ApiTester:
    """Base class for API testing"""
    ERROR_MESSAGES = [
        "UNAUTHENTICATED",
        "PERMISSION_DENIED", 
        "INVALID_ARGUMENT",
        "REQUEST_DENIED",
        "REJECTED",
        "BLOCKED",
        "BAD REQUEST",
        "INSUFFICIENTFILEPERMISSIONS",
        "ADMIN_ONLY_OPERATION"
    ]
    
    def __init__(self):
        self.rate_limiter = RateLimiter(calls=10, period=1)  # 10 calls per second
        
    def test_api_keys(self, api_keys: List[str], verbose: bool = False) -> Dict[str, Dict[str, ApiTestResult]]:
        """
        Tests a list of API keys
        
        Args:
            api_keys: List of keys to test
            verbose: If True, shows detailed responses
            
        Returns:
            Dictionary with test results
        """
        results = {}
        
        for key in api_keys:
            results[key] = {}
            self._print_key_header(key)
            
            for api_name, test_func in self._get_test_functions().items():
                try:
                    self.rate_limiter.wait()
                    result = self._run_test(api_name, test_func, key, verbose)
                    results[key][api_name] = result
                    self._print_result(result)
                except Exception as e:
                    logging.error(f"Error testing {api_name}: {str(e)}")
                    
        return results

    def _run_test(self, api_name: str, test_func, key: str, verbose: bool) -> ApiTestResult:
        """Runs an individual API test"""
        result = test_func(key, verbose)
        
        if result in self.ERROR_MESSAGES:
            return ApiTestResult(
                api_name=api_name,
                status=False,
                message=result
            )
            
        return ApiTestResult(
            api_name=api_name,
            status=True,
            message="WORKED",
            response_data=result if verbose else None
        )

    def _print_key_header(self, key: str):
        """Prints a colored header for each key"""
        title = "Testing API Key:"
        top = len(title + key) + 3
        top2 = "─" * top
        print(f"{Colors.HEADER}╭{top2}╮")
        print(f"{Colors.HEADER}│ {Colors.BOLD}{title} {key} {Colors.RESET + Colors.HEADER}│") 
        print(f"{Colors.HEADER}╰{top2}╯{Colors.RESET}")

    def _print_result(self, result: ApiTestResult):
        """Prints a colored test result"""
        if result.status:
            status = f"{Colors.SUCCESS}✅ [WORKED]{Colors.RESET}"
        else:
            status = f"{Colors.ERROR}❌ [{result.message}]{Colors.RESET}"
            
        print(f"{status} | {Colors.BOLD}{result.api_name}{Colors.RESET}")
        
        if result.response_data:
            print(f"{Colors.INFO}{result.response_data}{Colors.RESET}")
            
        print(f"{Colors.HEADER}{'─' * 60}{Colors.RESET}")

def banner():
    """Displays a colorful program banner"""
    banner = f"""
{Colors.BOLD + Colors.SUCCESS}    
 _              _ _    
| | {Colors.RESET}@thezakman{Colors.BOLD + Colors.SUCCESS} (_) | {Colors.RESET + Colors.WARNING}{VERSION}{Colors.BOLD + Colors.SUCCESS}  
| |_ __ _ _ __  _| | __
| __/ _` | '_ \\| | |/ /
| || (_| | |_) | |   < 
 \\__\\__,_| .__/|_|_|\\_\\
   {Colors.WARNING}- TEST{Colors.BOLD + Colors.SUCCESS}| |{Colors.WARNING}API KEYS -{Colors.BOLD + Colors.SUCCESS}
         |_|
{Colors.RESET}"""
    print(banner)

def process_response(response, verbose):
    """Processes API response and checks for error messages"""
    # Verifica se a resposta contém HTML da página de erro do Google
    if "<html>" in response.text and "We're sorry..." in response.text:
        return "BLOCKED"  # Identificamos que o Google está bloqueando a solicitação
        
    error_messages = ["ADMIN_ONLY_OPERATION", "UNAUTHENTICATED", "PERMISSION_DENIED", "INVALID_ARGUMENT", "REQUEST_DENIED", 
                      "REJECTED", "BLOCKED", "BAD REQUEST", "INSUFFICIENTFILEPERMISSIONS"]
    for error_message in error_messages:
        if error_message in response.text.upper():
            return error_message  # Return the specific error message
    # Verificar por códigos de erro HTTP específicos ou padrões de erro no JSON
    if response.status_code >= 400:
        try:
            # Tenta analisar a resposta como JSON para verificar erros específicos
            response_json = response.json()
            
            # Verifica se há estrutura de erro na resposta JSON
            if 'error' in response_json:
                # Casos específicos de autenticação que são falhas claras
                if 'message' in response_json['error'] and (
                    'authentication' in response_json['error']['message'].lower() or
                    'required' in response_json['error']['message'].lower() or
                    'configured for first-party' in response_json['error']['message'].lower()
                ):
                    return "PERMISSION_DENIED"
        except:
            # Se não conseguiu analisar JSON ou ocorreu outro erro
            pass
    # Se não houver erros, retorna o texto da resposta    
    return response.text if verbose else "WORKED"

#"""Google Maps and Location"""
def test_google_maps_api_geocode(api_key, verbose):
    #"""1. Google Maps API - Geocode - $10 per 1000 requests"""
    url = f"https://maps.googleapis.com/maps/api/geocode/json?key={api_key}&address=Brazil"
    response = requests.get(url)
    return process_response(response, verbose)

def test_google_maps_places_nearby(api_key, verbose):
    #"""2. Google Maps API - Places Nearby - $32 per 1000 requests"""
    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=-33.8670522,151.1957362&radius=500&type=restaurant&key={api_key}"
    response = requests.get(url)
    return process_response(response, verbose)

def test_google_maps_api_place_detais(api_key, verbose):
    #"""3. Google Maps API - Place Details - $17 per 1000 requests"""
    url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id=ChIJN1t_tDeuEmsRUsoyG83frY4&fields=name,rating,formatted_phone_number&key={api_key}"
    response = requests.get(url)
    return process_response(response, verbose)

def test_google_maps_places_photos_api(api_key, verbose):
    #"""4. Google Maps API - Places Photos"""
    """First we need to get a valid photo reference"""
    search_url = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input=Empire%20State%20Building&inputtype=textquery&fields=photos&key={api_key}"
    search_response = requests.get(search_url)
    search_data = json.loads(search_response.text)
    
    if 'candidates' in search_data and len(search_data['candidates']) > 0:
        if 'photos' in search_data['candidates'][0]:
            photo_reference = search_data['candidates'][0]['photos'][0]['photo_reference']
            url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photo_reference={photo_reference}&key={api_key}"
            response = requests.get(url)
            return process_response(response, verbose)
    return "BAD REQUEST"

def test_google_maps_api_Findplacefromtext(api_key, verbose):
    #"""5. Google Maps API - Find Place From Text - $17 per 1000 requests"""
    url = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input=Restaurant+Quinta+Brasil&inputtype=textquery&fields=photos,formatted_address,name,rating,opening_hours,geometry&key={api_key}"
    response = requests.get(url)
    return process_response(response, verbose)

def test_google_maps_api_Autocomplete(api_key, verbose):
    #"""6. Google Maps API - Autocomplete - $3 per 1000 requests"""
    url = f"https://maps.googleapis.com/maps/api/place/autocomplete/json?input=Bingh&types=%28cities%29&key={api_key}"
    response = requests.get(url)
    return process_response(response, verbose)

def test_google_maps_api_Staticmap(api_key, verbose):
    #"""7. Google Maps API - StaticMap - $2 per 1000 requests"""
    url = f"https://maps.googleapis.com/maps/api/staticmap?center=45%2C10&zoom=7&size=400x400&key={api_key}"
    response = requests.get(url)
    # Check if the response is an image
    if response.headers['Content-Type'].startswith('image/'):
        if verbose:
            return f"[!] Image URL: {response.url}"
    return process_response(response, verbose)

def test_google_maps_api_Streetview(api_key, verbose):
    #"""8. Google Maps API - StreetView - $7 per 1000 requests"""
    url = f"https://maps.googleapis.com/maps/api/streetview?size=400x400&location=40.720032,-73.988354&fov=90&heading=235&pitch=10&key={api_key}"
    response = requests.get(url)
    # Check if the response is an image
    if response.headers['Content-Type'].startswith('image/'):
        if verbose:
            return f"[!] Image URL: {response.url}"
    return process_response(response, verbose)

def test_google_maps_api_Directions(api_key, verbose):
    #"""9. Google Maps API - Directions - $10 per 1000 requests"""
    url = f"https://maps.googleapis.com/maps/api/directions/json?origin=Disneyland&destination=Universal+Studios+Hollywood4&key={api_key}"
    response = requests.get(url)
    return process_response(response, verbose)

def test_google_maps_api_Distancematrix(api_key, verbose):
    #"""10. Google Maps API - Distance Matrix - $10 per 1000 requests"""
    url = f"https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&origins=40.6655101,-73.89188969999998&destinations=40.6905615%2C-73.9976592%7C40.6905615%2C-73.9976592%7C40.6905615%2C-73.9976592%7C40.6905615%2C-73.9976592%7C40.6905615%2C-73.9976592%7C40.6905615%2C-73.9976592%7C40.659569%2C-73.933783%7C40.729029%2C-73.851524%7C40.6860072%2C-73.6334271%7C40.598566%2C-73.7527626%7C40.659569%2C-73.933783%7C40.729029%2C-73.851524%7C40.6860072%2C-73.6334271%7C40.598566%2C-73.7527626&key={api_key}"
    response = requests.get(url)
    return process_response(response, verbose)

def test_google_maps_api_elevation(api_key, verbose):
    #"""11. Google Maps API - Elevation - $5 per 1000 requests"""
    url = f"https://maps.googleapis.com/maps/api/elevation/json?locations=39.7391536,-104.9847034&key={api_key}"
    response = requests.get(url)
    return process_response(response, verbose)

def test_google_maps_api_Timezone(api_key, verbose):
    #"""12. Google Maps API - Timezone - $5 per 1000 requests"""
    url = f"https://maps.googleapis.com/maps/api/timezone/json?location=39.6034810,-119.6822510&timestamp=1331161200&key={api_key}"
    response = requests.get(url)
    return process_response(response, verbose)

def test_google_maps_api_geolocate(api_key, verbose):
    #"""13. Google Maps API - Geolocation - $5 per 1000 requests"""
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

#"""Google Roads APIs"""
def test_google_maps_api_NearestRoads(api_key, verbose):
    #"""14. Google Maps API - Nearest Roads - $10 per 1000 requests"""
    url = f"https://roads.googleapis.com/v1/nearestRoads?points=60.170880,24.942795|60.170879,24.942796|60.170877,24.942796&key={api_key}"
    response = requests.get(url)
    return process_response(response, verbose)

def test_google_maps_api_SnapToRoads(api_key, verbose):
    #"""15. Google Maps API - Snap To Roads - $10 per 1000 requests"""
    url = f"https://roads.googleapis.com/v1/snapToRoads?path=-35.27801,149.12958|-35.28032,149.12907&interpolate=true&key={api_key}"
    response = requests.get(url)
    return process_response(response, verbose)

def test_google_maps_api_SpeedLimits(api_key, verbose):
    """16. Google Maps API - Speed Limits - $20 per 1000 requests"""
    url = f"https://roads.googleapis.com/v1/speedLimits?path=38.75807927603043,-9.03741754643809&key={api_key}"
    response = requests.get(url)
    return process_response(response, verbose)

#"""Google Cloud AI & Machine Learning"""
def test_google_natural_language_api(api_key, verbose):
    #"""17. Google Cloud Natural Language API"""
    url = "https://language.googleapis.com/v1/documents:analyzeEntities"
    headers = {"X-Goog-Api-Key": api_key, "Content-Type": "application/json"}
    data = {"document": {"content": "The rain in Spain stays mainly in the plain.", "type": "PLAIN_TEXT"}}
    response = requests.post(url, json=data, headers=headers)
    return process_response(response, verbose)

def test_google_natural_language_sentiment(api_key, verbose):
    #"""18. Google Natural Language Sentiment API - $1 per 1000 requests"""
    url = "https://language.googleapis.com/v1/documents:analyzeSentiment"
    headers = {"X-Goog-Api-Key": api_key, "Content-Type": "application/json"}
    data = {
        "document": {
            "type": "PLAIN_TEXT",
            "content": "Google Cloud Natural Language API is fantastic!"
        },
        "encodingType": "UTF8"
    }
    response = requests.post(url, json=data, headers=headers)
    return process_response(response, verbose)

def test_google_vision_api(api_key, verbose):
    #"""19. Google Vision API"""
    url = "https://vision.googleapis.com/v1/images:annotate"
    headers = {"X-Goog-Api-Key": api_key, "Content-Type": "application/json"}
    data = {
        "requests": [
            {
                "image": {
                    "source": {
                        "imageUri": "https://64.media.tumblr.com/fc25fe4f65bc3d59cd7d51c98978bbc1/018960ee17970ed1-29/s128x128u_c1/a52339ef99aa53482b6719e226b03f47a87cee31.pnj"
                    }
                },
                "features": [
                    {"type": "DOCUMENT_TEXT_DETECTION"}
                ]
            }
        ]
    }
    response = requests.post(url, json=data, headers=headers)
    return process_response(response, verbose)

def test_google_cloud_text_to_speech_api(api_key, verbose):
    #"""20. Google Cloud Text-to-Speech API"""
    url = "https://texttospeech.googleapis.com/v1/text:synthesize"
    headers = {"X-Goog-Api-Key": api_key, "Content-Type": "application/json"}
    data = {
        "input": {"text": "Hello, world!"},
        "voice": {"languageCode": "en-US", "ssmlGender": "NEUTRAL"},
        "audioConfig": {"audioEncoding": "MP3"}
    }
    response = requests.post(url, json=data, headers=headers)
    return process_response(response, verbose)

def test_google_cloud_speech_to_text_api(api_key, verbose):
    #"""21. Google Cloud Speech-to-Text API"""
    url = "https://speech.googleapis.com/v1/speech:recognize"
    headers = {"X-Goog-Api-Key": api_key, "Content-Type": "application/json"}
    data = {
        "config": {
            "encoding": "LINEAR16",
            "sampleRateHertz": 16000,
            "languageCode": "en-US"
        },
        "audio": {
            "uri": "gs://cloud-samples-tests/speech/brooklyn.flac"
        }
    }
    response = requests.post(url, json=data, headers=headers)
    return process_response(response, verbose)

def test_google_cloud_video_intelligence_api(api_key, verbose):
    #"""22. Google Cloud Video Intelligence API"""
    url = "https://videointelligence.googleapis.com/v1/videos:annotate"
    headers = {"X-Goog-Api-Key": api_key, "Content-Type": "application/json"}
    data = {
        "inputContent": "base64_encoded_video",
        "features": ["LABEL_DETECTION"]
    }
    response = requests.post(url, json=data, headers=headers)
    return process_response(response, verbose)

def test_google_cloud_document_ai_api(api_key, verbose):
    #"""23. Google Cloud Document AI API"""
    url = "https://documentai.googleapis.com/v1/projects/-/locations/us-central1/processors"
    headers = {
        "X-Goog-Api-Key": api_key,
        "Content-Type": "application/json"
    }
    params = {
        "key": api_key
    }
    response = requests.get(url, headers=headers, params=params)
    return process_response(response, verbose)

#"""Google Translation & Language"""
def test_google_translate_api(api_key, verbose):
    #"""24. Google Translate API"""
    url = "https://translation.googleapis.com/language/translate/v2/detect"
    headers = {"X-Goog-Api-Key": api_key, "Content-Type": "application/json"}
    data = {"q": "Hola, ¿cómo estás?"}
    response = requests.post(url, json=data, headers=headers)
    return process_response(response, verbose)

def test_google_cloud_translation_api(api_key, verbose):
    #"""25. Google Cloud Translation API"""
    url = "https://translation.googleapis.com/language/translate/v2/languages"
    headers = {
        "X-Goog-Api-Key": api_key,
        "Content-Type": "application/json"
    }
    params = {
        "target": "pt",
        "key": api_key
    }
    response = requests.get(url, headers=headers, params=params)
    return process_response(response, verbose)

#"""Google Search & Content"""
def test_google_custom_search_api(api_key, verbose):
    #"""26. Google Custom Search API"""
    url = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx=017576662512468239146:omuauf_lfve&q=lectures"
    response = requests.get(url)
    return process_response(response, verbose)

def test_google_books_api(api_key, verbose):
    #"""27. Google Books API"""
    url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:0735619670&key={api_key}"
    response = requests.get(url)
    return process_response(response, verbose)

def test_google_youtube_api(api_key, verbose):
    #"""28. Google YouTube API"""
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q=python%20programming&key={api_key}"
    response = requests.get(url)
    return process_response(response, verbose)

def test_google_maps_api_Consumersearch(api_key, verbose):
    #"""29. Google Consumer Search"""
    url = f"https://www.googleapis.com/customsearch/v1?cx=017576662512468239146:omuauf_lfve&q=lectures&key={api_key}"
    response = requests.get(url)
    return process_response(response, verbose)

def test_google_fact_check_api(api_key, verbose):
    #"""30. Google Fact Check API - Free with limits"""
    url = f"https://factchecktools.googleapis.com/v1alpha1/claims:search?query=climate&key={api_key}"
    response = requests.get(url)
    return process_response(response, verbose)

def test_google_pagespeed_api(api_key, verbose):
    #"""31. Google PageSpeed Insights API - $0.15 per 1000 requests"""
    url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=https://google.com&key={api_key}"
    response = requests.get(url)
    return process_response(response, verbose)

def test_google_safe_browsing_api(api_key, verbose):
    #"""32. Google Safe Browsing API - $0.75 per 1000 requests"""
    url = f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    data = {
        "client": {"clientId": "test", "clientVersion": "1.0"},
        "threatInfo": {
            "threatTypes": ["MALWARE"],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": "http://example.com"}]
        }
    }
    response = requests.post(url, json=data, headers=headers)
    return process_response(response, verbose)

"""oogle Cloud Storage & Database"""
def test_google_cloud_storage_api(api_key, verbose):
    #"""33. Google Cloud Storage API"""
    url = f"https://storage.googleapis.com/storage/v1/b?project=my-project&key={api_key}"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key
    }
    try:
        response = requests.get(
            url,
            headers=headers,
            params={"maxResults": 1}
        )
        if response.status_code in [401, 403]:
            return "PERMISSION_DENIED"
        return process_response(response, verbose)
    except Exception as e:
        logging.error(f"Error testing Cloud Storage API: {str(e)}")
        return "BAD REQUEST"

def test_google_bigquery_api(api_key, verbose):
    #"""34. Google BigQuery API"""
    url = f"https://bigquery.googleapis.com/bigquery/v2/projects/my-project/queries?key={api_key}"
    data = {
        "query": "SELECT name FROM `bigquery-public-data.usa_names.usa_1910_2013` LIMIT 10"
    }
    response = requests.post(url, json=data)
    return process_response(response, verbose)

def test_google_cloud_datastore_api(api_key, verbose):
    #"""35. Google Cloud Datastore API"""
    url = f"https://datastore.googleapis.com/v1/projects/my-project:runQuery?key={api_key}"
    data = {
        "gqlQuery": {
            "queryString": "SELECT * FROM Task"
        }
    }
    response = requests.post(url, json=data)
    return process_response(response, verbose)

#"""Google Productivity & Organization"""
def test_google_drive_api(api_key, verbose):
    #"""36. Google Drive API"""
    url = f"https://www.googleapis.com/drive/v3/files?key={api_key}"
    response = requests.get(url)
    return process_response(response, verbose)

def test_google_sheets_api(api_key, verbose):
    #"""37. Google Sheets API"""
    url = f"https://sheets.googleapis.com/v4/spreadsheets/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/values/Class%20Data?key={api_key}"
    response = requests.get(url)
    return process_response(response, verbose)

def test_google_calendar_api(api_key, verbose):
    #"""38. Google Calendar API"""
    url = f"https://www.googleapis.com/calendar/v3/calendars/primary/events?key={api_key}"
    response = requests.get(url)
    return process_response(response, verbose)

def test_google_tasks_api(api_key, verbose):
    #"""39. Google Tasks API"""
    url = f"https://tasks.googleapis.com/tasks/v1/users/@me/lists?key={api_key}"
    response = requests.get(url)
    return process_response(response, verbose)

#"""Google Social & User Data"""
def test_google_people_api(api_key, verbose):
    #"""40. Google People API"""
    url = f"https://people.googleapis.com/v1/people/me?personFields=names,emailAddresses&key={api_key}"
    response = requests.get(url)
    return process_response(response, verbose)

def test_google_blogger_api(api_key, verbose):
    #"""41. Google Blogger API"""
    url = f"https://www.googleapis.com/blogger/v3/blogs/2399953?key={api_key}"
    response = requests.get(url)
    return process_response(response, verbose)

def test_google_civic_information_api(api_key, verbose):
    #"""42. Google Civic API"""
    url = f"https://www.googleapis.com/civicinfo/v2/representatives?key={api_key}&address=1600%20Amphitheatre%20Parkway%20Mountain%20View%2C%20CA%2094043"
    response = requests.get(url)
    return process_response(response, verbose)

#"""Google Design & Fonts"""
def test_google_fonts_api(api_key, verbose):
    """43. Google WebFonts API"""
    url = f"https://www.googleapis.com/webfonts/v1/webfonts?key={api_key}"
    response = requests.get(url)
    return process_response(response, verbose)

#"""Firebase APIs"""
def test_firebase_auth_api(api_key, verbose):
    """44. Firebase Authentication API - For managing user authentication"""
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    data = {}  # Corpo vazio é suficiente para testar a validade da chave
    
    response = requests.post(url, json=data, headers=headers)
    
    # Para o Firebase, um código 400 com mensagem específica indica que a chave é válida
    # mas faltam parâmetros (o que é esperado no nosso teste)
    if response.status_code == 400 and 'MISSING_EMAIL' in response.text:
        if verbose:
            return response.text
        return "WORKED"  # A chave é válida para o Firebase Auth
    
    return process_response(response, verbose)

def parse_api_selection(api_selection: str) -> list:
    """
    Converts the selection string to a list of API numbers
    Example: 
        "1,2,3" -> [1,2,3]
        "1-3" -> [1,2,3]
        "1" -> [1]
    """
    result = set()
    if not api_selection:
        return list(range(1,45))  # All APIs (1-45)
        
    parts = api_selection.split(',')
    for part in parts:
        if '-' in part:
            start, end = map(int, part.split('-'))
            result.update(range(start, end + 1))
        else:
            result.add(int(part))
    return sorted(list(result))

# API mapping organized by categories
def get_api_function_by_number(number: int):
    """Returns the test function corresponding to the API number, organized by categories"""
    api_functions = {
        # Google Maps and Location
        1: ("Google Maps API - Geocode", test_google_maps_api_geocode),
        2: ("Google Maps API - Places Nearby", test_google_maps_places_nearby),
        3: ("Google Maps API - Place Details", test_google_maps_api_place_detais),
        4: ("Google Maps API - Places Photos", test_google_maps_places_photos_api),
        5: ("Google Maps API - Find Place From Text", test_google_maps_api_Findplacefromtext),
        6: ("Google Maps API - Autocomplete", test_google_maps_api_Autocomplete),
        7: ("Google Maps API - StaticMap", test_google_maps_api_Staticmap),
        8: ("Google Maps API - StreetView", test_google_maps_api_Streetview),
        9: ("Google Maps API - Directions", test_google_maps_api_Directions),
        10: ("Google Maps API - Distance Matrix", test_google_maps_api_Distancematrix),
        11: ("Google Maps API - Elevation", test_google_maps_api_elevation),
        12: ("Google Maps API - Timezone", test_google_maps_api_Timezone),
        13: ("Google Maps API - Geolocation", test_google_maps_api_geolocate),

        # Google Roads APIs
        14: ("Google Maps API - Nearest Roads", test_google_maps_api_NearestRoads),
        15: ("Google Maps API - Snap To Roads", test_google_maps_api_SnapToRoads),
        16: ("Google Maps API - Speed Limits", test_google_maps_api_SpeedLimits),

        # Google Cloud AI & Machine Learning
        17: ("Google Cloud Natural Language API", test_google_natural_language_api),
        18: ("Google Natural Language Sentiment API", test_google_natural_language_sentiment),
        19: ("Google Vision API", test_google_vision_api),
        20: ("Google Cloud Text-to-Speech API", test_google_cloud_text_to_speech_api),
        21: ("Google Cloud Speech-to-Text API", test_google_cloud_speech_to_text_api),
        22: ("Google Cloud Video Intelligence API", test_google_cloud_video_intelligence_api),
        23: ("Google Cloud Document AI API", test_google_cloud_document_ai_api),

        # Google Translation & Language
        24: ("Google Translate API", test_google_translate_api),
        25: ("Google Cloud Translation API", test_google_cloud_translation_api),

        # Google Search & Content
        26: ("Google Custom Search API", test_google_custom_search_api),
        27: ("Google Books API", test_google_books_api),
        28: ("Google YouTube API", test_google_youtube_api),
        29: ("Google Consumer Search", test_google_maps_api_Consumersearch),
        30: ("Google Fact Check API", test_google_fact_check_api),
        31: ("Google PageSpeed Insights API", test_google_pagespeed_api),
        32: ("Google Safe Browsing API", test_google_safe_browsing_api),

        # Google Cloud Storage & Database
        33: ("Google Cloud Storage API", test_google_cloud_storage_api),
        34: ("Google BigQuery API", test_google_bigquery_api),
        35: ("Google Cloud Datastore API", test_google_cloud_datastore_api),

        # Google Productivity & Organization
        36: ("Google Drive API", test_google_drive_api),
        37: ("Google Sheets API", test_google_sheets_api),
        38: ("Google Calendar API", test_google_calendar_api),
        39: ("Google Tasks API", test_google_tasks_api),

        # Google Social & User Data
        40: ("Google People API", test_google_people_api),
        41: ("Google Blogger API", test_google_blogger_api),
        42: ("Google Civic API", test_google_civic_information_api),

        # Google Design & Fonts
        43: ("Google WebFonts API", test_google_fonts_api),
        
        # Firebase Services
        44: ("Firebase Authentication API", test_firebase_auth_api)
    }
    return api_functions.get(number)

def list_available_apis():
    """Lists all available APIs with their numbers organized by categories"""
    print(f"\n{Colors.HEADER}Available APIs for Testing:{Colors.RESET}")
    print(f"{Colors.HEADER}{'─' * 60}{Colors.RESET}")
    
    # Organize APIs by category
    categories = {
        "Google Maps and Location": range(1, 14),
        "Google Roads APIs": range(14, 17),
        "Google Cloud AI & Machine Learning": range(17, 24),
        "Google Translation & Language": range(24, 26),
        "Google Search & Content": range(26, 33),
        "Google Cloud Storage & Database": range(33, 36),
        "Google Productivity & Organization": range(36, 40),
        "Google Social & User Data": range(40, 43),
        "Google Design & Fonts": [43],
        "Firebase Services": [44]
    }
    
    for category, api_range in categories.items():
        print(f"\n{Colors.BOLD}{category}{Colors.RESET}")
        for api_num in api_range:
            api_info = get_api_function_by_number(api_num)
            if api_info:
                api_name = api_info[0]
                print(f"  {Colors.INFO}[{api_num}]{Colors.RESET} {api_name}")
    
    print(f"\n{Colors.HEADER}{'─' * 60}{Colors.RESET}")
    print(f"Use '-a' or '--api' to select specific APIs (e.g., -a \"1,3,5\" or -a \"1-5\")")
    print(f"To test all APIs, do not use the '-a' parameter\n")

def test_api_keys(api_keys, verbose, output_file=None, api_selection=None):
    """
    Tests a list of API keys against selected Google APIs
    
    Args:
        api_keys: List of API keys to test
        verbose: If True, prints detailed API responses
        output_file: Optional file path to save results
        api_selection: String specifying which APIs to test (e.g. "1,3,5-7")
    
    Returns:
        Dictionary with test results
    """
    api_results = {}
    selected_apis = parse_api_selection(api_selection)
    
    for key in api_keys:
        api_results[key] = {}
        spacer = f"{Colors.HEADER}{'─' * 60}{Colors.RESET}"
        title = "Testing API Key:"
        top = len(title + key) + 3
        top2 = "─" * top
        print(f"{Colors.INFO}╭{top2}╮")
        print(f"{Colors.INFO}│ {Colors.RESET + Colors.BOLD}{title} {key} {Colors.RESET + Colors.INFO}│")
        print(f"{Colors.INFO}╰{top2}╯{Colors.RESET}")

        for api_num in selected_apis:
            api_func = get_api_function_by_number(api_num)
            if api_func:
                api_name, test_function = api_func
                try:
                    # Call the API test function
                    result = test_function(key, verbose)
                    
                    # Process the result
                    if result in ApiTester.ERROR_MESSAGES:
                        status = f"{Colors.ERROR}❌ [{result}]{Colors.RESET}"
                    else:
                        status = f"{Colors.SUCCESS}✅ [WORKED]{Colors.RESET}"
                        api_results[key][api_name] = result
                    
                    # Display result with API number BEFORE status (inverted order)
                    print(f"{Colors.BOLD}[{api_num}] {api_name}{Colors.RESET} | {status}")
                    
                    # Show response details if verbose mode is enabled
                    if verbose and result not in ApiTester.ERROR_MESSAGES:
                        print(f"{Colors.INFO}{result}{Colors.RESET}")
                    
                    print(spacer)
                except Exception as e:
                    logging.error(f"Error testing {api_name}: {str(e)}")
    
    # Save results to file if output_file is specified
    if output_file:
        save_results_to_file(api_results, output_file)
        
    return api_results

def save_results_to_file(api_results, output_file):
    """
    Saves API test results to a file
    
    Args:
        api_results: Dictionary containing test results
        output_file: Path to the output file
    """
    try:
        with open(output_file, 'w') as f:
            # Create a simplified version of results for JSON serialization
            output_data = {}
            for key, apis in api_results.items():
                output_data[key] = {
                    api_name: "Success" for api_name in apis.keys()
                }
                
            # Write formatted JSON to file
            json.dump(output_data, f, indent=2)
            print(f"\n{Colors.SUCCESS}Results saved to {output_file}{Colors.RESET}")
    except Exception as e:
        logging.error(f"Error saving results to file: {str(e)}")

def main():
    try:
        parser = argparse.ArgumentParser(description='Test Google API keys')
        parser.add_argument('-k', '--key', help='Single API key to test')
        parser.add_argument('-l', '--list', help='File containing list of API keys, one per line')
        parser.add_argument('-v', '--verbose', action='store_true', help='Print full responses for successful tests')
        parser.add_argument('-o', '--output', help='Output file to save the results')
        parser.add_argument('-a', '--api', help='Select specific APIs to test (e.g., "1,2,3" or "1-5" or "1")')
        parser.add_argument('-la', '--list-apis', action='store_true', help='List all available APIs with their numbers')

        args = parser.parse_args()

        if args.list_apis:
            list_available_apis()
            return

        if args.key:
            test_api_keys([args.key], args.verbose, args.output, args.api)
        elif args.list:
            with open(args.list, 'r') as file:
                keys = file.read().splitlines()
                print(f"[Total keys]: {len(keys)}")               
                test_api_keys(keys, args.verbose, args.output, args.api)
        else:
            print("No API key or list provided. Use -k to provide a single key or -l to provide a list of keys.")
            print("Use --list-apis to see all available APIs with their numbers.")
    
    except KeyboardInterrupt:
        print("\n[!] Exiting...")
        exit(0)

if __name__ == "__main__":
    banner()
    main()