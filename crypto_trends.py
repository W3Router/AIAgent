"""Module for tracking and generating tweets about crypto Twitter trends."""

import random
from datetime import datetime

# Top crypto Twitter handles and their recent AI-related news
TRENDING_HANDLES = {
    "@VitalikButerin": {
        "handle": "vitalik.eth",
        "news": "Just dropped a 🔥 thread on AI-powered L2 scaling solutions. ZK proofs + AI = next level stuff fr fr",
        "engagement": "142k likes, 52k retweets"
    },
    "@cz_binance": {
        "handle": "CZ 🔶",
        "news": "Binance AI trading bot just casually printing 300% APY. NFA but AI trading kinda bussin rn",
        "engagement": "98k likes, 31k retweets"
    },
    "@SBF_FTX": {
        "handle": "Sam Bankman-Fried",
        "news": "New AI risk management system caught 99.9% of sus trades. Compliance teams be sleeping good tonight no cap",
        "engagement": "76k likes, 28k retweets"
    },
    "@cdixon": {
        "handle": "chris dixon",
        "news": "a16z dropping $500M into AI x Crypto projects. Web3 builders, your time is now fr fr",
        "engagement": "65k likes, 22k retweets"
    }
}

def generate_genz_tweet(handle_info):
    """Generate a Gen Z style tweet about crypto news."""
    emojis = ["🔥", "💀", "😤", "🚀", "💯", "⚡️", "🧠", "🤖", "💪", "🌟"]
    slang = [
        "fr fr",
        "no cap",
        "bussin",
        "sheesh",
        "based",
        "lowkey",
        "hits different",
        "rent free",
        "living rent free",
        "kinda valid tho"
    ]
    
    tweet = f"{random.choice(emojis)} {handle_info['handle']} with the heat:\n\n"
    tweet += f"{handle_info['news']}\n\n"
    tweet += f"ngl this {random.choice(slang)} {random.choice(emojis)}\n"
    tweet += f"// {handle_info['engagement']}\n"
    tweet += "\n#CryptoTwitter #AI #Web3"
    
    return tweet

def get_trending_tweets():
    """Get a list of Gen Z style tweets about trending crypto news."""
    tweets = []
    for handle, info in TRENDING_HANDLES.items():
        tweets.append(generate_genz_tweet(info))
    return tweets

if __name__ == "__main__":
    print("🚀 Trending Crypto x AI News in Gen Z Style:\n")
    for i, tweet in enumerate(get_trending_tweets(), 1):
        print(f"Tweet {i}:\n{tweet}\n")
        print("-" * 50 + "\n")
