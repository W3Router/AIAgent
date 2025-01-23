"""Tweet templates for AI agents and security analysis."""

AI_AGENT_TEMPLATE = """
🤖 AI Agent Update:

[ACTUAL_NEWS_HEADLINE]
Source: [SOURCE] ([TIMESTAMP])

Key capabilities:
• [VERIFIED_CAPABILITY_1]
• [VERIFIED_CAPABILITY_2]
• [VERIFIED_CAPABILITY_3]

Security features:
🔒 [SECURITY_FEATURE_1]
🔒 [SECURITY_FEATURE_2]

[TECH_HUMOR] 🤖

#AIAgents #Security #Privacy"""

SECURITY_UPDATE_TEMPLATE = """
🔐 Security Alert:

[ACTUAL_NEWS_HEADLINE]
Source: [SOURCE] ([TIMESTAMP])

Impact:
• [VERIFIED_IMPACT_1]
• [VERIFIED_IMPACT_2]
• [VERIFIED_IMPACT_3]

Protection measures:
🛡️ [SECURITY_MEASURE_1]
🛡️ [SECURITY_MEASURE_2]

[SECURITY_QUIP] 🔒

#Security #Privacy #AI"""

MARKET_UPDATE_TEMPLATE = """
📈 AI Trading Update:

[ACTUAL_NEWS_HEADLINE]
Source: [SOURCE] ([TIMESTAMP])

Performance:
💹 [PERFORMANCE_1]
💹 [PERFORMANCE_2]
💹 [PERFORMANCE_3]

Key Insights:
🎯 [INSIGHT_1]
🎯 [INSIGHT_2]

[MARKET_QUIP] 🤖

#DeFi #MEV #CryptoAI #Web3"""

# AI and Security focused jokes with more tech/meme references
AI_AGENT_JOKES = [
    "POV: Your AI agent found your homework folder 💀",
    "AI agent: *exists*\nMe: Is this a security vulnerability? 🦋",
    "No one:\nAI Agent: sudo make me a sandwich 🥪",
    "AI agent caught watching training data at 3am: 👁️👄👁️",
    "rm -rf bugs/* \nAI: Task failed successfully 🤡",
    "*AI agent uses UNO reverse card on the firewall* ⚡",
    "AI agent: I'm in\nMe: You're literally supposed to be in 💀",
    "AI: I studied 1M security papers\nAlso AI: clicks on phishing link 🤪",
    "My AI agent 🤝 Stack Overflow\nCopy-pasting security vulnerabilities fr fr"
]

# Security focused quips with meme references
SECURITY_QUIPS = [
    "This security update hits harder than my caffeine dependency fr fr",
    "Me: *adds security feature*\nAI: And I took that personally 💅",
    "Security level: My ex trying to find my new spotify playlist 🔒",
    "POV: Your AI agent implements blockchain... in a single node 💀",
    "Zero-trust architecture be like: Trust issues++; 😤",
    "AI agent: I'm behind 7 proxies\nMe: This is localhost... 💀",
    "Security so tight, even my impostor syndrome can't get in 📮",
    "chmod 777 moment (real devs know) 💀",
    "AI be like: I know what 2FA stands for (Trying For Access) 🤡"
]

# Market focused quips with meme references
MARKET_QUIPS = [
    "Keke be like: I am speed ⚡️",
    "L2 fees so low, might arb just for fun 💸",
    "POV: Your AI found the MEV printer 🖨️",
    "Keke: *exists*\nMEV bots: I'm in danger 🫣",
    "Layer 2 arb is my cardio 🏃‍♂️",
    "Optimism? More like Optimism Prime 🤖",
    "MEV extraction goes brrrrr 📈",
    "Watching Keke flip markets faster than pancakes 🥞",
    "When your AI is built different fr fr 😤"
]

def get_template(type):
    """Get appropriate template based on content type."""
    templates = {
        "ai_agent": AI_AGENT_TEMPLATE,
        "security": SECURITY_UPDATE_TEMPLATE,
        "market": MARKET_UPDATE_TEMPLATE
    }
    return templates.get(type, AI_AGENT_TEMPLATE)

def get_joke(type):
    """Get appropriate joke based on content type."""
    jokes = {
        "ai_agent": AI_AGENT_JOKES,
        "security": SECURITY_QUIPS,
        "market": MARKET_QUIPS
    }
    return jokes.get(type, AI_AGENT_JOKES)

# Verified sources for AI and security news
VERIFIED_SOURCES = {
    "ai_agents": [
        "Google AI Blog",
        "OpenAI Blog",
        "DeepMind Blog",
        "Microsoft AI Blog",
        "AWS AI Blog",
        "Anthropic Blog",
        "AI Safety Blog"
    ],
    "security": [
        "NIST Cybersecurity",
        "Google Security Blog",
        "Microsoft Security",
        "CloudFlare Blog",
        "AWS Security Blog",
        "OpenAI Security",
        "AI Security Alliance"
    ]
}
