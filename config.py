"""
Configuration management for the podcast script generator.
Centralizes all settings and API keys.
"""

import os
from pathlib import Path
from typing import Dict
from datetime import datetime

# Base directories
BASE_DIR = Path(__file__).parent
SCRIPTS_DIR = BASE_DIR / "scripts"
LOGS_DIR = BASE_DIR / "logs"
OUTPUT_DIR = BASE_DIR / "output"
AUDIO_DIR = BASE_DIR / "output" / "audio"

# Create directories if they don't exist
SCRIPTS_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
AUDIO_DIR.mkdir(exist_ok=True)

# Podcast configuration - supports 15, 30, and 45 minute durations
# Duration can be set via PODCAST_DURATION_MINUTES environment variable
PODCAST_DURATION_MINUTES = int(os.getenv("PODCAST_DURATION_MINUTES", "30"))
# Clamp between 15-45 minutes (15, 30, or 45)
if PODCAST_DURATION_MINUTES < 15:
    PODCAST_DURATION_MINUTES = 15
elif PODCAST_DURATION_MINUTES > 45:
    PODCAST_DURATION_MINUTES = 45
elif PODCAST_DURATION_MINUTES not in [15, 30, 45]:
    # Round to nearest supported duration
    if PODCAST_DURATION_MINUTES < 22:
        PODCAST_DURATION_MINUTES = 15
    elif PODCAST_DURATION_MINUTES < 37:
        PODCAST_DURATION_MINUTES = 30
    else:
        PODCAST_DURATION_MINUTES = 45

# Base section weights (proportions that scale with duration)
BASE_SECTION_WEIGHTS = {
    "intro": 0.05,
    "main_stories": 0.65,  # Will be distributed across variable number of main stories
    "tech_spotlight": 0.15,
    "listener_questions": 0.08,  # Listener questions section
    "deep_dive": 0.10,  # Optional section
    "expert_interview": 0.10,  # Optional section
    "outro": 0.05,  # Increased to include thought-provoking question
    "transitions": 0.07
}

# Function to calculate dynamic section allocation based on duration
def calculate_section_allocation(duration_minutes: int) -> Dict:
    """
    Calculate section allocation based on target duration.
    
    Args:
        duration_minutes: Target duration in minutes (15, 30, or 45)
        
    Returns:
        Dictionary with section configurations
    """
    total_seconds = duration_minutes * 60
    words_per_minute = 150  # Average speaking pace
    target_word_count = duration_minutes * words_per_minute
    
    # Calculate number of main stories based on duration
    # 15 min: 2 stories, 30 min: 3 stories, 45 min: 4 stories
    if duration_minutes == 15:
        num_main_stories = 2
    elif duration_minutes == 30:
        num_main_stories = 3
    else:  # 45 minutes
        num_main_stories = 4
    
    # Allocate time for each section
    sections = {
        "intro": {
            "duration_seconds": int(total_seconds * BASE_SECTION_WEIGHTS["intro"]),
            "weight": BASE_SECTION_WEIGHTS["intro"],
            "word_count_target": int(target_word_count * BASE_SECTION_WEIGHTS["intro"])
        },
        "outro": {
            "duration_seconds": int(total_seconds * BASE_SECTION_WEIGHTS["outro"]),
            "weight": BASE_SECTION_WEIGHTS["outro"],
            "word_count_target": int(target_word_count * BASE_SECTION_WEIGHTS["outro"])
        },
        "tech_spotlight": {
            "duration_seconds": int(total_seconds * BASE_SECTION_WEIGHTS["tech_spotlight"]),
            "weight": BASE_SECTION_WEIGHTS["tech_spotlight"],
            "word_count_target": int(target_word_count * BASE_SECTION_WEIGHTS["tech_spotlight"])
        },
        "listener_questions": {
            "duration_seconds": int(total_seconds * BASE_SECTION_WEIGHTS["listener_questions"]),
            "weight": BASE_SECTION_WEIGHTS["listener_questions"],
            "word_count_target": int(target_word_count * BASE_SECTION_WEIGHTS["listener_questions"]),
            "enabled": True  # Enabled by default
        },
        "transitions": {
            "duration_seconds": int(total_seconds * BASE_SECTION_WEIGHTS["transitions"]),
            "weight": BASE_SECTION_WEIGHTS["transitions"]
        }
    }
    
    # Distribute main stories weight across variable number of stories
    main_story_weight = BASE_SECTION_WEIGHTS["main_stories"] / num_main_stories
    main_story_duration = int(total_seconds * main_story_weight)
    main_story_word_count = int(target_word_count * main_story_weight)
    
    for i in range(1, num_main_stories + 1):
        sections[f"main_story_{i}"] = {
            "duration_seconds": main_story_duration,
            "weight": main_story_weight,
            "word_count_target": main_story_word_count
        }
    
    # Optional sections (can be enabled via config)
    sections["deep_dive"] = {
        "duration_seconds": int(total_seconds * BASE_SECTION_WEIGHTS["deep_dive"]),
        "weight": BASE_SECTION_WEIGHTS["deep_dive"],
        "word_count_target": int(target_word_count * BASE_SECTION_WEIGHTS["deep_dive"]),
        "enabled": False  # Disabled by default, can be enabled per episode
    }
    
    sections["expert_interview"] = {
        "duration_seconds": int(total_seconds * BASE_SECTION_WEIGHTS["expert_interview"]),
        "weight": BASE_SECTION_WEIGHTS["expert_interview"],
        "word_count_target": int(target_word_count * BASE_SECTION_WEIGHTS["expert_interview"]),
        "enabled": False  # Disabled by default, can be enabled per episode
    }
    
    return sections

