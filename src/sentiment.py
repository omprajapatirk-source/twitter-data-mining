"""
Sentiment Analysis and Topic Categorization Module
Based on Marco Bonzanini's Twitter Data Mining Architecture (Part 4 & 6)
Provides lexicon-based polarity scoring, negation handling, emoticon weighting, and topic categorization.
"""

import re
from .tokenizer import TwitterTokenizer

# Sentiment Lexicons
POSITIVE_WORDS = {
    "good", "great", "awesome", "excellent", "happy", "love", "loved", "loving", "best", "fantastic",
    "amazing", "wonderful", "perfect", "brilliant", "super", "nice", "cool", "top", "win", "winner",
    "winning", "excited", "exciting", "innovative", "success", "successful", "glad", "proud", "favorite",
    "favourite", "impressive", "recommend", "recommended", "beautiful", "clean", "fast", "powerful",
    "positive", "gain", "profit", "bullish", "breakthrough", "achievement", "enjoy", "enjoyed", "valuable"
}

NEGATIVE_WORDS = {
    "bad", "terrible", "awful", "worst", "hate", "hated", "hating", "sad", "angry", "broken",
    "fail", "failed", "failing", "failure", "boring", "slow", "bug", "bugs", "buggy", "crash",
    "crashes", "crashed", "poor", "horrible", "disappointed", "disappointing", "useless", "waste",
    "loss", "lost", "losing", "problem", "problems", "error", "errors", "scam", "bearish", "garbage",
    "trash", "annoying", "annoyed", "frustrating", "frustrated", "negative", "hate", "issue", "issues"
}

EMOTICON_SENTIMENT = {
    ":)": 1.0, ":-)": 1.0, ":D": 1.5, ":-D": 1.5, ";)": 0.8, ";-)": 0.8,
    "<3": 1.5, "😊": 1.2, "🎉": 1.5, "🚀": 1.5, "🔥": 1.2, "❤️": 1.5, "👍": 1.0,
    ":(": -1.0, ":-(": -1.0, ":'(": -1.5, "D:": -1.2, "👎": -1.0, "💔": -1.5, "😢": -1.2, "😡": -1.5
}

NEGATIONS = {"not", "no", "never", "hardly", "barely", "scarcely", "isn't", "aren't", "wasn't", "weren't", "don't", "doesn't", "didn't", "won't", "wouldn't", "can't", "couldn't"}
INTENSIFIERS = {"very": 1.5, "extremely": 2.0, "super": 1.5, "really": 1.4, "incredibly": 2.0, "absolutely": 1.8, "highly": 1.5, "too": 1.3}

TOPIC_KEYWORDS = {
    "Artificial Intelligence & ML": {"ai", "gpt", "llm", "machinelearning", "deeplearning", "nlp", "neural", "gemini", "claude", "chatgpt", "openai", "model", "agents"},
    "Software & Tech": {"python", "javascript", "coding", "developer", "opensource", "github", "programming", "software", "api", "database", "cloud", "aws", "linux"},
    "Business & Markets": {"startup", "finance", "stocks", "market", "economy", "crypto", "bitcoin", "investment", "growth", "revenue", "funding", "business"},
    "Sports & Entertainment": {"football", "soccer", "basketball", "nba", "movie", "gaming", "music", "concert", "championship", "rugby", "cricket"},
    "Science & Climate": {"space", "nasa", "climate", "environment", "energy", "physics", "earth", "renewable", "solar", "research"}
}

class TwitterSentimentAnalyzer:
    """Analyzes tweet sentiment and identifies topics based on text patterns and lexicons."""

    def __init__(self, tokenizer: TwitterTokenizer = None):
        self.tokenizer = tokenizer or TwitterTokenizer()

    def analyze_text(self, text: str) -> dict:
        """
        Calculates sentiment polarity score (-1.0 to 1.0) and label (positive, neutral, negative).
        Accounts for negations, intensifiers, and emoticons.
        """
        if not text:
            return {"score": 0.0, "label": "neutral", "pos_count": 0, "neg_count": 0}

        tokens = self.tokenizer.preprocess(
            text,
            lowercase=True,
            remove_stopwords=False,
            remove_punctuation=False,
            remove_urls=True
        )

        pos_score = 0.0
        neg_score = 0.0
        negation_active = False
        negation_window = 0
        current_multiplier = 1.0

        for i, token in enumerate(tokens):
            # Check for emoticons or emojis
            if token in EMOTICON_SENTIMENT:
                emo_val = EMOTICON_SENTIMENT[token]
                if emo_val > 0:
                    pos_score += emo_val
                else:
                    neg_score += abs(emo_val)
                continue

            # Check negation
            if token in NEGATIONS:
                negation_active = True
                negation_window = 3
                continue

            # Check intensifier
            if token in INTENSIFIERS:
                current_multiplier = INTENSIFIERS[token]
                continue

            # Decrement negation window
            if negation_window > 0:
                negation_window -= 1
            else:
                negation_active = False

            # Check sentiment words
            if token in POSITIVE_WORDS:
                val = 1.0 * current_multiplier
                if negation_active:
                    neg_score += val
                else:
                    pos_score += val
                current_multiplier = 1.0

            elif token in NEGATIVE_WORDS:
                val = 1.0 * current_multiplier
                if negation_active:
                    pos_score += val
                else:
                    neg_score += val
                current_multiplier = 1.0

        raw_diff = pos_score - neg_score
        total_signals = pos_score + neg_score

        # Normalized compound score between -1.0 and 1.0
        if total_signals == 0:
            score = 0.0
        else:
            score = raw_diff / (total_signals + 1.0)

        score = round(max(-1.0, min(1.0, score)), 3)

        if score >= 0.08:
            label = "positive"
        elif score <= -0.08:
            label = "negative"
        else:
            label = "neutral"

        return {
            "score": score,
            "label": label,
            "pos_score": round(pos_score, 2),
            "neg_score": round(neg_score, 2)
        }

    def categorize_topic(self, text: str) -> str:
        """Classifies tweet into dominant topic category."""
        tokens = set(self.tokenizer.preprocess(text, lowercase=True, remove_stopwords=True))
        best_topic = "General / Miscellaneous"
        max_overlap = 0

        for topic, keywords in TOPIC_KEYWORDS.items():
            overlap = len(tokens.intersection(keywords))
            if overlap > max_overlap:
                max_overlap = overlap
                best_topic = topic

        return best_topic

    def analyze_batch(self, tweets: list[dict]) -> dict:
        """Analyzes a collection of tweets for aggregate sentiment distribution and topic metrics."""
        sentiment_counts = {"positive": 0, "neutral": 0, "negative": 0}
        topic_counts = {}
        scored_tweets = []
        total_score = 0.0

        for tweet in tweets:
            text = tweet.get("text", "")
            sent_res = self.analyze_text(text)
            topic = self.categorize_topic(text)

            sentiment_counts[sent_res["label"]] += 1
            topic_counts[topic] = topic_counts.get(topic, 0) + 1
            total_score += sent_res["score"]

            annotated_tweet = {
                **tweet,
                "sentiment": sent_res,
                "topic": topic
            }
            scored_tweets.append(annotated_tweet)

        total_tweets = len(tweets) or 1
        avg_polarity = round(total_score / total_tweets, 3)

        return {
            "sentiment_counts": sentiment_counts,
            "topic_counts": topic_counts,
            "average_polarity": avg_polarity,
            "annotated_tweets": scored_tweets
        }
