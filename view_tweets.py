import re
from datetime import datetime, timedelta
import logging

def parse_log_date(line):
    """Extract date from log line"""
    try:
        date_str = line.split(' - ')[0]
        return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S,%f')
    except:
        return None

def extract_tweet(line):
    """Extract tweet content from log line"""
    match = re.search(r'Would post tweet: (.*)', line)
    if match:
        return match.group(1)
    return None

def get_tweets_for_date(date):
    """Get all tweets from a specific date"""
    tweets = []
    try:
        with open('ai_posts.log', 'r') as f:
            for line in f:
                log_date = parse_log_date(line)
                if log_date and log_date.date() == date.date():
                    tweet = extract_tweet(line)
                    if tweet:
                        tweets.append((log_date, tweet))
    except FileNotFoundError:
        print("No log file found. The posting system might not have generated any tweets yet.")
        return []
    
    return tweets

def display_tweets(days=3):
    """Display tweets from the last n days"""
    today = datetime.now()
    
    for i in range(days):
        date = today - timedelta(days=i)
        tweets = get_tweets_for_date(date)
        
        print(f"\n{'='*20} Tweets for {date.strftime('%Y-%m-%d')} {'='*20}")
        if tweets:
            for timestamp, tweet in tweets:
                print(f"\n[{timestamp.strftime('%H:%M:%S')}]")
                print("-" * 80)
                print(tweet)
                print("-" * 80)
        else:
            print("No tweets found for this date")

if __name__ == "__main__":
    display_tweets()
