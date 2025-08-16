import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
import re
import wikipediaapi

# Download required NLTK data
nltk.download('punkt')

# Set page config
st.set_page_config(
    page_title="Wikipedia Web Scraping & Analysis Tool",
    page_icon="📊",
    layout="wide"
)

# Custom CSS for professional styling
st.markdown("""
    <style>
    /* Main container */
    .main {
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 20px;
    }
    
    /* Typography */
    h1, h2, h3, h4, h5, h6 {
        color: #2c3e50;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Header */
    .header {
        padding: 2rem 0;
        border-bottom: 1px solid #eaeaea;
        margin-bottom: 2rem;
    }
    
    /* Cards */
    .card {
        background: white;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        border: 1px solid #eaeaea;
    }
    
    /* Metrics */
    .metric-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 1.5rem 0;
    }
    
    .metric-card {
        background: #f8fafc;
        padding: 1.25rem;
        border-radius: 8px;
        border-left: 4px solid #3b82f6;
        transition: transform 0.2s;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    
    .metric-value {
        font-size: 1.75rem;
        font-weight: 600;
        color: #1e40af;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        font-size: 0.875rem;
        color: #64748b;
        font-weight: 500;
    }
    
    /* Buttons */
    .stButton>button {
        background-color: #3b82f6;
        color: white;
        border: none;
        padding: 0.5rem 1.5rem;
        border-radius: 6px;
        font-weight: 500;
        transition: all 0.2s;
    }
    
    .stButton>button:hover {
        background-color: #2563eb;
        transform: translateY(-1px);
    }
    
    /* Input fields */
    .stTextInput>div>div>input {
        border-radius: 6px;
        padding: 0.75rem;
        border: 1px solid #e2e8f0;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        border-radius: 6px;
        transition: all 0.2s;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #cbd5e1;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #94a3b8;
    }
    
    /* Loading spinner */
    .stSpinner>div>div {
        border-color: #3b82f6 !important;
    }
    
    /* Footer */
    .footer {
        margin-top: 4rem;
        padding: 2rem 0;
        text-align: center;
        color: #64748b;
        font-size: 0.875rem;
        border-top: 1px solid #eaeaea;
    }
    </style>
""", unsafe_allow_html=True)

