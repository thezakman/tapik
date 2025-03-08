#!/usr/bin/env python3.11
#import webbrowser
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

# Inicialize o colorama (necessário para Windows)
init(autoreset=True)

class Colors:
    """Define cores e estilos para output"""
    HEADER = Fore.CYAN
    SUCCESS = Fore.GREEN
    ERROR = Fore.RED
    WARNING = Fore.YELLOW
    INFO = Fore.BLUE
    RESET = Style.RESET_ALL
    BOLD = Style.BRIGHT

# Suprimir apenas o NotOpenSSLWarning
warnings.filterwarnings("ignore", category=InsecureRequestWarning)

VERSION = "v0.8.3"

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

@dataclass
class ApiTestResult:
    """Armazena o resultado de um teste de API"""
    api_name: str
    status: bool
    message: str
    response_data: Optional[str] = None

class RateLimiter:
    """Implementa rate limiting para as requisições"""
    def __init__(self, calls: int = 1, period: int = 1):
        self.calls = calls
        self.period = period
        self.timestamps = []

    def wait(self):
        """Espera se necessário para respeitar o rate limit"""
        now = time.time()
        self.timestamps = [t for t in self.timestamps if now - t <= self.period]
        
        if len(self.timestamps) >= self.calls:
            sleep_time = self.timestamps[0] + self.period - now
            if (sleep_time > 0):
                time.sleep(sleep_time)
        
        self.timestamps.append(now)

class ApiTester:
    """Classe base para testes de API"""
    ERROR_MESSAGES = [
        "UNAUTHENTICATED",
        "PERMISSION_DENIED", 
        "INVALID_ARGUMENT",
        "REQUEST_DENIED",
        "REJECTED",
        "BLOCKED",
        "BAD REQUEST",
        "INSUFFICIENTFILEPERMISSIONS"
    ]
    
    def __init__(self):
        self.rate_limiter = RateLimiter(calls=10, period=1)  # 10 chamadas por segundo
        
    def test_api_keys(self, api_keys: List[str], verbose: bool = False) -> Dict[str, Dict[str, ApiTestResult]]:
        """
        Testa uma lista de chaves de API
        
        Args:
            api_keys: Lista de chaves para testar
            verbose: Se True, mostra respostas detalhadas
            
        Returns:
            Dicionário com resultados dos testes
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
                    logging.error(f"Erro testando {api_name}: {str(e)}")
                    
        return results

    def _run_test(self, api_name: str, test_func, key: str, verbose: bool) -> ApiTestResult:
        """Executa um teste individual"""
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
        """Imprime o cabeçalho colorido para cada chave"""
        title = "Testing API Key:"
        top = len(title + key) + 3
        top2 = "─" * top
        print(f"{Colors.HEADER}╭{top2}╮")
        print(f"│ {Colors.BOLD}{title} {key} │") 
        print(f"╰{top2}╯{Colors.RESET}")

    def _print_result(self, result: ApiTestResult):
        """Imprime o resultado colorido de um teste"""
        if result.status:
            status = f"{Colors.SUCCESS}✅ [WORKED]{Colors.RESET}"
        else:
            status = f"{Colors.ERROR}❌ [{result.message}]{Colors.RESET}"
            
        print(f"{status} | {Colors.BOLD}{result.api_name}{Colors.RESET}")
        
        if result.response_data:
            print(f"{Colors.INFO}{result.response_data}{Colors.RESET}")
            
        print(f"{Colors.HEADER}{'─' * 60}{Colors.RESET}")

def banner():
    """Banner colorido do programa"""
    banner = f"""
{Colors.BOLD + Colors.SUCCESS}    
 _              _ _    
