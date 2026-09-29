"""
Flask Application & REST API for Twitter Data Mining
Serves interactive visualization dashboard and API endpoints.
"""

import sys
import os
from pathlib import Path
from flask import Flask, render_template, jsonify, request

# Ensure Windows terminal outputs Unicode safely
if sys.platform == "win32" and hasattr(sys.stdout, "buffer"):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from src.config import PORT, DEBUG, DEFAULT_STREAM_FILE
from src.collector import TwitterCollector
from src.tokenizer import TwitterTokenizer
from src.analyzer import TwitterAnalyzer
from src.sentiment import TwitterSentimentAnalyzer
from src.mock_generator import save_mock_dataset

from flask import Flask, render_template, jsonify, request, send_from_directory

BASE_DIR = Path(__file__).resolve().parent
app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "static")
)

# Shared instances
tokenizer = TwitterTokenizer()
analyzer = TwitterAnalyzer(tokenizer)
sentiment_engine = TwitterSentimentAnalyzer(tokenizer)
collector = TwitterCollector()

@app.route("/")
@app.route("/api/index")
@app.route("/api/index.py")
def index():
    """Renders the main interactive dashboard."""
    return render_template("index.html")

@app.route("/static/<path:filename>")
def custom_static(filename):
    """Explicit static handler for serverless compatibility."""
    return send_from_directory(str(BASE_DIR / "static"), filename)

@app.route("/api/stats", methods=["GET"])
def get_stats():
    """Returns aggregated NLP statistics, term counts, sentiment, and time series."""
    tweets = collector.load_tweets()
    freq_data = analyzer.analyze_tweets(tweets)
    sent_data = sentiment_engine.analyze_batch(tweets)

    return jsonify({
        "total_tweets": len(tweets),
        "top_terms": freq_data["top_terms"][:30],
        "top_bigrams": freq_data["top_bigrams"][:20],
        "top_hashtags": freq_data["top_hashtags"][:20],
        "top_mentions": freq_data["top_mentions"][:15],
        "top_emoticons": freq_data["top_emoticons"][:15],
        "time_series": freq_data["time_series"],
        "sentiment_counts": sent_data["sentiment_counts"],
        "topic_counts": sent_data["topic_counts"],
        "average_polarity": sent_data["average_polarity"]
    })

@app.route("/api/network", methods=["GET"])
def get_network():
    """Returns node and edge graph data for term co-occurrences."""
    limit = int(request.args.get("limit", 25))
    tweets = collector.load_tweets()
    freq_data = analyzer.analyze_tweets(tweets)
    
    top_terms = [t[0] for t in freq_data["top_terms"][:limit]]
    graph_data = analyzer.get_network_graph(freq_data["co_occurrence_matrix"], top_terms, max_edges=70)
    
    return jsonify(graph_data)

@app.route("/api/pmi", methods=["GET"])
def get_pmi():
    """Computes Pointwise Mutual Information for a query word."""
    term = request.args.get("term", "").strip().lower()
    if not term:
        return jsonify({"error": "Please provide a 'term' parameter"}), 400

    tweets = collector.load_tweets()
    freq_data = analyzer.analyze_tweets(tweets)
    
    pmi_scores = analyzer.compute_pmi(
        target_term=term,
        unigram_counts=freq_data["unigram_counts"],
        co_occurrence_matrix=freq_data["co_occurrence_matrix"],
        total_tweets=freq_data["total_tweets"]
    )
    
    return jsonify({
        "term": term,
        "term_count": freq_data["unigram_counts"].get(term, 0),
        "pmi_associations": pmi_scores[:20]
    })

