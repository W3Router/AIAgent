"""Real-time crypto news and tweet generation system focusing on AI and agents."""

import os
import json
import requests
from datetime import datetime, timedelta
from pycoingecko import CoinGeckoAPI
from dotenv import load_dotenv
import random
import pytz
import re

class CryptoNewsAggregator:
    def __init__(self, http_session=None):
        load_dotenv()
        self.coingecko = CoinGeckoAPI()
        self.api_key = os.getenv('CRYPTOCOMPARE_API_KEY')
        self.http_session = http_session or requests.Session()
        self.ai_keywords = [
            'artificial intelligence', 'machine learning', 'neural network',
            'autonomous agent', 'agentic ai', 'llm', 'language model',
            'deep learning', 'ai model', 'chatbot', 'intelligent agent',
            'predictive analytics', 'ai trading', 'ml algorithm'
        ]
        self.used_accounts = set()  # Track used accounts in this session
        
    def reset_used_accounts(self):
        """Reset the used accounts tracking at the start of each day"""
        self.used_accounts = set()
        
    def get_unused_account(self, accounts):
        """Get a random unused account, reset if all are used"""
        available = [acc for acc in accounts if acc not in self.used_accounts]
        if not available:
            self.reset_used_accounts()
            available = accounts
        
        chosen = random.choice(available)
        self.used_accounts.add(chosen)
        return chosen
        
    def contains_ai_content(self, text):
        """Check if text contains AI-related keywords."""
        text = text.lower()
        return any(keyword in text for keyword in self.ai_keywords) or \
               bool(re.search(r'\b(ai|ml)\b', text))
        
    def get_latest_news(self):
        """Get AI and agent-related news from the last 24 hours."""
        try:
            url = "https://min-api.cryptocompare.com/data/v2/news/?lang=EN&categories=AI|Technology|Trading"
            headers = {'authorization': f'Apikey {self.api_key}'}
            response = self.http_session.get(url, headers=headers, verify=False, timeout=30)
            news_data = response.json()
            
            if 'Data' in news_data and news_data['Data']:
                sg_tz = pytz.timezone('Asia/Singapore')
                current_time = datetime.now(sg_tz)
                recent_news = []
                
                for article in news_data['Data']:
                    published_time = datetime.fromtimestamp(article['published_on']).replace(tzinfo=sg_tz)
                    time_diff = current_time - published_time
                    
                    if time_diff <= timedelta(hours=24):
                        # Strict check for AI-related content
                        title = article['title']
                        body = article['body'][:500]  # Check first 500 chars for performance
                        
                        if self.contains_ai_content(title) or self.contains_ai_content(body):
                            # Extract key AI insights from the body
                            sentences = body.split('. ')
                            # Remove metadata and clean up sentences
                            clean_sentences = [s for s in sentences 
                                            if self.contains_ai_content(s) and 
                                            'appeared first' not in s.lower() and
                                            len(s.split()) > 5]  # Ensure meaningful sentences
                            
                            recent_news.append({
                                'title': title,
                                'body': body,
                                'ai_insights': clean_sentences[:2],  # Top 2 AI-related sentences
                                'source': article['source_info']['name']
                            })
                
                return recent_news
            return []
        except Exception as e:
            print(f"Error fetching news: {str(e)}")
            return []

    def get_trending_ai_coins(self):
        """Get trending AI-related coins."""
        try:
            trending = self.coingecko.get_search_trending()
            ai_coins = [coin for coin in trending['coins'] 
                       if self.contains_ai_content(coin['item']['name']) or 
                          self.contains_ai_content(coin['item']['symbol'])]
            return ai_coins[:3]  # Top 3 AI-related trending coins
        except Exception as e:
            print(f"Error fetching trending coins: {str(e)}")
            return []