| | {Colors.RESET}@thezakman{Colors.BOLD + Colors.SUCCESS} (_) | {Colors.RESET + Colors.WARNING}{VERSION}{Colors.BOLD + Colors.SUCCESS}  
| |_ __ _ _ __  _| | __
| __/ _` | '_ \| | |/ /
| || (_| | |_) | |   < 
 \__\__,_| .__/|_|_|\_\\
   {Colors.WARNING}- TEST{Colors.BOLD + Colors.SUCCESS}| |{Colors.WARNING}API KEYS -{Colors.BOLD + Colors.SUCCESS}
         |_|
{Colors.RESET}"""
    print(banner)

def process_response(response, verbose):
    error_messages = ["UNAUTHENTICATED", "PERMISSION_DENIED", "INVALID_ARGUMENT", "REQUEST_DENIED", "REJECTED", "BLOCKED", "BAD REQUEST", "INSUFFICIENTFILEPERMISSIONS"]
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
    """Testa a API do Google Cloud Storage usando uma operação de listagem"""
    # Endpoint para listar buckets (operação mais básica)
    url = f"https://storage.googleapis.com/storage/v1/b?project=my-project&key={api_key}"
    
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key
    }
    
    try:
        response = requests.get(
            url,
            headers=headers,
            params={"maxResults": 1}  # Limita a 1 resultado para economia
        )
        
        # Se a resposta contiver "error" com código 401/403, ainda é um resultado válido
        # pois indica que a API key é válida mas precisa de permissões
        if response.status_code in [401, 403]:
            return "PERMISSION_DENIED"
            
        return process_response(response, verbose)
        
    except Exception as e:
        logging.error(f"Erro ao testar Cloud Storage API: {str(e)}")
        return "BAD REQUEST"
    
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

#"28. Tests the Google Calendar API"
def test_google_calendar_api(api_key, verbose):
    url = f"https://www.googleapis.com/calendar/v3/calendars/primary/events?key={api_key}"
    response = requests.get(url)
    return process_response(response, verbose)

#"29. Tests the Google Tasks API"
def test_google_tasks_api(api_key, verbose):
    url = f"https://tasks.googleapis.com/tasks/v1/users/@me/lists?key={api_key}"
    response = requests.get(url)
    return process_response(response, verbose)

#"30. Tests the Google People API"
def test_google_people_api(api_key, verbose):
    url = f"https://people.googleapis.com/v1/people/me?personFields=names,emailAddresses&key={api_key}"
    response = requests.get(url)
    return process_response(response, verbose)

#"31. Tests the Google Cloud Natural Language API"
def test_google_cloud_natural_language_api(api_key, verbose):
    url = "https://language.googleapis.com/v1/documents:analyzeSentiment"
    headers = {"X-Goog-Api-Key": api_key, "Content-Type": "application/json"}
    data = {
        "document": {
            "type": "PLAIN_TEXT",
            "content": "I love coding! It's so much fun."
        }
    }
    response = requests.post(url, json=data, headers=headers)
    return process_response(response, verbose)

#"32. Tests the Google Cloud Text-to-Speech API"
def test_google_cloud_text_to_speech_api(api_key, verbose):
    url = "https://texttospeech.googleapis.com/v1/text:synthesize"
    headers = {"X-Goog-Api-Key": api_key, "Content-Type": "application/json"}
    data = {
        "input": {"text": "Hello, world!"},
        "voice": {"languageCode": "en-US", "ssmlGender": "NEUTRAL"},
        "audioConfig": {"audioEncoding": "MP3"}
    }
    response = requests.post(url, json=data, headers=headers)
    return process_response(response, verbose)

#"33. Tests the Google Cloud Speech-to-Text API"
def test_google_cloud_speech_to_text_api(api_key, verbose):
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

#"34. Tests the Google Cloud Translation API"
def test_google_cloud_translation_api(api_key, verbose):
    url = "https://translation.googleapis.com/language/translate/v2/languages"  # Endpoint corrigido
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

#"35. Tests the Google Cloud Document AI API"
def test_google_cloud_document_ai_api(api_key, verbose):
    url = "https://documentai.googleapis.com/v1/projects/-/locations/us-central1/processors"  # Endpoint corrigido
    headers = {
        "X-Goog-Api-Key": api_key,
        "Content-Type": "application/json"
    }
    params = {
        "key": api_key
    }
    response = requests.get(url, headers=headers, params=params)
    return process_response(response, verbose)

#"36. Tests the Google Cloud Video Intelligence API"
def test_google_cloud_video_intelligence_api(api_key, verbose):
    url = "https://videointelligence.googleapis.com/v1/videos:annotate"
    headers = {"X-Goog-Api-Key": api_key, "Content-Type": "application/json"}
    data = {
        "inputContent": "base64_encoded_video",
        "features": ["LABEL_DETECTION"]
    }
    response = requests.post(url, json=data, headers=headers)
    return process_response(response, verbose)

#"37. Tests the Google Maps Places Photos API"
def test_google_maps_places_photos_api(api_key, verbose):
    # Primeiro precisamos obter uma referência de foto válida
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

#"38. Tests the Google BigQuery API"
def test_google_bigquery_api(api_key, verbose):
    url = f"https://bigquery.googleapis.com/bigquery/v2/projects/my-project/queries?key={api_key}"
    data = {
        "query": "SELECT name FROM `bigquery-public-data.usa_names.usa_1910_2013` LIMIT 10"
    }
    response = requests.post(url, json=data)
    return process_response(response, verbose)

#39. Tests the Google Cloud Datastore API
def test_google_cloud_datastore_api(api_key, verbose):
    url = f"https://datastore.googleapis.com/v1/projects/my-project:runQuery?key={api_key}"
    data = {
        "gqlQuery": {
            "queryString": "SELECT * FROM Task"
        }
    }
    response = requests.post(url, json=data)
    return process_response(response, verbose)

#40. Tests the Google Cloud Natural Language Sentiment API
def test_google_natural_language_sentiment(api_key, verbose):
    """Testa a API de Análise de Sentimento (US$ 1.00 por 1.000 requisições)"""
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

#41 Tests the Google Safe Browsing API
def test_google_safe_browsing_api(api_key, verbose):
    """Testa a API de Safe Browsing (US$ 0.75 por 1.000 requisições)"""
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

#42 Tests the Google PageSpeed Insights API
def test_google_pagespeed_api(api_key, verbose):
    """Testa a API do PageSpeed Insights (US$ 0.15 por 1.000 requisições)"""
    url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=https://google.com&key={api_key}"
    response = requests.get(url)
    return process_response(response, verbose)

#43 Tests the Google Maps Places Nearby API
def test_google_maps_places_nearby(api_key, verbose):
    """Testa a API de Pesquisa de Locais Próximos (US$ 32 por 1.000 requisições)"""
    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=-33.8670522,151.1957362&radius=500&type=restaurant&key={api_key}"
    response = requests.get(url)
    return process_response(response, verbose)

#44 Tests the Google Fact Check API
def test_google_fact_check_api(api_key, verbose):
    """Testa a API de Verificação de Fatos (US$ 0.00 - Gratuita com limites)"""
    url = f"https://factchecktools.googleapis.com/v1alpha1/claims:search?query=climate&key={api_key}"
    response = requests.get(url)
    return process_response(response, verbose)

def parse_api_selection(api_selection: str) -> list:
    """
    Converte a string de seleção em uma lista de números de API
    Exemplo: 
        "1,2,3" -> [1,2,3]
        "1-3" -> [1,2,3]
        "1" -> [1]
    """
    result = set()
    if not api_selection:
        return list(range(1,44))  # Todas as APIs (1-44)
        
    parts = api_selection.split(',')
    for part in parts:
        if '-' in part:
            start, end = map(int, part.split('-'))
            result.update(range(start, end + 1))
        else:
            result.add(int(part))
    return sorted(list(result))

def get_api_function_by_number(number: int):
    """Retorna a função de teste correspondente ao número da API"""
    api_functions = {
        1: ("Google Maps API - Consumer Search", test_google_maps_api_Consumersearch),
        2: ("Google Maps API - StaticMap", test_google_maps_api_Staticmap),
        3: ("Google Maps API - StreetView", test_google_maps_api_Streetview),
        4: ("Google Maps API - Directions", test_google_maps_api_Directions),
        5: ("Google Maps API - Geocode", test_google_maps_api_geocode),
        6: ("Google Maps API - Distance Matrix", test_google_maps_api_Distancematrix),
        7: ("Google Maps API - Find Place From Text", test_google_maps_api_Findplacefromtext),
        8: ("Google Maps API - Autocomplete", test_google_maps_api_Autocomplete),
        9: ("Google Maps API - Elevation", test_google_maps_api_elevation),
        10: ("Google Maps API - Timezone", test_google_maps_api_Timezone),
        11: ("Google Maps API - Nearest Roads", test_google_maps_api_NearestRoads),
        12: ("Google Maps API - Geolocation", test_google_maps_api_geolocate),
        13: ("Google Maps API - Snap To Roads", test_google_maps_api_SnapToRoads),
        14: ("Google Maps API - Speed Limits", test_google_maps_api_SpeedLimits),
        15: ("Google Maps API - Place Details", test_google_maps_api_place_detais),
        16: ("Google Natural Language API", test_google_natural_language_api),
        17: ("Google Books API", test_google_books_api),
        18: ("Google YouTube API", test_google_youtube_api),
        19: ("Google Custom Search API", test_google_custom_search_api),
        20: ("Google Translate API", test_google_translate_api),
        21: ("Google Civic API", test_google_civic_information_api),
        22: ("Google Blogger API", test_google_blogger_api),
        23: ("Google WebFonts API", test_google_fonts_api),
        24: ("Google Cloud Storage API", test_google_cloud_storage_api),
        25: ("Google Drive API", test_google_drive_api),
        26: ("Google Sheets API", test_google_sheets_api),
        27: ("Google Vision API", test_google_vision_api),
        28: ("Google Calendar API", test_google_calendar_api),
        29: ("Google Tasks API", test_google_tasks_api),
        30: ("Google People API", test_google_people_api),
        31: ("Google Cloud Natural Language API", test_google_cloud_natural_language_api),
        32: ("Google Cloud Text-to-Speech API", test_google_cloud_text_to_speech_api),
        33: ("Google Cloud Speech-to-Text API", test_google_cloud_speech_to_text_api),
        34: ("Google Cloud Translation API", test_google_cloud_translation_api),
        35: ("Google Cloud Document AI API", test_google_cloud_document_ai_api),
        36: ("Google Cloud Video Intelligence API", test_google_cloud_video_intelligence_api),
        37: ("Google Maps Places Photos API", test_google_maps_places_photos_api),
        38: ("Google BigQuery API", test_google_bigquery_api),
        39: ("Google Cloud Datastore API", test_google_cloud_datastore_api),
        40: ("Google Cloud Natural Language Sentiment API", test_google_natural_language_sentiment),
        41: ("Google Safe Browsing API", test_google_safe_browsing_api),
        42: ("Google PageSpeed Insights API", test_google_pagespeed_api),
        43: ("Google Maps Places Nearby API", test_google_maps_places_nearby),
        44: ("Google Fact Check API", test_google_fact_check_api)
    }
    return api_functions.get(number)

# Modifique a função test_api_keys para aceitar a lista de APIs
def test_api_keys(api_keys, verbose, output_file=None, api_selection=None):
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
                    result = test_function(key, verbose)
                    if result in ApiTester.ERROR_MESSAGES:
                        status = f"{Colors.ERROR}❌ [{result}]{Colors.RESET}"
                    else:
                        status = f"{Colors.SUCCESS}✅ [WORKED]{Colors.RESET}"
                        api_results[key][api_name] = result
                    
                    print(f"{status} | {Colors.BOLD}{api_name}{Colors.RESET}")
                    if verbose and result not in ApiTester.ERROR_MESSAGES:
                        print(f"{Colors.INFO}{result}{Colors.RESET}")
                    print(spacer)
                except Exception as e:
                    logging.error(f"Erro testando {api_name}: {str(e)}")

# Modifique a função main para incluir o novo argumento
def main():
    try:
        parser = argparse.ArgumentParser(description='Test Google API keys')
        parser.add_argument('-k', '--key', help='Single API key to test')
        parser.add_argument('-l', '--list', help='File containing list of API keys, one per line')
        parser.add_argument('-v', '--verbose', action='store_true', help='Print full responses for successful tests')
        parser.add_argument('-o', '--output', help='Output file to save the results')
        parser.add_argument('-a', '--api', help='Select specific APIs to test (e.g., "1,2,3" or "1-5" or "1")')

        args = parser.parse_args()

        if args.key:
            test_api_keys([args.key], args.verbose, args.output, args.api)
        elif args.list:
            with open(args.list, 'r') as file:
                keys = file.read().splitlines()
                print(f"[Total of keys]: {len(keys)}")               
                test_api_keys(keys, args.verbose, args.output, args.api)
        else:
            print("No API key or list provided. Use -k to provide a single key or -l to provide a list of keys.")
    
    except KeyboardInterrupt:
        print("\n[!] Exiting...")
        exit(0)

if __name__ == "__main__":
    banner()
    main()