# Podcast configuration with dynamic section allocation
PODCAST_CONFIG = {
    "title": "Decoded: AI, Big Data, and Tech Futures",
    "duration_minutes": PODCAST_DURATION_MINUTES,
    "target_word_count": PODCAST_DURATION_MINUTES * 150,  # ~150 words per minute
    "sections": calculate_section_allocation(PODCAST_DURATION_MINUTES),
    "num_main_stories": 2 if PODCAST_DURATION_MINUTES == 15 else (3 if PODCAST_DURATION_MINUTES == 30 else 4),  # 2-4 stories based on duration
    "optional_sections": {
        "deep_dive": {"enabled": os.getenv("ENABLE_DEEP_DIVE", "false").lower() == "true"},
        "expert_interview": {"enabled": os.getenv("ENABLE_EXPERT_INTERVIEW", "false").lower() == "true"}
    }
}

# Content sources configuration
CONTENT_SOURCES = {
    "rss_feeds": [
        "https://feeds.feedburner.com/oreilly/radar",
        "https://www.wired.com/feed/rss",
        "https://techcrunch.com/feed/",
        "https://www.theverge.com/rss/index.xml",
        "https://feeds.feedburner.com/venturebeat/SZYF",
        "https://www.artificialintelligence-news.com/feed/",
        "https://www.datasciencecentral.com/feed/",
        "https://bigdata-madesimple.com/feed/",
        "https://spectrum.ieee.org/rss",  # IEEE Spectrum
        "https://ieeexplore.ieee.org/rss/TOC.jsp?punumber=5",  # IEEE Computer Society
    ],
    "academic_sources": {
        "arxiv": {
            "enabled": True,
            "categories": ["cs.AI", "cs.LG", "cs.CL", "stat.ML", "cs.CV", "cs.NE"],
            "max_results": 50,  # Increased from 20 for better content selection
            "days_back": 14  # Increased from 7 to capture more content
        },
        "ieee_spectrum": {
            "enabled": True,
            "rss_feed": "https://spectrum.ieee.org/rss"
        }
    },
    "github": {
        "enabled": True,
        "api_key": os.getenv("GITHUB_API_KEY", ""),  # Set via environment variable
        "topics": ["machine-learning", "artificial-intelligence", "deep-learning", "data-science"],
        "languages": ["python", "javascript", "julia", "r"],
        "max_results": 20  # Increased from 10 for better content selection
    },
    "data_portals": {
        "kaggle": {
            "enabled": True,
            "kaggle_json_path": BASE_DIR / "kaggle" / "kaggle.json",  # Path to kaggle.json
            "api_key": os.getenv("KAGGLE_API_KEY", ""),
            "username": os.getenv("KAGGLE_USERNAME", ""),
            "max_results": 10
        },
        "datagov": {
            "enabled": True,
            "max_results": 20  # Increased from 10
        },
        "worldbank": {
            "enabled": True,
            "max_results": 20  # Increased from 10
        }
    },
    "newsletter_feeds": {
        "enabled": True,
        "feeds": [
            # Add newsletter RSS feeds here when available
            # Google Alerts can be configured to send to RSS feed
        ]
    },
    "news_apis": {
        "newsapi": {
            "enabled": True,
            "api_key": os.getenv("NEWSAPI_KEY", os.getenv("NEWS_API_KEY", "")),
            "endpoints": [
                "https://newsapi.org/v2/everything",
                "https://newsapi.org/v2/top-headlines"
            ],
            "query_params": {
                "q": "AI OR artificial intelligence OR machine learning OR big data OR data science",
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": 50  # Increased from 20 for better content selection
            }
        },
        "reddit": {
            "enabled": True,
            "subreddits": [
                "r/MachineLearning",
                "r/artificial",
                "r/datascience",
                "r/bigdata",
                "r/technology",
                "r/Futurology"
            ],
            "sort": "hot",
            "limit": 10
        }
    },
    "web_scraping": {
        "enabled": True,
        "sources": [
            "https://www.technologyreview.com/topic/artificial-intelligence/",
            "https://www.technologyreview.com/topic/data/",
            "https://www.technologyreview.com/topic/computing/",
        ]
    }
}

