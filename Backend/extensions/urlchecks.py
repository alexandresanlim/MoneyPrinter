import requests
from termcolor import colored

def is_valid_url(url: str) -> bool:
    
    
    try:
        response = requests.get(url)
        
        print(colored(f'{response.status_code} {url}', 'blue'))
        
        return response.ok and response.status_code == 200
    
    except requests.exceptions.HTTPError:
        return False
    
    except:
        return False
    
def is_url(url: str):
    return url.startswith("http://") or url.startswith("https://")


