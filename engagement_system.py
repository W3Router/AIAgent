import tweepy
import json
import logging
import os
import time
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("engagement.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TwitterEngagementSystem:
    def __init__(self):
        self.config_dir = Path(__file__).parent / "config"
        self.load_configs()
        self.setup_twitter_api()
        
    def load_configs(self):
        """加载配置文件"""
        try:
            with open(self.config_dir / "content_strategy.json", "r") as f:
                self.content_strategy = json.load(f)
        except FileNotFoundError as e:
            logger.error(f"Configuration file not found: {e}")
            raise
            
    def setup_twitter_api(self):
        """设置Twitter API"""
        try:
            self.client = tweepy.Client(
                bearer_token=os.getenv("TWITTER_BEARER_TOKEN"),
                consumer_key=os.getenv("TWITTER_API_KEY"),
                consumer_secret=os.getenv("TWITTER_API_SECRET"),
                access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
                access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET"),
                wait_on_rate_limit=True
            )
            logger.info("Successfully connected to Twitter API")
        except Exception as e:
            logger.error(f"Failed to initialize Twitter API: {e}")
            raise

    def get_mentions(self, since_id=None):
        """获取提及我们的推文"""
        try:
            mentions = self.client.get_users_mentions(
                id=self.client.get_me().data.id,
                since_id=since_id,
                tweet_fields=['created_at', 'text', 'author_id']
            )
            return mentions.data if mentions.data else []
        except Exception as e:
            logger.error(f"Error getting mentions: {e}")
            return []

    def get_tweet_replies(self, tweet_id):
        """获取特定推文的回复"""
        try:
            replies = self.client.search_recent_tweets(
                query=f"conversation_id:{tweet_id}",
                tweet_fields=['created_at', 'text', 'author_id']
            )
            return replies.data if replies.data else []
        except Exception as e:
            logger.error(f"Error getting replies: {e}")
            return []

    def like_tweet(self, tweet_id):
        """点赞推文"""
        try:
            self.client.like(tweet_id)
            logger.info(f"Liked tweet: {tweet_id}")
            return True
        except Exception as e:
            logger.error(f"Error liking tweet: {e}")
            return False

    def retweet(self, tweet_id):
        """转发推文"""
        try:
            self.client.retweet(tweet_id)
            logger.info(f"Retweeted: {tweet_id}")
            return True
        except Exception as e:
            logger.error(f"Error retweeting: {e}")
            return False

    def follow_user(self, user_id):
        """关注用户"""
        try:
            self.client.follow_user(user_id)
            logger.info(f"Followed user: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error following user: {e}")
            return False

    def reply_to_tweet(self, tweet_id, reply_text):
        """回复推文"""
        try:
            response = self.client.create_tweet(
                text=reply_text,
                in_reply_to_tweet_id=tweet_id
            )
            logger.info(f"Replied to tweet {tweet_id}: {reply_text}")
            return True
        except Exception as e:
            logger.error(f"Error replying to tweet: {e}")
            return False

    def engage_with_mentions(self):
        """与提及互动"""
        try:
            mentions = self.get_mentions()
            for mention in mentions:
                # 点赞提及
                self.like_tweet(mention.id)
                
                # 根据内容决定是否回复
                if any(keyword in mention.text.lower() for keyword in ['question', 'help', '?']):
                    reply = "Thank you for reaching out! We'll look into this and get back to you soon. 🙏"
                    self.reply_to_tweet(mention.id, reply)
                
                # 考虑关注用户
                if self.should_follow_user(mention.author_id):
                    self.follow_user(mention.author_id)
                
        except Exception as e:
            logger.error(f"Error in engagement cycle: {e}")

    def should_follow_user(self, user_id):
        """决定是否关注用户"""
        try:
            user = self.client.get_user(
                id=user_id,
                user_fields=['public_metrics', 'description']
            ).data
            
            # 关注标准
            followers_count = user.public_metrics['followers_count']
            following_count = user.public_metrics['following_count']
            
            # 简单的关注标准示例
            if followers_count > 1000 and following_count / followers_count < 2:
                return True
                
            return False
        except Exception as e:
            logger.error(f"Error checking user metrics: {e}")
            return False

    def engage_with_influencers(self):
        """与行业影响者互动"""
        try:
            influencers = self.content_strategy["twitter_handles"]["industry_experts"]["top_influencers"]
            
            for influencer in influencers:
                # 移除@符号
                username = influencer.replace("@", "")
                
                try:
                    # 获取用户最新推文
                    user = self.client.get_user(username=username).data
                    tweets = self.client.get_users_tweets(
                        id=user.id,
                        max_results=5,
                        tweet_fields=['created_at']
                    ).data
                    
                    if not tweets:
                        continue
                        
                    for tweet in tweets:
                        # 检查是否已经互动过
                        if not self.has_engaged(tweet.id):
                            # 根据内容决定互动方式
                            if self.should_engage_with_tweet(tweet.text):
                                self.like_tweet(tweet.id)
                                
                                # 某些情况下转发
                                if self.should_retweet(tweet.text):
                                    self.retweet(tweet.id)
                                    
                except Exception as e:
                    logger.error(f"Error engaging with influencer {username}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error in influencer engagement: {e}")

    def should_engage_with_tweet(self, text):
        """决定是否与推文互动"""
        # 检查推文是否包含相关关键词
        relevant_keywords = ['crypto', 'blockchain', 'defi', 'ai', 'web3']
        return any(keyword in text.lower() for keyword in relevant_keywords)

    def should_retweet(self, text):
        """决定是否转发推文"""
        # 更严格的转发标准
        high_value_keywords = ['announcement', 'breaking', 'news', 'research']
        return any(keyword in text.lower() for keyword in high_value_keywords)

    def has_engaged(self, tweet_id):
        """检查是否已经与推文互动过"""
        try:
            # 获取我们的点赞历史
            user_id = self.client.get_me().data.id
            liked = self.client.get_liked_tweets(id=user_id, max_results=100)
            liked_ids = [tweet.id for tweet in (liked.data or [])]
            
            return tweet_id in liked_ids
        except Exception as e:
            logger.error(f"Error checking engagement history: {e}")
            return False

    def run_engagement_cycle(self):
        """运行互动循环"""
        try:
            logger.info("Starting engagement cycle")
            
            # 处理提及
            self.engage_with_mentions()
            
            # 与影响者互动
            self.engage_with_influencers()
            
            logger.info("Completed engagement cycle")
            
        except Exception as e:
            logger.error(f"Error in engagement cycle: {e}")

def main():
    try:
        engagement_system = TwitterEngagementSystem()
        
        while True:
            engagement_system.run_engagement_cycle()
            # 每15分钟运行一次
            time.sleep(900)
            
    except Exception as e:
        logger.error(f"Main execution error: {e}")

if __name__ == "__main__":
    main()
