"""Store verified information and high-klout crypto accounts for reference."""

# Top crypto Twitter accounts with high engagement
HIGH_KLOUT_ACCOUNTS = {
    "vitalik.eth": {
        "handle": "@VitalikButerin",
        "focus": ["Ethereum", "Blockchain", "Tech"],
        "typical_topics": ["scaling", "security", "innovation"]
    },
    "cz_binance": {
        "handle": "@cz_binance",
        "focus": ["Exchange", "Industry News", "Market"],
        "typical_topics": ["exchange updates", "industry trends"]
    },
    "saylor": {
        "handle": "@saylor",
        "focus": ["Bitcoin", "Macro", "Investment"],
        "typical_topics": ["bitcoin adoption", "institutional investment"]
    },
    "sbf_ftx": {
        "handle": "@SBF_FTX",
        "focus": ["Trading", "Exchange", "Markets"],
        "typical_topics": ["market analysis", "trading insights"]
    },
    "aantonop": {
        "handle": "@aantonop",
        "focus": ["Bitcoin", "Security", "Education"],
        "typical_topics": ["security", "blockchain education"]
    }
}

# Verified news sources
VERIFIED_SOURCES = {
    "tech": [
        "TechCrunch",
        "The Information",
        "Wired",
        "ArsTechnica",
        "The Verge"
    ],
    "crypto": [
        "CoinDesk",
        "The Block",
        "Cointelegraph",
        "Decrypt",
        "CryptoSlate"
    ],
    "research": [
        "arXiv.org",
        "OpenAI Blog",
        "DeepMind Blog",
        "Google AI Blog",
        "Microsoft Research"
    ]
}

# Only use verified metrics that are publicly available
VERIFIED_METRICS = {
    "openai": {
        "source": "OpenAI Blog",
        "metrics": {
            "gpt4": {
                "release_date": "2023-03-14",
                "capabilities": ["advanced reasoning", "creative tasks", "coding"]
            }
        }
    },
    "ethereum": {
        "source": "ethereum.org",
        "metrics": {
            "transactions": "over 1 million daily",
            "validators": "over 500,000",
            "total_value_locked": "$20B+"
        }
    }
}

def get_verified_quote(account, topic):
    """Get a real, verified quote from a high-klout account if available."""
    return None  # Only return real quotes, no fabrication
