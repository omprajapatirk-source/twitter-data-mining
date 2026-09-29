"""
Term Frequency and Co-occurrence Analyzer
Based on Marco Bonzanini's Data Mining Architecture (Part 3)
Calculates Unigrams, Bigrams, Co-occurrence Matrices, and PMI (Pointwise Mutual Information).
"""

import math
from collections import Counter, defaultdict
from typing import Iterable
from .tokenizer import TwitterTokenizer

class TwitterAnalyzer:
    """Analyzes a collection of tweets for frequencies, bigrams, and term co-occurrences."""

    def __init__(self, tokenizer: TwitterTokenizer = None):
        self.tokenizer = tokenizer or TwitterTokenizer()

    def analyze_tweets(self, tweets: list[dict], min_word_len: int = 2) -> dict:
        """
        Runs comprehensive analysis over a list of tweet objects.
        Expected tweet format: {"text": str, "created_at": str, ...}
        """
        unigram_counts = Counter()
        bigram_counts = Counter()
        hashtag_counts = Counter()
        mention_counts = Counter()
        emoji_counts = Counter()
        com_matrix = defaultdict(lambda: defaultdict(int))
        total_tweets = len(tweets)
        time_distribution = Counter()

        for tweet in tweets:
            text = tweet.get("text", "")
            if not text:
                continue

            # Time grouping (e.g. YYYY-MM-DD or YYYY-MM-DD HH:00)
            created_at = tweet.get("created_at", "")
            if created_at:
                date_key = created_at[:13] if len(created_at) >= 13 else created_at[:10]
                time_distribution[date_key] += 1

            # Extract specific entities
            entities = self.tokenizer.extract_entities(text)
            for ht in entities["hashtags"]:
                hashtag_counts[ht] += 1
            for mn in entities["mentions"]:
                mention_counts[mn] += 1
            for emo in entities["emoticons"]:
                emoji_counts[emo] += 1

            # Preprocessed terms for frequency & co-occurrence
            terms = self.tokenizer.preprocess(
                text,
                lowercase=True,
                remove_stopwords=True,
                remove_punctuation=True,
                remove_urls=True
            )

            # Filter single character terms or noise
            clean_terms = [t for t in terms if len(t) >= min_word_len and not t.startswith('http')]

            # Unigrams
            for term in clean_terms:
                unigram_counts[term] += 1

            # Bigrams
            for i in range(len(clean_terms) - 1):
                bigram = (clean_terms[i], clean_terms[i + 1])
                bigram_counts[f"{bigram[0]} {bigram[1]}"] += 1

            # Co-occurrence matrix (unique terms per tweet to count document co-occurrence)
            unique_terms = sorted(list(set(clean_terms)))
            for i in range(len(unique_terms)):
                for j in range(i + 1, len(unique_terms)):
                    w1, w2 = unique_terms[i], unique_terms[j]
                    com_matrix[w1][w2] += 1
                    com_matrix[w2][w1] += 1

        return {
            "total_tweets": total_tweets,
            "top_terms": unigram_counts.most_common(50),
            "top_bigrams": bigram_counts.most_common(30),
            "top_hashtags": hashtag_counts.most_common(25),
            "top_mentions": mention_counts.most_common(20),
            "top_emoticons": emoji_counts.most_common(15),
            "time_series": dict(sorted(time_distribution.items())),
            "unigram_counts": dict(unigram_counts),
            "co_occurrence_matrix": {k: dict(v) for k, v in com_matrix.items()}
        }

    def compute_pmi(
        self,
        target_term: str,
        unigram_counts: dict[str, int],
        co_occurrence_matrix: dict[str, dict[str, int]],
        total_tweets: int,
        min_co_occurrences: int = 2
    ) -> list[tuple[str, float]]:
        """
        Calculates Pointwise Mutual Information (PMI) for a given target word against all co-occurring words.
        PMI(x, y) = log2( P(x, y) / (P(x) * P(y)) )
        """
        target = target_term.lower()
        if target not in unigram_counts or total_tweets == 0:
            return []

        p_x = unigram_counts[target] / total_tweets
        pmi_scores = []
        target_co = co_occurrence_matrix.get(target, {})

        for other_term, co_count in target_co.items():
            if co_count < min_co_occurrences:
                continue
            p_y = unigram_counts.get(other_term, 0) / total_tweets
            p_xy = co_count / total_tweets

            if p_x > 0 and p_y > 0 and p_xy > 0:
                pmi = math.log2(p_xy / (p_x * p_y))
                pmi_scores.append((other_term, round(pmi, 4)))

        pmi_scores.sort(key=lambda item: item[1], reverse=True)
        return pmi_scores

    def get_network_graph(self, co_occurrence_matrix: dict, top_n_terms: list[str], max_edges: int = 60) -> dict:
        """Generates node & edge data for interactive graph visualization (Vis.js / D3)."""
        nodes = [{"id": term, "label": term, "value": 1} for term in top_n_terms]
        edges = []
        seen = set()

        for w1 in top_n_terms:
            neighbors = co_occurrence_matrix.get(w1, {})
            for w2, count in neighbors.items():
                if w2 in top_n_terms:
                    pair = tuple(sorted([w1, w2]))
                    if pair not in seen and count > 0:
                        seen.add(pair)
                        edges.append({
                            "from": pair[0],
                            "to": pair[1],
                            "value": count,
                            "title": f"{pair[0]} & {pair[1]}: {count} co-occurrences"
                        })

        # Sort edges by weight and limit
        edges.sort(key=lambda e: e["value"], reverse=True)
        edges = edges[:max_edges]

        return {"nodes": nodes, "edges": edges}
