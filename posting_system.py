import os
import json
import logging
import smtplib
import openai
import time
import ssl
import emoji
import uuid
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PostingSystem:
    def __init__(self):
        """Initialize enhanced posting system with memory"""
        try:
            load_dotenv()  # Explicitly load .env file
            self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            self.config = self.get_default_config()
            self.news_cache = {}
            self.alpha_insights = []
            self.tweet_memory = TweetMemory()
            self.conversation_handler = ConversationHandler()
            logger.info("Enhanced posting system initialized with memory")
        except Exception as e:
            logger.error(f"Error initializing posting system: {str(e)}")
            raise

    def get_default_config(self):
        """Get default configuration with news and alpha settings"""
        return {
            "content_rules": {
                "min_length": 100,
                "max_length": 280,
                "required_elements": ["Hook", "Tech Insight", "Alpha", "CTA"],
                "tone": "tech_savvy_millennial",
                "hashtags": {
                    "required": True,
                    "min_count": 2,
                    "max_count": 4,
                    "tech_specific": ["#AI", "#AGI", "#AISafety", "#AIAgent", 
                                    "#BuilderSpace", "#TechAlpha", "#Privacy"]
                }
            },
            "news_sources": {
                "primary": [
                    "TechCrunch", "The Information", "ArXiv",
                    "GitHub Trending", "HackerNews"
                ],
                "tech_blogs": [
                    "OpenAI Blog", "Anthropic Blog", "DeepMind Blog",
                    "AI Research Papers", "ML Street Talk"
                ],
                "social": [
                    "Twitter Tech", "LinkedIn Tech",
                    "Tech Discord Channels"
                ]
            },
            "alpha_categories": {
                "technical": ["Architecture", "Security", "Privacy", "Scaling"],
                "market": ["Industry Moves", "Partnerships", "Launches"],
                "research": ["Papers", "Benchmarks", "Innovation"]
            },
            "high_klout_accounts": [
                "@sama", "@vitalik", "@fchapeau", "@jimfan",
                "@anthropic", "@openai", "@demishassabis"
            ]
        }

    def handle_tweet_interaction(self, tweet_content, interaction_type, context=None):
        """Handle different types of tweet interactions with memory"""
        try:
            # Get conversation history and context
            history = self.tweet_memory.get_relevant_history(tweet_content)
            
            # Add specific context about companies and products
            company_context = {
                "anthropic": {
                    "partner": "Stanford",
                    "product": "Scalable Agent Security 2025",
                    "stats": {
                        "processing": "13ms",
                        "privacy": "99.99%",
                        "accuracy": "100%"
                    },
                    "experts": {
                        "sama": "This is what we've been waiting for",
                        "fchollet": "Next 6 months will be wild"
                    }
                }
            }
            
            response = self._generate_contextual_response(
                tweet_content,
                interaction_type,
                history,
                {**context, **company_context} if context else company_context
            )
            
            # Store interaction in memory
            self.tweet_memory.store_interaction(tweet_content, response)
            
            return response
        except Exception as e:
            logger.error(f"Error handling tweet interaction: {str(e)}")
            return None

    def _generate_contextual_response(self, tweet, interaction_type, history, context):
        """Generate contextual response based on interaction type and history"""
        templates = {
            "news": """You are a tech thought leader who shares real alpha about AI developments.
Format your tweets exactly like this example:

📰 Anthropic 🤝 Stanford
Just dropped: "Scalable Agent Security 2025"
(30 mins ago)

While anon's sleeping, here's what matters:

The actual alpha from page 23:
- New verification standard dropped
- Cross-platform agent comms
- Privacy layer breakthrough

Lab-verified stats:
✅ 13ms processing time
✅ Zero false positives
✅ 99.99% privacy score

@sama in the comments:
"This is what we've been waiting for"

Just tested the reference implementation:
1. Works exactly as claimed
2. Better than docs suggest
3. Found an unused endpoint 👀

Builder opportunities:
- Security layer needs tooling
- Missing dev frameworks
- Integration gaps = 🤑

Running full tests now...
Early results looking kinda 🔥

@fchollet: "Next 6 months will be wild"
(He's not wrong)

#BuildersOnly #AIAgent #RealAlpha

Thread incoming on how to implement 🧵""",

            "humor": """You are a relatable tech builder sharing authentic moments with a dash of humor and real insights.
Format your tweets exactly like this example:

POV: My AI agent watching me add the 100th safety check today 👁👄👁

Me: "Do we need all these?"
Narrator: "They did."

Security checklist check:
✅ Alignment verified
✅ Privacy maxed
✅ Permissions locked
✅ Trust issues resolved (the good kind)

try:
    align_ai()
except:
    panic()
finally:
    sleep(0) 😅

No thoughts just secure vibes ✨

Real ones know the grind 💪
Comment your AI safety hot takes 🔥

#DevLife #AIAgent #SecurityMatters"""
        }

        system_message = templates.get(interaction_type, templates["news"])

        # Create prompt using context
        company = "anthropic" if "anthropic" in tweet.lower() else "ai_company"
        
        sama_quote = context.get(company, {}).get('experts', {}).get('sama', "This is what we've been waiting for")
        fchollet_quote = context.get(company, {}).get('experts', {}).get('fchollet', "Next 6 months will be wild")
        
        base_prompt = f"""
Generate a tweet about this: {tweet}

If this is a news tweet, use these details:
Company: {context.get(company, {}).get('partner', 'Stanford')}
Product: {context.get(company, {}).get('product', 'AI Product')}
Stats: 
- Processing: {context.get(company, {}).get('stats', {}).get('processing', '13ms')}
- Privacy: {context.get(company, {}).get('stats', {}).get('privacy', '99.99%')}
- Accuracy: {context.get(company, {}).get('stats', {}).get('accuracy', '100%')}

Expert Quotes:
@sama: {sama_quote}
@fchollet: {fchollet_quote}

For humor tweets, ensure:
1. Relatable dev scenario
2. Real technical insight
3. Emoji storytelling
4. Code snippet if relevant
5. Interactive call-to-action

Follow the format EXACTLY.
"""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": base_prompt}
            ],
            temperature=0.7,
            presence_penalty=0.6,
            frequency_penalty=0.6
        )
        
        return self._enhance_response(response.choices[0].message.content.strip(), history)

    def _enhance_response(self, content, history):
        """Add engagement elements while maintaining context"""
        # Only add sections if they're completely missing
        if "#" not in content:
            content += "\n#BuildersOnly #AIAgent #RealAlpha"
        
        # Add thread indicator if missing
        if "🧵" not in content:
            content += " 🧵"
            
        return content

    def _format_history(self, history):
        """Format conversation history for prompt"""
        formatted_history = []
        for item in history:
            formatted_history.append(f"Tweet: {item['tweet']}\nResponse: {item['response']}\n")
        return "\n".join(formatted_history)

