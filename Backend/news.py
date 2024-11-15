import requests

from typing import List
from termcolor import colored

def search_news(query: str, api_key: str, limit: int = 5, language:str = 'en') -> List[str]:
    """
    Searches for stock videos based on a query.

    Args:
        query (str): The query to search for.
        api_key (str): The API key to use.

    Returns:
        List[str]: A list of stock videos.
    """

    # Build URL
    qurl = f"https://gnews.io/api/v4/search?q={query}&lang={language}&max={limit}&apikey={api_key}"

    # Send the request
    r = requests.get(qurl)

    # Parse the response
    response = r.json()
    
    
    print(colored(response, "cyan"))
    
    titles = ''
    sentences = ''
    images = ''
    result = []
    
    try:
        
        for i in range(limit):
            titleResponse = response["articles"][i]["title"]
            titleFilter =''.join(filter(lambda x: x != "\"", titleResponse)).replace(",", ".").replace(";", ",")
            source = response["articles"][i]["source"]["name"]
            
            titles += f"{titleFilter} ({source});\n\n"
            
            descriptionResponse = response["articles"][i]["description"]
            descriptionFilter = ''.join(filter(lambda x: x != '"', descriptionResponse)).replace(";", ",")
            sentences += f"{titleFilter}. {descriptionFilter};\n\n"
            
            imageResponse = response["articles"][i]["image"]
            images += f"{imageResponse};\n\n"
            
            
        result.append(titles)
        result.append(sentences)
        result.append(images)
        
        print(colored(result[0], "red"))
            
                
    except Exception as e:
        print(colored("[-] No news found.", "red"))
        print(colored(e, "red"))

    # Let user know
    print(colored(f"\t=> \"{query}\" found titles: {titles} and sentences: {sentences}", "cyan"))

    # Return the video url
    return result
