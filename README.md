# Wikipedia Web Scraping & Analysis Tool

A powerful web application that scrapes and analyzes Wikipedia articles, providing detailed insights and metrics about the content.

## 🚀 Features

- Web scraping of Wikipedia articles
- Text analysis including sentiment analysis
- Reading level assessment
- Word and sentence statistics
- Interactive web interface
- Export analysis results to JSON

## 🛠️ Tech Stack

### Backend
- **Python 3.x** - Core programming language
- **Streamlit** - Web application framework
- **BeautifulSoup4** - Web scraping
- **NLTK** - Natural Language Processing
- **TextBlob** - Sentiment analysis
- **Pandas** - Data manipulation
- **Requests** - HTTP requests

### Frontend
- **Streamlit Components** - UI components
- **Custom CSS** - Styling and layout
- **JavaScript** - Interactive elements

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/abhisek-raj/web_scraping-bot.git
   cd web_scraping-bot
   ```

2. **Create and activate a virtual environment** (recommended)
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # On Windows
   source venv/bin/activate  # On macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   python -m nltk.downloader punkt
   ```

### Running the Application

```bash
streamlit run app.py
```

Then open your browser and navigate to `http://localhost:8501`

## 📊 Features in Detail

### Article Analysis
- Word count and sentence statistics
- Reading time estimation
- Sentiment analysis (polarity and subjectivity)
- Text complexity metrics
- Section-wise content analysis

### Data Export
- Export analysis results as JSON
- Copy article summaries
- Save analysis reports

## 📂 Project Structure

```
.
├── .gitignore          # Git ignore file
├── README.md           # This file
├── app.py             # Main application file
├── requirements.txt   # Python dependencies
├── articles_extracted/ # Directory for extracted articles
└── output/            # Directory for analysis outputs
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Wikipedia for their API and content
- Streamlit for the amazing web framework
- NLTK and TextBlob for NLP capabilities