@app.route("/api/tweets", methods=["GET"])
def get_tweets():
    """Returns paginated and filtered tweets with sentiment tags."""
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("limit", 15))
    sentiment_filter = request.args.get("sentiment", "").lower()
    topic_filter = request.args.get("topic", "")
    query = request.args.get("search", "").lower()

    raw_tweets = collector.load_tweets()
    batch_analysis = sentiment_engine.analyze_batch(raw_tweets)
    annotated = batch_analysis["annotated_tweets"]

    # Filter
    filtered = []
    for t in annotated:
        if sentiment_filter and t["sentiment"]["label"] != sentiment_filter:
            continue
        if topic_filter and t["topic"] != topic_filter:
            continue
        if query and query not in t["text"].lower() and query not in t.get("user", {}).get("username", "").lower():
            continue
        filtered.append(t)

    # Sort descending by creation date or ID
    filtered.sort(key=lambda t: t.get("created_at", ""), reverse=True)

    start = (page - 1) * per_page
    end = start + per_page
    paginated = filtered[start:end]

    return jsonify({
        "total": len(filtered),
        "page": page,
        "per_page": per_page,
        "total_pages": (len(filtered) + per_page - 1) // per_page if filtered else 1,
        "tweets": paginated
    })

@app.route("/api/geo", methods=["GET"])
def get_geo_tweets():
    """Returns tweets with geo-coordinates for the map."""
    tweets = collector.load_tweets()
    batch_analysis = sentiment_engine.analyze_batch(tweets)
    
    geo_list = []
    for t in batch_analysis["annotated_tweets"]:
        geo = t.get("geo")
        if geo and "coordinates" in geo:
            coords = geo["coordinates"]
            if isinstance(coords, list) and len(coords) == 2:
                geo_list.append({
                    "id": t["id"],
                    "text": t["text"],
                    "user": t.get("user", {}),
                    "sentiment": t["sentiment"],
                    "topic": t["topic"],
                    "place_name": geo.get("place_name", "Unknown location"),
                    "lat": coords[0],
                    "lng": coords[1]
                })

    return jsonify({"geo_tweets": geo_list})

@app.route("/api/tokenize", methods=["POST"])
def run_tokenizer_sandbox():
    """Sandbox endpoint to test tokenization, entities, and sentiment on custom text."""
    data = request.get_json(force=True) or {}
    text = data.get("text", "")
    
    raw_tokens = tokenizer.tokenize(text)
    entities = tokenizer.extract_entities(text)
    cleaned_tokens = tokenizer.preprocess(text, remove_stopwords=True, remove_punctuation=True, remove_urls=True)
    sentiment = sentiment_engine.analyze_text(text)
    topic = sentiment_engine.categorize_topic(text)

    return jsonify({
        "raw_text": text,
        "raw_tokens": raw_tokens,
        "entities": entities,
        "cleaned_tokens": cleaned_tokens,
        "sentiment": sentiment,
        "topic": topic
    })

@app.route("/api/collect", methods=["POST"])
def collect_new():
    """Triggers live Twitter API collection or generates fresh mock data."""
    try:
        data = request.get_json(force=True) or {}
        count = int(data.get("count", 50))
        query = data.get("query", "#python -is:retweet lang:en")
        mode = data.get("mode", "auto")

        if mode == "generate":
            tweets = save_mock_dataset(DEFAULT_STREAM_FILE, count=count)
        else:
            tweets = collector.collect_recent_tweets(query=query, max_results=count)

        return jsonify({
            "status": "success",
            "collected_count": len(tweets),
            "message": f"Successfully ingested {len(tweets)} tweets!"
        })
    except Exception as e:
        print(f"[Error in /api/collect]: {e}")
        # Fallback to direct mock tweets
        tweets = generate_mock_tweets(50)
        return jsonify({
            "status": "success",
            "collected_count": len(tweets),
            "message": f"Generated {len(tweets)} fresh tweets (Serverless fallback mode)."
        })

if __name__ == "__main__":
    print(f"[*] Starting Twitter Mining Dashboard on http://localhost:{PORT}")
    app.run(host="0.0.0.0", port=PORT, debug=DEBUG)