# Content filtering keywords
TOPIC_KEYWORDS = {
    "ai": [
        "artificial intelligence", "machine learning", "deep learning",
        "neural network", "GPT", "LLM", "ChatGPT", "AI model", "AGI",
        "computer vision", "NLP", "natural language processing"
    ],
    "big_data": [
        "big data", "data analytics", "data science", "data warehouse",
        "data lake", "ETL", "data pipeline", "data engineering",
        "Apache Spark", "Hadoop", "data processing"
    ],
    "tech_futures": [
        "quantum computing", "blockchain", "Web3", "metaverse",
        "IoT", "edge computing", "5G", "6G", "autonomous vehicles",
        "robotics", "biotechnology", "nanotechnology", "future tech"
    ]
}

# Multi-topic episode support
# Can specify multiple topics per episode (default: all topics)
EPISODE_TOPICS = os.getenv("EPISODE_TOPICS", "").lower()
if EPISODE_TOPICS:
    # Parse comma-separated topics (e.g., "ai,big_data")
    EPISODE_TOPICS = [topic.strip() for topic in EPISODE_TOPICS.split(",") if topic.strip()]
    # Filter topic keywords to only include selected topics
    if EPISODE_TOPICS:
        filtered_keywords = {k: v for k, v in TOPIC_KEYWORDS.items() if k in EPISODE_TOPICS}
        if filtered_keywords:
            TOPIC_KEYWORDS = filtered_keywords
else:
    EPISODE_TOPICS = list(TOPIC_KEYWORDS.keys())  # Use all topics by default

# Update PODCAST_CONFIG with episode topics
PODCAST_CONFIG["episode_topics"] = EPISODE_TOPICS

# OpenAI configuration (for instructor and content processing)
OPENAI_CONFIG = {
    "api_key": os.getenv("OPENAI_API_KEY", ""),
    "model": os.getenv("OPENAI_MODEL", "gpt-4o"),
    "temperature": 0.7,
    "max_tokens": 4000
}

