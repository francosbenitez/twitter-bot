import os
import random
import json
from pathlib import Path
import tweepy
import csv
import requests

ROOT = Path(__file__).resolve().parents[0]

def twitter_api():
    print("Get credentials")
    consumer_key = os.getenv("CONSUMER_KEY")
    consumer_secret = os.getenv("CONSUMER_SECRET")
    access_token = os.getenv("ACCESS_TOKEN")
    access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")

    print("Authenticate")
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    return api

def tweet_image(url, message):
    api = twitter_api()
    filename = 'temp.jpg'
    request = requests.get(url, stream=True)
    if request.status_code == 200:
        with open(filename, 'wb') as image:
            for chunk in request:
                image.write(chunk)

        api.update_with_media(filename, status=message)
        os.remove(filename)
    else:
        print("Unable to download image")

def get_tweet(tweets_file, excluded_tweets=None):
    """Get tweet to post from CSV file"""

    with open(tweets_file) as csvfile:
        reader = csv.DictReader(csvfile)
        possible_tweets = [row["tweet"] for row in reader]

    if excluded_tweets:
        recent_tweets = [status_object.text for status_object in excluded_tweets]
        possible_tweets = [tweet for tweet in possible_tweets if tweet not in recent_tweets]

    selected_tweet = random.choice(possible_tweets)

    return selected_tweet


def lambda_handler(event, context):
    api = twitter_api()
    print("Get tweet from csv file")
    tweets_file = ROOT / "tweets.csv"
    recent_tweets = api.user_timeline()[:3]
    tweet = get_tweet(tweets_file)

    if tweet.startswith("https://"):    
      print(f"Post tweet: {tweet}")
      url = tweet
      message = ""
      tweet_image(url, message)
    else: 
      print(f"Post tweet: {tweet}")
      api.update_status(tweet)
    return {"statusCode": 200, "tweet": tweet}