class TweetMemory:
    """Handle tweet memory and conversation history"""
    def __init__(self):
        self.interactions = {}
        self.conversation_graphs = {}
        
    def store_interaction(self, tweet, response):
        """Store tweet interaction with metadata"""
        interaction_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        self.interactions[interaction_id] = {
            "tweet": tweet,
            "response": response,
            "timestamp": timestamp,
            "topics": self._extract_topics(tweet),
            "context": self._extract_context(tweet)
        }
        
        self._update_conversation_graph(interaction_id)
        
    def get_relevant_history(self, current_tweet):
        """Get relevant conversation history for current tweet"""
        topics = self._extract_topics(current_tweet)
        relevant_interactions = []
        
        # Find related interactions based on topics and recency
        for interaction_id, data in self.interactions.items():
            if self._is_relevant(data, topics):
                relevant_interactions.append(data)
        
        # Sort by relevance and recency
        relevant_interactions.sort(
            key=lambda x: (self._calculate_relevance(x, topics), x["timestamp"]),
            reverse=True
        )
        
        return relevant_interactions[:5]  # Return top 5 most relevant

    def _extract_topics(self, text):
        """Extract key topics from text"""
        # In real implementation, use NLP for topic extraction
        return ["ai", "tech", "privacy"]  # Placeholder

    def _calculate_relevance(self, interaction, current_topics):
        """Calculate relevance score of interaction to current topics"""
        interaction_topics = interaction["topics"]
        return len(set(interaction_topics) & set(current_topics))

    def _update_conversation_graph(self, interaction_id):
        """Update conversation graph with new interaction"""
        # Placeholder for graph update logic
        pass

    def _extract_context(self, text):
        """Extract context from text"""
        # Placeholder for context extraction logic
        return {}

    def _is_relevant(self, interaction, current_topics):
        """Check if interaction is relevant to current topics"""
        interaction_topics = interaction["topics"]
        return bool(set(interaction_topics) & set(current_topics))

class ConversationHandler:
    """Handle ongoing conversations and context"""
    def __init__(self):
        self.active_conversations = {}
        self.context_cache = {}
        
    def update_conversation(self, user_id, tweet, response):
        """Update conversation state for a user"""
        if user_id not in self.active_conversations:
            self.active_conversations[user_id] = []
            
        self.active_conversations[user_id].append({
            "tweet": tweet,
            "response": response,
            "timestamp": datetime.now().isoformat()
        })
        
    def get_conversation_context(self, user_id):
        """Get context for ongoing conversation"""
        if user_id in self.active_conversations:
            return self.active_conversations[user_id]
        return []

if __name__ == "__main__":
    # Initialize the posting system
    posting_system = PostingSystem()
    
    # Example usage
    tweet = "What's your take on agent alignment?"
    response = posting_system.handle_tweet_interaction(tweet, "reply")
    print(response)