# ElevenLabs configuration (for text-to-speech/audio generation)
ELEVENLABS_CONFIG = {
    "api_key": os.getenv("ELEVENLABS_API_KEY", ""),
    "model": "eleven_multilingual_v2",  # Supports multiple languages
    "voice_preferences": {
        "preferred_voice": "Lyra",  # Try to use Lyra voice for conversational podcast
        "gender": "female",
        "accent": "british",
        "style": "conversational"  # Conversational style for podcast discussion
    },
    "voice_settings": {
        "stability": 0.6,  # Slightly higher for conversational feel
        "similarity_boost": 0.8,  # Higher for more natural voice
        "style": 0.3,  # Some style for conversational tone
        "use_speaker_boost": True
    }
}

# Script generation settings
SCRIPT_GENERATION = {
    "max_articles_per_section": 3,
    "min_article_length": 200,
    "max_article_length": 2000,
    "include_quotes": True,
    "include_statistics": True,
    "tone": "conversational",
    "style": "engaging and accessible",
    "use_optimized_prompt": True,  # Use the optimized ChatGPT prompt template
    "target_word_count": 4800,  # For 30-45 minute podcast
    "include_pauses": True,  # Include [pause] markers for natural delivery
    "include_placeholders": True,  # Include bracketed placeholders for customization
    "single_host_mode": os.getenv("SINGLE_HOST_MODE", "false").lower() == "true"  # Enable single-host format
}

# Logging configuration
LOGGING_CONFIG = {
    "level": os.getenv("LOG_LEVEL", "INFO"),
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": LOGS_DIR / "podcast_generator.log"
}

# Output formats
OUTPUT_FORMATS = {
    "script": {
        "format": "markdown",
        "include_timestamps": True,
        "include_word_count": True,
        "include_sources": True
    },
    "audio_notes": {
        "format": "plain_text",
        "include_pauses": True,
        "include_emphasis": True
    }
}

# Podcast publishing configuration
# RSS feed and podcast distribution settings
RSS_DIR = BASE_DIR / "output" / "rss"
RSS_DIR.mkdir(parents=True, exist_ok=True)

COVER_ART_DIR = BASE_DIR / "output" / "cover_art"
COVER_ART_DIR.mkdir(parents=True, exist_ok=True)

EPISODES_DB_PATH = BASE_DIR / "output" / "episodes.json"
EPISODES_DB_PATH.parent.mkdir(parents=True, exist_ok=True)

PODCAST_PUBLISHING_CONFIG = {
    "podcast_title": os.getenv("PODCAST_TITLE", "DECODED"),
    "podcast_description": os.getenv(
        "PODCAST_DESCRIPTION",
        "Weekly podcast covering the latest developments in AI, Big Data, and technology futures. "
        "Exploring cutting-edge research, industry trends, and their real-world implications."
    ),
    "podcast_author": os.getenv("PODCAST_AUTHOR", "AIPodCast Generator"),
    "podcast_language": os.getenv("PODCAST_LANGUAGE", "en-US"),
    "podcast_copyright": os.getenv("PODCAST_COPYRIGHT", f"Copyright {datetime.now().year}"),
    "podcast_categories": [
        {"category": "Technology", "subcategory": "Tech News"},
        {"category": "Science", "subcategory": "Natural Sciences"}
    ],
    "podcast_explicit": os.getenv("PODCAST_EXPLICIT", "false").lower() == "true",
    # Base URL for podcast files (must be publicly accessible)
    # Set via PODCAST_BASE_URL environment variable
    "base_url": os.getenv("PODCAST_BASE_URL", "https://your-domain.com/podcast"),
    "website_url": os.getenv("PODCAST_WEBSITE_URL", "https://your-website.com"),
    "cover_art_url": os.getenv("PODCAST_COVER_ART_URL", "https://your-domain.com/podcast/cover-art.jpg"),
    "rss_feed_url": os.getenv("PODCAST_RSS_FEED_URL", "https://your-domain.com/podcast/feed.xml"),
    "rss_feed_filename": "podcast_feed.xml",
    "cover_art_filename": "cover_art.png",
    # Email for podcast owner (optional but recommended)
    "podcast_email": os.getenv("PODCAST_EMAIL", ""),
    # Maximum number of episodes to include in RSS feed (0 = all)
    "max_episodes_in_feed": int(os.getenv("PODCAST_MAX_EPISODES_IN_FEED", "50")),
}

