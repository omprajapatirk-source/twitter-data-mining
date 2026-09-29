# Twitter / X Data Mining & NLP Intelligence Suite
> An end-to-end Python social media data mining, custom regex tokenization, co-occurrence analysis, sentiment intelligence, and interactive visualization platform based on the classic architecture by **Marco Bonzanini**.

---

## 🌟 Overview & Architecture

This project implements the complete 5-part data mining workflow modernized for Python 3 and Twitter API v2, with offline dataset generation and a visual dashboard.

```
┌─────────────────────────┐
│ 1. Data Ingestion Hub   │  <-- Live Twitter API v2 (Tweepy) & Realistic Mock Stream Generator
└────────────┬────────────┘
             │ JSONL Storage
┌────────────▼────────────┐
│ 2. Custom NLP Tokenizer │  <-- Regex entity extraction (@mentions, #hashtags, URLs, Emojis, Emoticons)
└────────────┬────────────┘
             │ Normalized Tokens & Stopword Filtering
┌────────────▼────────────┐
│ 3. Frequency & Co-occur │  <-- Unigrams, Bigrams, n x n Co-occurrence Matrix, Pointwise Mutual Info (PMI)
└────────────┬────────────┘
             │ Lexicon & Sentiment Rules
┌────────────▼────────────┐
│ 4. Sentiment & Topics   │  <-- Polarity scoring (-1.0 to +1.0), Negation weighting, Topic clustering
└────────────┬────────────┘
             │ REST APIs
┌────────────▼────────────┐
│ 5. Interactive Dashboard│  <-- Glassmorphism UI, Chart.js, Vis.js Network Graph, Leaflet Geo Map
└─────────────────────────┘
```

---

## 🚀 Quick Start

### 1. Installation
Ensure Python 3.10+ is installed, then install the dependencies:
```bash
cd C:\Users\Om\.gemini\antigravity-ide\scratch\twitter-data-mining
pip install -r requirements.txt
```

### 2. Run the Command-Line Pipeline (CLI)
Run the complete multi-stage pipeline directly in your terminal:
```bash
# Run all steps sequentially (Tokenizer test, Ingestion, Frequencies, PMI, Sentiment)
python cli.py all

# Or run individual steps:
python cli.py tokenize       # Test custom regex tokenizer & entity extraction
python cli.py collect --count 50   # Ingest or generate 50 fresh tweets
python cli.py analyze        # Output top unigrams, bigrams, hashtags, and PMI
python cli.py sentiment      # Output sentiment breakdown & topic distribution
```

### 3. Launch the Interactive Web Dashboard
```bash
python server.py
```
Open **`http://localhost:5000`** in your browser.

---

## 💡 Key Features & Modules

### 1. Text Pre-Processing (`src/tokenizer.py`)
- Custom multi-component regex capturing emoticons (e.g. `:)`, `:D`), Unicode emojis (🚀, 🔥), Twitter handles (`@user`), hashtags (`#topic`), numbers, and URLs.
- Stopwords filtering tailored for social media noise (e.g., `rt`, `via`, `amp`).
- Separate entity extraction engine for hashtag and mention extraction.

### 2. Term Frequencies & Co-occurrences (`src/analyzer.py`)
- Calculates Unigrams and Bigrams.
- Builds an $n \times n$ symmetric Co-occurrence Matrix to find terms appearing together.
- Calculates **Pointwise Mutual Information (PMI)**:
  $$\text{PMI}(x, y) = \log_2 \left( \frac{P(x, y)}{P(x) \cdot P(y)} \right)$$

### 3. Sentiment & Topic Classification (`src/sentiment.py`)
- Normalized sentiment polarity score $(-1.0 \text{ to } +1.0)$.
- Handles negation context windows (e.g. "not good" inverted to negative) and intensifiers ("super", "extremely").
- Emoticon and Emoji sentiment weights.
- Multi-topic categorization (AI/ML, Software/Tech, Business/Markets, Science/Climate, Sports).

### 4. Data Ingestion & Stream Collector (`src/collector.py`)
- **Live Mode**: Connects via `tweepy.Client` using Twitter API v2 Bearer Token.
- **Simulation / Offline Mode**: Generates realistic geotagged social streams across 10 global tech hubs with engagement metrics.

### 5. Interactive Visual Dashboard (`server.py` & `static/`)
- **Frequencies & Bigrams**: Real-time Chart.js bar visualizations.
- **Co-occurrence Network Graph**: Vis.js force-directed physics graph with clickable nodes.
- **PMI Explorer**: Live search for word associations.
- **Sentiment & Topics**: Doughnut charts, category distribution, and timeline volume.
- **Geo Tweet Map**: Interactive Leaflet.js dark map displaying geotagged tweets colored by sentiment.
- **Tweet Stream Explorer**: Real-time search, sentiment filter, and pagination.
- **Live NLP Sandbox**: Real-time testing of regex tokenization and entity extraction.

---

## ⚙️ Configuration (`.env`)
To use live Twitter API v2 endpoints instead of the simulated stream generator, copy `.env.example` to `.env`:
```env
TWITTER_BEARER_TOKEN=your_bearer_token_here
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
PORT=5000
```
*(If left blank, the application automatically uses the built-in realistic mock stream engine.)*
