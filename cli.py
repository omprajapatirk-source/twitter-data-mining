#!/usr/bin/env python
"""
Twitter Data Mining CLI Runner
Interactive command-line workflow demonstrating Marco Bonzanini's 5-part tutorial series.
"""

import sys
import argparse
from pathlib import Path

# Ensure Windows terminal outputs Unicode/Emojis safely
if sys.platform == "win32" and hasattr(sys.stdout, "buffer"):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from src.collector import TwitterCollector
from src.tokenizer import TwitterTokenizer
from src.analyzer import TwitterAnalyzer
from src.sentiment import TwitterSentimentAnalyzer
from src.mock_generator import save_mock_dataset
from src.config import DEFAULT_STREAM_FILE

def print_header(title: str):
    print("\n" + "=" * 65)
    print(f"  {title}")
    print("=" * 65)

def step_collect(count: int, query: str):
    print_header("PART 1: Data Collection & Ingestion")
    collector = TwitterCollector()
    tweets = collector.collect_recent_tweets(query=query, max_results=count)
    print(f"\n[+] Total Tweets Stored: {len(tweets)}")
    if tweets:
        sample = tweets[0]
        print(f"\nSample Tweet [ID: {sample['id']}]:")
        print(f"User: @{sample.get('user', {}).get('username', 'user')}")
        print(f"Text: {sample['text']}")
        print(f"Date: {sample['created_at']}")

def step_tokenize():
    print_header("PART 2: Text Pre-processing & Custom Tokenizer")
    sample_text = (
        "RT @py_dev: Just built an awesome #NLP pipeline with #Python & @tweepy! "
        "Check it out https://t.co/example :D #DataScience #AI 🚀"
    )
    tokenizer = TwitterTokenizer()

    print(f"Raw Tweet Text:\n\"{sample_text}\"\n")
    print("1. Raw Tokens (Custom Regex):")
    print(tokenizer.tokenize(sample_text))

    print("\n2. Extracted Entities:")
    entities = tokenizer.extract_entities(sample_text)
    for k, v in entities.items():
        print(f"   - {k.capitalize()}: {v}")

    print("\n3. Normalized & Filtered (Stopwords & Punctuation removed):")
    print(tokenizer.preprocess(sample_text, remove_stopwords=True, remove_punctuation=True, remove_urls=True))

def step_frequencies():
    print_header("PART 3: Term Frequencies, Bigrams & Co-occurrences")
    collector = TwitterCollector()
    tweets = collector.load_tweets()
    analyzer = TwitterAnalyzer()
    
    results = analyzer.analyze_tweets(tweets)

    print(f"Analyzed {results['total_tweets']} tweets.\n")
    print("Top 10 Terms (Unigrams):")
    for term, cnt in results["top_terms"][:10]:
        print(f"   {term:20s} : {cnt} times")

    print("\nTop 10 Bigrams:")
    for bg, cnt in results["top_bigrams"][:10]:
        print(f"   {bg:25s} : {cnt} times")

    print("\nTop 10 Hashtags:")
    for ht, cnt in results["top_hashtags"][:10]:
        print(f"   {ht:20s} : {cnt} times")

    # Pointwise Mutual Information (PMI) sample
    if results["top_terms"]:
        top_term = results["top_terms"][0][0]
        print(f"\nPointwise Mutual Information (PMI) for '{top_term}':")
        pmi_scores = analyzer.compute_pmi(
            top_term,
            results["unigram_counts"],
            results["co_occurrence_matrix"],
            results["total_tweets"]
        )
        for other, pmi in pmi_scores[:5]:
            print(f"   PMI({top_term}, {other:15s}) = {pmi:.4f}")

def step_sentiment():
    print_header("PART 4 & 6: Sentiment Analysis & Topic Categorization")
    collector = TwitterCollector()
    tweets = collector.load_tweets()
    sentiment_engine = TwitterSentimentAnalyzer()
    
    analysis = sentiment_engine.analyze_batch(tweets)
    counts = analysis["sentiment_counts"]
    total = len(tweets) or 1

    print(f"Analyzed {len(tweets)} tweets.")
    print(f"Average Polarity Score: {analysis['average_polarity']} (-1.0 to +1.0)\n")
    print("Sentiment Breakdown:")
    for label, count in counts.items():
        pct = (count / total) * 100
        print(f"   {label.capitalize():10s} : {count:3d} ({pct:5.1f}%)")

    print("\nTopic Breakdown:")
    for topic, count in analysis["topic_counts"].items():
        print(f"   {topic:30s} : {count:3d} tweets")

def main():
    parser = argparse.ArgumentParser(description="Mining Twitter Data with Python CLI")
    parser.add_argument("action", choices=["collect", "tokenize", "analyze", "sentiment", "all", "generate"],
                        nargs="?", default="all", help="Action step to run")
    parser.add_argument("--count", type=int, default=100, help="Number of tweets to collect/generate")
    parser.add_argument("--query", type=str, default="#python -is:retweet lang:en", help="Search query")
    args = parser.parse_args()

    if args.action == "collect":
        step_collect(args.count, args.query)
    elif args.action == "tokenize":
        step_tokenize()
    elif args.action == "analyze":
        step_frequencies()
    elif args.action == "sentiment":
        step_sentiment()
    elif args.action == "generate":
        print_header("Generating Fresh Synthetic Twitter Dataset")
        save_mock_dataset(DEFAULT_STREAM_FILE, count=args.count)
        print(f"[+] Successfully generated {args.count} realistic tweets at {DEFAULT_STREAM_FILE}")
    elif args.action == "all":
        step_tokenize()
        step_collect(args.count, args.query)
        step_frequencies()
        step_sentiment()
        print("\n" + "=" * 65)
        print("  [+] All Pipeline Steps Completed Successfully!")
        print("  To launch the Interactive Visual Dashboard, run:")
        print("     python server.py")
        print("=" * 65 + "\n")

if __name__ == "__main__":
    main()