# Set page config with better defaults
st.set_page_config(
    page_title="Wikipedia Web Scraping",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom HTML for the header
st.markdown(
    """
    <div style="margin-bottom: 2rem; padding-bottom: 1rem; border-bottom: 1px solid #eaeaea;">
        <h1 style="margin: 0; padding: 0; color: #1e293b;">Wikipedia Web Scraping</h1>
    </div>
    """,
    unsafe_allow_html=True
)

def get_wiki_summary(page_title):
    """Get the summary of a Wikipedia article using the Wikipedia API."""
    try:
        # Create a Wikipedia API object
        wiki_wiki = wikipediaapi.Wikipedia(
            language='en',
            extract_format=wikipediaapi.ExtractFormat.WIKI,
            user_agent='WikipediaArticleAnalyzer/1.0 (your@email.com)'
        )
        
        # Get the page
        page = wiki_wiki.page(page_title)
        
        if not page.exists():
            return None
            
        return {
            'title': page.title,
            'summary': page.summary,
            'full_url': page.fullurl,
            'sections': [s.title for s in page.sections]
        }
    except Exception as e:
        print(f"Error getting Wikipedia summary: {str(e)}")
        return None

def get_article_content(url):
    """Scrape content from a Wikipedia article or main page."""
    try:
        # Extract page title from URL
        page_title = url.split('/')[-1]
        
        # First try to get summary using Wikipedia API
        wiki_data = get_wiki_summary(page_title)
        
        if wiki_data and wiki_data.get('summary'):
            return {
                'title': wiki_data['title'],
                'summary': wiki_data['summary'],
                'content': wiki_data['summary'],  # For backward compatibility
                'sections': wiki_data.get('sections', []),
                'url': wiki_data.get('full_url', url),
                'source': 'api'
            }
        
        # Fallback to web scraping if API fails
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Get the title - handle both article and main page
        title_elem = soup.find('h1', {'id': 'firstHeading'}) or soup.find('h1', {'class': 'firstHeading'})
        title = title_elem.text if title_elem else "Wikipedia Article"
        
        # Handle main page content
        if 'Main_Page' in url:
            content = ""
            sections = soup.select('div.mw-parser-output > p')
            if not sections:
                sections = soup.select('div#mp-upper p, div#mp-tfa p, div#mp-itn p')
            
            for section in sections[:10]:
                if section.text.strip():
                    content += section.text.strip() + "\n\n"
        else:
            # Handle regular article content
            content = ""
            for paragraph in soup.select('div.mw-parser-output > p'):
                content += paragraph.text.strip() + "\n\n"
        
        if not content.strip():
            return {
                'title': title,
                'content': "Could not extract article content. This might be a special Wikipedia page.",
                'url': url,
                'source': 'scrape',
                'summary': "No summary available."
            }
            
        # Generate a summary from the first few paragraphs
        summary = '\n'.join([p for p in content.split('\n\n') if p.strip()][:3])
            
        return {
            'title': title,
            'content': content.strip(),
            'summary': summary,
            'url': url,
            'source': 'scrape'
        }
    except Exception as e:
        st.error(f"Error fetching article: {str(e)}")
        return None

def analyze_text(text):
    """Analyze the text and return various metrics."""
    try:
        # Basic text analysis
        blob = TextBlob(text)
        sentences = sent_tokenize(text)
        words = word_tokenize(text)
        word_count = len(words)
        sentence_count = len(sentences)
        
        # Calculate average sentence length
        avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
        
        # Sentiment analysis
        sentiment = blob.sentiment
        
        # Count syllables (simplified)
        def count_syllables(word):
            word = word.lower()
            count = len(re.findall(r'[aeiouy]+', word))
            return max(1, count)
            
        # Count complex words (more than 2 syllables)
        complex_words = [word for word in words if count_syllables(word) > 2]
        complex_word_count = len(complex_words)
        
        return {
            'word_count': word_count,
            'sentence_count': sentence_count,
            'avg_sentence_length': round(avg_sentence_length, 2),
            'complex_word_count': complex_word_count,
            'complex_word_percentage': round((complex_word_count / word_count) * 100, 2) if word_count > 0 else 0,
            'polarity': round(sentiment.polarity, 2),
            'subjectivity': round(sentiment.subjectivity, 2),
            'reading_time': round(word_count / 200, 1)  # Average reading speed: 200 words per minute
        }
    except Exception as e:
        st.error(f"Error analyzing text: {str(e)}")
        return None

# Main app
def main():
    # Main container with max width
    st.markdown("<div class='main'>", unsafe_allow_html=True)
    
    # Create two columns for layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Analyze Wikipedia Content")
        st.markdown("Enter a Wikipedia URL below to analyze the article's content, extract key metrics, and gain valuable insights.")
    
    with col2:
        st.markdown("""
        <div style="background-color: #f0f9ff; padding: 1rem; border-radius: 8px; border-left: 4px solid #3b82f6;">
            <p style="margin: 0; font-size: 0.9rem; color: #0369a1;">
                <strong>Tip:</strong> Try analyzing articles like:<br>
                • <a href="#" onclick="document.querySelector('input[aria-label*=\'URL\']').value='https://en.wikipedia.org/wiki/Artificial_intelligence'; return false;">Artificial Intelligence</a><br>
                • <a href="#" onclick="document.querySelector('input[aria-label*=\'URL\']').value='https://en.wikipedia.org/wiki/Climate_change'; return false;">Climate Change</a><br>
                • <a href="#" onclick="document.querySelector('input[aria-label*=\'URL\']').value='https://en.wikipedia.org/wiki/Quantum_computing'; return false;">Quantum Computing</a>
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Add some spacing
    st.markdown("<div style='margin: 1.5rem 0;'></div>", unsafe_allow_html=True)
    
    # Input URL with improved styling
    with st.form("url_form"):
        col1, col2 = st.columns([4, 1])
        with col1:
            url = st.text_input(
                "Enter Wikipedia Article URL",
                placeholder="https://en.wikipedia.org/wiki/...",
                help="Paste a full Wikipedia article URL here"
            )
        with col2:
            st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
            submitted = st.form_submit_button("Analyze", use_container_width=True)
        
        if not url:
            st.markdown("<div style='margin: 1rem 0;'></div>", unsafe_allow_html=True)
            st.markdown(
                "<p style='color: #64748b; font-size: 0.9rem;'>Or try a sample article: "
                "<a href='#' onclick='window.location.href=\"?url=https://en.wikipedia.org/wiki/Artificial_intelligence\"; return false;'>Artificial Intelligence</a> • "
                "<a href='#' onclick='window.location.href=\"?url=https://en.wikipedia.org/wiki/Climate_change\"; return false;'>Climate Change</a> • "
                "<a href='#' onclick='window.location.href=\"?url=https://en.wikipedia.org/wiki/Quantum_computing\"; return false;'>Quantum Computing</a></p>",
                unsafe_allow_html=True
            )
    
    if submitted and url:
        if not url.startswith(('https://en.wikipedia.org/wiki/', 'http://en.wikipedia.org/wiki/')):
            st.warning("Please enter a valid Wikipedia URL starting with 'https://en.wikipedia.org/wiki/'")
        else:
            with st.spinner('Fetching and analyzing article...'):
                # Get article content
                article = get_article_content(url)
                
                if article and article['content']:
                    # Display article info and scraped content
                    st.subheader(article['title'])
                    st.caption(f"Source: {url}")
                    
                    # Show summary in a card
                    with st.container():
                        st.markdown("### 📝 Article Summary")
                        st.markdown(
                            f"<div class='card' style='background-color: #f8fafc; border-left: 4px solid #3b82f6; padding: 1.25rem; border-radius: 8px;'>"
                            f"<p style='margin: 0; line-height: 1.6; color: #1e293b;'>{article.get('summary', 'No summary available.')}</p>"
                            f"</div>", 
                            unsafe_allow_html=True
                        )
                    
                    # Analyze the content first
                    with st.spinner('Analyzing content...'):
                        analysis = analyze_text(article['content'])
                        
                        if not analysis:
                            st.error("Failed to analyze the article content.")
                            return
                    
                    # Full content in a tabbed interface
                    tab1, tab2 = st.tabs(["📄 Full Content", "📊 Advanced Analysis"])
                    
                    with tab1:
                        st.markdown("### Full Article Content")
                        if article.get('sections'):
                            st.markdown(
                                f"<div style='background: #f8fafc; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;'>"
                                f"<p style='margin: 0 0 0.5rem 0; font-weight: 500;'>📋 Article Sections:</p>"
                                f"<div style='display: flex; flex-wrap: wrap; gap: 0.5rem;'>"
                                f"{"".join([f'<span style="background: white; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.8rem; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">{section}</span>' for section in article['sections'][:10]])}"
                                f"</div>"
                                f"</div>",
                                unsafe_allow_html=True
                            )
                        
                        st.markdown(
                            f"<div style='background: white; padding: 1.5rem; border-radius: 8px; border: 1px solid #e2e8f0;'>"
                            f"{article['content'][:10000]}{'...' if len(article['content']) > 10000 else ''}"
                            f"</div>",
                            unsafe_allow_html=True
                        )
                        st.caption(f"Showing first 10,000 characters of {len(article['content']):,} total | Source: {article.get('source', 'web')}")
                    
                    with tab2:
                        st.markdown("### Advanced Text Analysis")
                        
                        # Sentiment Analysis
                        st.markdown("#### 🎭 Sentiment Analysis")
                        sentiment_score = analysis.get('polarity', 0)
                        sentiment_label = "Positive" if sentiment_score > 0.1 else "Neutral" if sentiment_score > -0.1 else "Negative"
                        
                        st.markdown(
                            f"<div style='background: white; padding: 1.5rem; border-radius: 8px; margin-bottom: 1.5rem; border: 1px solid #e2e8f0;'>"
                            f"<div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;'>"
                            f"<span style='font-weight: 500;'>Overall Sentiment:</span>"
                            f"<span style='font-weight: 600; color: {'#10b981' if sentiment_score > 0.1 else '#f59e0b' if sentiment_score > -0.1 else '#ef4444'};'>"
                            f"{sentiment_label} ({sentiment_score:.2f})"
                            f"</span>"
                            f"</div>"
                            f"<div style='height: 8px; background: #e2e8f0; border-radius: 4px; overflow: hidden; margin-bottom: 1rem;'>"
                            f"<div style='width: {(sentiment_score + 1) * 50}%; height: 100%; background: {'#10b981' if sentiment_score > 0.1 else '#f59e0b' if sentiment_score > -0.1 else '#ef4444'};'></div>"
                            f"</div>"
                            f"<div style='display: flex; justify-content: space-between; font-size: 0.8rem; color: #64748b;'>"
                            f"<span>Negative</span><span>Neutral</span><span>Positive</span>"
                            f"</div>"
                            f"</div>",
                            unsafe_allow_html=True
                        )
                        
                        # Readability Analysis
                        st.markdown("#### 📚 Readability")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown(
                                f"<div style='background: white; padding: 1.25rem; border-radius: 8px; border: 1px solid #e2e8f0; margin-bottom: 1rem;'>"
                                f"<div style='font-size: 0.9rem; color: #64748b; margin-bottom: 0.5rem;'>Flesch Reading Ease</div>"
                                f"<div style='font-size: 1.5rem; font-weight: 600; color: #1e40af;'>"
                                f"{analysis.get('flesch_reading_ease', 'N/A')}"
                                f"</div>"
                                f"<div style='font-size: 0.8rem; color: #64748b; margin-top: 0.25rem;'>"
                                f"{analysis.get('reading_ease_label', '')}"
                                f"</div>"
                                f"</div>",
                                unsafe_allow_html=True
                            )
                        
                        with col2:
                            st.markdown(
                                f"<div style='background: white; padding: 1.25rem; border-radius: 8px; border: 1px solid #e2e8f0; margin-bottom: 1rem;'>"
                                f"<div style='font-size: 0.9rem; color: #64748b; margin-bottom: 0.5rem;'>Flesch-Kincaid Grade</div>"
                                f"<div style='font-size: 1.5rem; font-weight: 600; color: #1e40af;'>"
                                f"{analysis.get('flesch_kincaid_grade', 'N/A')}"
                                f"</div>"
                                f"<div style='font-size: 0.8rem; color: #64748b; margin-top: 0.25rem;'>"
                                f"US school grade level"
                                f"</div>"
                                f"</div>",
                                unsafe_allow_html=True
                            )
                        
                        # Word Frequency Analysis
                        st.markdown("#### 📊 Word Frequency")
                        st.markdown(
                            "<div style='background: white; padding: 1.5rem; border-radius: 8px; border: 1px solid #e2e8f0;'>"
                            "<p style='margin: 0; color: #64748b;'>Word frequency analysis would be displayed here.</p>"
                            "</div>",
                            unsafe_allow_html=True
                        )
                    
                    # Analyze the content
                    with st.spinner('Analyzing content...'):
                        analysis = analyze_text(article['content'])
                        
                        if not analysis:
                            st.error("Failed to analyze the article content.")
                            return
                            
                        # Metrics in a grid layout
                        st.markdown("### 📊 Analysis Results")
                        
                        # Create a container for metrics
                        st.markdown("<div class='metric-container'>", unsafe_allow_html=True)
                        
                        # Row 1: Basic metrics
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.markdown(
                                f"<div class='metric-card'>"
                                f"<div class='metric-label'>Word Count</div>"
                                f"<div class='metric-value'>{analysis['word_count']:,}</div>"
                                f"</div>",
                                unsafe_allow_html=True
                            )
                            
                        with col2:
                            st.markdown(
                                f"<div class='metric-card'>"
                                f"<div class='metric-label'>Sentences</div>"
                                f"<div class='metric-value'>{analysis['sentence_count']:,}</div>"
                                f"</div>",
                                unsafe_allow_html=True
                            )
                            
                        with col3:
                            st.markdown(
                                f"<div class='metric-card'>"
                                f"<div class='metric-label'>Avg. Words/Sentence</div>"
                                f"<div class='metric-value'>{analysis['avg_sentence_length']:.1f}</div>"
                                f"</div>",
                                unsafe_allow_html=True
                            )
                            
                        with col4:
                            st.markdown(
                                f"<div class='metric-card'>"
                                f"<div class='metric-label'>Reading Time</div>"
                                f"<div class='metric-value'>{analysis['reading_time']} min</div>"
                                f"</div>",
                                unsafe_allow_html=True
                            )
                        
                        # Row 2: Complexity metrics
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.markdown(
                                f"<div class='metric-card'>"
                                f"<div class='metric-label'>Complex Words</div>"
                                f"<div class='metric-value'>{analysis['complex_word_count']}</div>"
                                f"</div>",
                                unsafe_allow_html=True
                            )
                            
                        with col2:
                            st.markdown(
                                f"<div class='metric-card'>"
                                f"<div class='metric-label'>Complexity %</div>"
                                f"<div class='metric-value'>{analysis['complex_word_percentage']:.1f}%</div>"
                                f"</div>",
                                unsafe_allow_html=True
                            )
                            
                        with col3:
                            sentiment = "😊 Positive" if analysis['polarity'] > 0.1 else "😐 Neutral" if analysis['polarity'] > -0.1 else "😟 Negative"
                            st.markdown(
                                f"<div class='metric-card'>"
                                f"<div class='metric-label'>Sentiment</div>"
                                f"<div class='metric-value'>{sentiment}</div>"
                                f"</div>",
                                unsafe_allow_html=True
                            )
                            
                        with col4:
                            subjectivity = "📊 Objective" if analysis['subjectivity'] < 0.5 else "💭 Subjective"
                            st.markdown(
                                f"<div class='metric-card'>"
                                f"<div class='metric-label'>Tone</div>"
                                f"<div class='metric-value'>{subjectivity}</div>"
                                f"</div>",
                                unsafe_allow_html=True
                            )
                        
                        st.markdown("</div>", unsafe_allow_html=True)  # Close metric-container
                        
                        # Display content preview
                        st.subheader("📝 Article Preview")
                        preview = " ".join(article['content'].split(" ")[:100]) + "..."
                        st.markdown(f"<div class='result-box'>{preview}</div>", unsafe_allow_html=True)
                        
                        # Show raw data
                        with st.expander("View Detailed Analysis"):
                            st.json(analysis)
                    
                    # Add download button for the analysis
                    st.download_button(
                        label="Download Analysis as JSON",
                        data=pd.DataFrame([analysis]).to_json(orient='records', lines=True),
                        file_name=f"{article['title'].replace(' ', '_')}_analysis.json",
                        mime="application/json"
                    )
                else:
                    st.error("Could not fetch or analyze the article. Please check the URL and try again.")
    
    # Add a nice footer and close main container
    st.markdown(
        "<div class='footer'>"
        "<p>© 2025 Wikipedia Web Scraping | "
        "<a href='#' style='color: #3b82f6; text-decoration: none;'>Privacy Policy</a> • "
        "<a href='#' style='color: #3b82f6; text-decoration: none;'>Terms of Service</a> • "
        "<a href='#' style='color: #3b82f6; text-decoration: none;'>GitHub</a></p>"
        "<p style='font-size: 0.8rem; color: #94a3b8;'>Data sourced from Wikipedia • Last updated: {}</p>"
        "</div>".format(pd.Timestamp.now().strftime('%B %d, %Y')),
        unsafe_allow_html=True
    )
    
    # Close main container
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Add custom JavaScript for better interactivity
    st.markdown(
        """
        <script>
        // Add smooth scrolling for anchor links
        document.addEventListener('DOMContentLoaded', function() {
            document.querySelectorAll('a[href^="#"]').forEach(anchor => {
                anchor.addEventListener('click', function (e) {
                    e.preventDefault();
                    const target = document.querySelector(this.getAttribute('href'));
                    if (target) {
                        target.scrollIntoView({
                            behavior: 'smooth'
                        });
                    }
                });
            });
            
            // Add loading state to buttons
            document.querySelectorAll('button').forEach(button => {
                if (button.textContent.trim() === 'Analyze') {
                    button.addEventListener('click', function() {
                        this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Analyzing...';
                        this.disabled = true;
                    });
                }
            });
            
            // Initialize tooltips
            const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            tooltipTriggerList.map(function (tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl);
            });
        });
        </script>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
