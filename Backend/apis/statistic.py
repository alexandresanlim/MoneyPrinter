import requests

API_KEY = "AIzaSyDuvcF1iMzKa5KVC6kYYlheVdGB6R-ozGI"
CHANNEL_ID = "UCRZDgA08rxRckuY6fKoNwuQ"  # Substitua pelo ID do canal

# Estatísticas do canal


def get_channel_stats():
    
    url_stats = f"https://www.googleapis.com/youtube/v3/channels?part=statistics&id={CHANNEL_ID}&key={API_KEY}"
    response_stats = requests.get(url_stats).json()
    stats = response_stats["items"][0]["statistics"]
    
    print(f"Inscritos: {stats['subscriberCount']}, Visualizações: {stats['viewCount']}")
    
    return {
        "subscriberCount": stats['subscriberCount'],
        "viewCount": stats['viewCount'],
        "videoCount": stats['videoCount']
    }


def get_comments() -> list:
    url_comments = f"https://www.googleapis.com/youtube/v3/commentThreads?part=snippet&allThreadsRelatedToChannelId={CHANNEL_ID}&key={API_KEY}&order=time"
    response_comments = requests.get(url_comments).json()
    
    comments = []
    
    for item in response_comments["items"]:

        comment = {
            "nome": item["snippet"]["topLevelComment"]["snippet"]["authorDisplayName"],
            "imagem": item["snippet"]["topLevelComment"]["snippet"]["authorProfileImageUrl"],
            "comentario": item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
        }
        
        comments.append(comment)
    
    return comments
