import os
import tweepy
from dotenv import load_dotenv

def load_env():
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    print(f"\nTrying to load .env file from: {env_path}")
    print(f"File exists: {os.path.exists(env_path)}\n")
    load_dotenv(env_path)

def test_twitter_api():
    print("Starting Twitter API test...\n")
    
    # Get credentials from environment variables
    api_key = os.getenv('TWITTER_API_KEY')
    api_secret = os.getenv('TWITTER_API_SECRET')
    access_token = os.getenv('TWITTER_ACCESS_TOKEN')
    access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
    bearer_token = os.getenv('TWITTER_BEARER_TOKEN')

    print("Credentials loaded from .env file")
    
    try:
        # Test OAuth 1.0a Authentication
        auth = tweepy.OAuthHandler(api_key, api_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth)
        
        print("\nTesting OAuth 1.0a authentication...")
        user = api.verify_credentials()
        print(f"Successfully authenticated as: @{user.screen_name}")
        
        # Test OAuth 2.0 (Bearer Token) Authentication
        print("\nTesting Bearer Token authentication...")
        client = tweepy.Client(bearer_token=bearer_token,
                             consumer_key=api_key,
                             consumer_secret=api_secret,
                             access_token=access_token,
                             access_token_secret=access_token_secret)
        
        me = client.get_me()
        print(f"Successfully retrieved user data using Bearer Token")
        print(f"User ID: {me.data.id}")
        print(f"Username: @{me.data.username}")
        print(f"Name: {me.data.name}")
        
    except Exception as e:
        print(f"\nError occurred: {str(e)}")
        print(f"Error type: {type(e).__name__}")

if __name__ == "__main__":
    load_env()
    test_twitter_api()
