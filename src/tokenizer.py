"""
Twitter Custom Tokenizer
Based on Marco Bonzanini's NLP & Twitter Mining Preprocessing Architecture (Part 2)
Enhanced for modern Python 3 and emoji support.
"""

import re
import html
import string

# Emoticon regular expressions
EMOTICONS_STR = r"""
    (?:
      [<>]?
      [:;=8]                     # eyes
      [\-o\*\']?                 # optional nose
      [\)\]\(\[dDpP/\:\}\{@\|\\] # mouth
      |
      [\)\]\(\[dDpP/\:\}\{@\|\\] # mouth
      [\-o\*\']?                 # optional nose
      [:;=8]                     # eyes
      [<>]?
    )"""

# Regex components for Twitter-specific tokens
REGEX_PATTERNS = [
    EMOTICONS_STR,
    r'<[^>]+>',                                               # HTML tags
    r'(?:@[\w_]+)',                                           # Twitter @mentions
    r"(?:\#+[\w_]+[\w\'_\-]*[\w_]+)",                         # Twitter #hashtags
    r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',  # URLs
    r'(?:(?:\d+,?)+(?:\.?\d+)?)',                             # Numbers
    r"(?:[a-zA-Z]+(?:['\-_][a-zA-Z]+)*)",                     # Words with dashes/apostrophes
    r'(?:[\U00010000-\U0010ffff])',                           # Unicode Emojis
    r'(?:\S)'                                                 # Any other non-space char
]

# Compiled token regex
TOKENS_RE = re.compile(r'(' + '|'.join(REGEX_PATTERNS) + r')', re.VERBOSE | re.IGNORECASE | re.UNICODE)
EMOTICON_RE = re.compile(r'^' + EMOTICONS_STR + r'$', re.VERBOSE | re.IGNORECASE | re.UNICODE)

# Standard English stopwords + Twitter artifacts
DEFAULT_STOPWORDS = set([
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't",
    "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can't",
    "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during",
    "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't", "have", "haven't", "having",
    "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers", "herself", "him", "himself", "his", "how",
    "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its",
    "itself", "let's", "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on",
    "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "shan't",
    "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such", "than", "that", "that's",
    "the", "their", "theirs", "them", "themselves", "then", "there", "there's", "these", "they", "they'd",
    "they'll", "they're", "they've", "this", "those", "through", "to", "too", "under", "until", "up", "very",
    "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when",
    "when's", "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with", "won't",
    "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves",
    # Twitter specific noise terms
    "rt", "via", "http", "https", "amp", "co", "u", "ur", "im", "dont", "cant", "w", "lol", "omg"
])

PUNCTUATION_SET = set(string.punctuation) - {'#', '@'}

class TwitterTokenizer:
    """Tokenizer tailored for Twitter text with regex filtering and normalization."""

    def __init__(self, stopwords=None):
        self.stopwords = stopwords if stopwords is not None else DEFAULT_STOPWORDS

    def tokenize(self, text: str) -> list[str]:
        """Tokenizes text using the Bonzanini regex tokenizer without altering case."""
        if not text:
            return []
        # Unescape HTML characters (&amp; -> &)
        clean_text = html.unescape(text)
        return TOKENS_RE.findall(clean_text)

    def preprocess(
        self,
        text: str,
        lowercase: bool = True,
        remove_stopwords: bool = True,
        remove_punctuation: bool = True,
        remove_urls: bool = False,
        keep_mentions: bool = True,
        keep_hashtags: bool = True
    ) -> list[str]:
        """
        Full text pre-processing pipeline:
        - Tokenizes
        - Conditionally lowercases (preserves emoticon casing)
        - Removes stopwords, URLs, mentions, or punctuation based on flags
        """
        tokens = self.tokenize(text)
        processed = []

        for token in tokens:
            # Check if token is an emoticon (keep case for emoticons like :D vs :d)
            is_emoticon = bool(EMOTICON_RE.match(token))
            tok = token if (is_emoticon or not lowercase) else token.lower()

            tok_lower = tok.lower()

            # URL removal filter
            if remove_urls and (tok_lower.startswith('http://') or tok_lower.startswith('https://')):
                continue

            # Mention removal filter
            if not keep_mentions and tok.startswith('@'):
                continue

            # Hashtag removal filter
            if not keep_hashtags and tok.startswith('#'):
                continue

            # Stopword removal
            if remove_stopwords and tok_lower in self.stopwords:
                continue

            # Punctuation removal
            if remove_punctuation and tok in PUNCTUATION_SET:
                continue

            if tok.strip():
                processed.append(tok)

        return processed

    def extract_entities(self, text: str) -> dict:
        """Extracts hashtags, mentions, URLs, and emoticons separately."""
        tokens = self.tokenize(text)
        hashtags = [t.lower() for t in tokens if t.startswith('#') and len(t) > 1]
        mentions = [t.lower() for t in tokens if t.startswith('@') and len(t) > 1]
        urls = [t for t in tokens if t.startswith('http://') or t.startswith('https://')]
        emoticons = [t for t in tokens if EMOTICON_RE.match(t)]
        
        return {
            "hashtags": hashtags,
            "mentions": mentions,
            "urls": urls,
            "emoticons": emoticons
        }
