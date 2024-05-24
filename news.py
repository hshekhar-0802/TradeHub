from newsapi import NewsApiClient
import json

def getnews():
    newsapi = NewsApiClient(api_key='59e16cfcedb34459b1e13ec27c5aec29')
    top_headlines = newsapi.get_top_headlines(category='business',language='en',country='in')
    titles = [article['title'] for article in top_headlines['articles']]
    descriptions = [article['description'] for article in top_headlines['articles']]
    urls = [article['url'] for article in top_headlines['articles']]
    url_to_images = [article['urlToImage'] for article in top_headlines['articles']]
    return titles,descriptions, urls, url_to_images