def generate_tweet(news_item, trending_coins=None, aggregator=None):
    """Generate tweets about AI crypto news with varying formats, including philosophical insights."""
    
    # Initialize aggregator if not provided
    if aggregator is None:
        aggregator = CryptoNewsAggregator()
    
    # Different tweet formats
    formats = [
        "ai_manual",
        "expectation_reality",
        "tier_list",
        "patch_notes",
        "alignment_chart",
        "skill_tree"
    ]
    
    # AI Manual format
    ai_manual = [
        "AI Trading Manual v2025:\n1. turn on AI\n2. touch grass\n3. come back to gains 📈",
        "How to Trade in 2025:\n1. let AI do its thing\n2. go outside\n3. profit 🤖",
        "AI Agent Setup Guide:\n1. deploy bot\n2. delete trading apps\n3. enjoy life 🌴",
        "Trading Psychology 2025:\n1. trust the AI\n2. ignore the charts\n3. stay hydrated 💧",
        "Modern Trading Steps:\n1. AI does analysis\n2. AI makes trades\n3. you take credit 😎"
    ]
    
    # Expectation vs Reality
    expectation_reality = [
        "Humans trading:\n- research for hours\n- emotional decisions\n- panic sells\n\nAI trading:\n- instant analysis\n- pure logic\n- never sleeps 🤖",
        "What you think AI trading is:\n- complex math\n- rocket science\n- magic\n\nWhat it actually is:\n- number go up\n- you go outside\n- life good 📈",
        "Crypto Bros:\n- 'trust me bro'\n- 'to the moon'\n- 'buy my course'\n\nAI Agents:\n- verified data\n- actual profits\n- no merch 💅",
        "Human Copium:\n- 'AI can't feel markets'\n- 'need human touch'\n- 'tech will fail'\n\nMeanwhile AI:\n- outperforms\n- outlasts\n- outsmart 🧠",
        "Traditional Trading:\n- charts\n- indicators\n- stress\n\nAI Trading:\n- beep boop\n- task failed successfully\n- number go up 🚀"
    ]
    
    # Tier List
    tier_list = [
        "Trading Tier List 2025:\nS: AI Agents\nA: AI + Human\nB: Bot Trading\nF: Manual Trading 📊",
        "Portfolio Manager Tier List:\nS: Autonomous AI\nA: Supervised AI\nB: Quant Bots\nF: Your Emotions 🎯",
        "Trading Speed Tier List:\nS: AI Microseconds\nA: Bot Milliseconds\nB: HFT Seconds\nF: Human Minutes ⚡",
        "Risk Management Tier List:\nS: AI Systems\nA: Smart Contracts\nB: Stop Losses\nF: Trust Me Bro 🛡️",
        "Market Analysis Tier List:\nS: AI Networks\nA: Machine Learning\nB: Technical Analysis\nF: Astrology 🔮"
    ]
    
    # Patch Notes
    patch_notes = [
        "HUMAN TRADER v2025.1 PATCH NOTES:\n- nerfed emotional trading\n- buffed AI integration\n- removed FOMO feature 🎮",
        "MARKET UPDATE v2025:\n- added AI agents\n- removed human error\n- fixed paper hands bug\n- buffed returns 🛠️",
        "TRADING v2.0 CHANGELOG:\n- deprecated manual trading\n- added AI autopilot\n- removed sleep requirement 🔄",
        "CRYPTO PATCH 2025.1:\n- AI agents now meta\n- humans need buff\n- emotion mechanic removed\n- added grass touching 🌱",
        "MARKET HOTFIX:\n- fixed human error bug\n- implemented AI oversight\n- removed panic sell button 🔧"
    ]
    
    # Alignment Chart
    alignment_chart = [
        "Trading Alignment Chart:\nLawful Good: AI Agent\nChaotic Good: AI + Human\nChaotic Evil: 3am Trading 📱",
        "Market Player Alignment:\nLawful Good: AI Systems\nNeutral: Quant Bots\nChaotic Evil: Trust Me Bros 🎲",
        "Portfolio Alignment:\nLawful Good: AI Manager\nNeutral Good: Index Bot\nChaotic Evil: Leverage Trading 🎯",
        "Strategy Alignment:\nLawful Good: AI Analysis\nTrue Neutral: DCA Bot\nChaotic Evil: FOMO Trading 🎭",
        "Trader Alignment:\nLawful Good: AI Agent\nNeutral Good: Bot Trader\nChaotic Evil: Emotional Trader 🃏"
    ]
    
    # Skill Tree
    skill_tree = [
        "TRADING SKILL TREE 2025:\n⭐ AI Integration (MAX)\n└ Human Emotion (DISABLED)\n  └ Manual Trading (DEPRECATED) 🎮",
        "MARKET SKILL TREE:\n⭐ AI Analysis (MAXED)\n└ Technical Analysis (OBSOLETE)\n  └ Gut Feeling (ERROR 404) 🎯",
        "PORTFOLIO SKILL TREE:\n⭐ AI Management (UNLOCKED)\n└ Bot Trading (UPGRADED)\n  └ Manual Trading (LOCKED) 🔒",
        "TRADER EVOLUTION TREE:\n⭐ AI Partnership (EVOLVED)\n└ Bot Usage (LEARNED)\n  └ Chart Reading (FORGOTTEN) 📊",
        "CRYPTO SKILL TREE:\n⭐ AI Agent (MASTERED)\n└ Smart Contracts (LEARNED)\n  └ Emotional Control (404) 🎓"
    ]
    
    # Crypto influencer references with their typical styles
    influencer_refs = [
        ("@cobie", "would never fall for human trading cope 🧵"),
        ("@gainzy", "AI only goes up 📈"),
        ("@CryptoKaleo", "called it: AI agents > human traders"),
        ("@DegenSpartan", "letting the AI cook 👨‍🍳"),
        ("@0xWave", "was right about AI trading supremacy"),
        ("@0xfoobar", "watching AI agents flip traders rn 👀"),
        ("@VitalikButerin", "AI alignment looking good ser"),
        ("@zhusu", "been real quiet since AI started trading"),
        ("@AltcoinPsycho", "'imagine not having an AI agent'"),
        ("@IamNomad", "spotted this AI alpha first"),
        ("@loomdart", "AI agents are the new meta"),
        ("@Pentosh1", "AI chart patterns never lie"),
        ("@CryptoCred", "technical analysis is dead, AI killed it"),
        ("@SmallCapScience", "adapt or get rekt by AI"),
        ("@crypto_birb", "AI agents flipping my bags")
    ]
    
    # Trader references with their typical advice
    trader_refs = [
        ("@MacnBTC", "switched to AI trading"),
        ("@CryptoMessiah", "AI agents are free money"),
        ("@inversebrah", "inverse the humans, follow the AI"),
        ("@TheCryptoDog", "letting the AI hunt for alpha"),
        ("@nebraskangooner", "these AI levels are key"),
        ("@Cryptanzee", "AI agents never sleep"),
        ("@TraderMayne", "AI trading is the future"),
        ("@CryptoTony__", "AI broke the trendline"),
        ("@ByzGeneral", "AI armies are assembling"),
        ("@CryptoKaleo", "AI agents printing rn")
    ]
    
    # Choose format
    format_type = random.choice(formats)
    
    if format_type == "ai_manual":
        tweet = f"{random.choice(ai_manual)}\n\n"
        tweet += f"Latest Example:\n{news_item['title']}"
            
    elif format_type == "expectation_reality":
        tweet = f"{random.choice(expectation_reality)}\n\n"
        tweet += f"Breaking News:\n{news_item['title']}"
        
    elif format_type == "tier_list":
        tweet = f"{random.choice(tier_list)}\n\n"
        tweet += f"Today's Proof:\n{news_item['title']}"
        
    elif format_type == "patch_notes":
        tweet = f"{random.choice(patch_notes)}\n\n"
        tweet += f"Changelog Entry:\n{news_item['title']}"
        
    elif format_type == "alignment_chart":
        tweet = f"{random.choice(alignment_chart)}\n\n"
        tweet += f"Current Meta:\n{news_item['title']}"
        
    else:  # skill_tree
        tweet = f"{random.choice(skill_tree)}\n\n"
        tweet += f"Skill Unlocked:\n{news_item['title']}"
    
    # Add AI insights if available
    if news_item.get('ai_insights'):
        tweet += f"\n\nPatch Note: {random.choice(news_item['ai_insights'])}"
    
    # Choose random unused accounts for this tweet
    influencer = aggregator.get_unused_account(influencer_refs)
    trader = aggregator.get_unused_account(trader_refs)
    
    # Format the references
    influencer_ref = f"{influencer[0]} {influencer[1]}"
    trader_ref = f"{trader[0]} {trader[1]}"
    
    # Add the references to the tweet
    if random.random() < 0.7:  # 70% chance to add influencer reference
        tweet += f"\n\n{influencer_ref}"
    
    # Add trader reference with different format
    if random.random() < 0.3:  # 30% chance to use trader reference
        tweet += f"\n\neven {trader_ref}... you good? 👀"
    else:
        # Spicy questions without account references
        questions = [
            "still trading manually? that's kinda cringe bro 😬",
            "imagine not having AI automation in 2025... you good? 👀",
            "what's your excuse for not using AI? wrong answers only 🎭",
            "day trading is cool but have you tried grass touching? 🌱",
            "how's that technical analysis working out for you? 📉"
        ]
        tweet += f"\n\n{random.choice(questions)}"
    
    tweet += "\n#AIFirst #CryptoNetworks #TheNetwork"
    
    return tweet

if __name__ == "__main__":
    aggregator = CryptoNewsAggregator()
    news = aggregator.get_latest_news()
    trending = aggregator.get_trending_ai_coins()
    
    if news:
        tweet = generate_tweet(news[0], trending, aggregator)
        print(f"\n{tweet}\n")
    else:
        print("No recent AI news found in the last 24 hours.")
