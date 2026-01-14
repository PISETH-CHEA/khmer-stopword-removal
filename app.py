from flask import Flask, request, render_template, jsonify, session
from scripts.demo_stopword_removal import KhmerStopwordRemover
from src.preprocessing.unicode_normalizer import normalize_text
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import json

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['SECRET_KEY'] = os.urandom(24)

# Database configuration
DB_CONFIG = {
    'dbname': 'khmer_nlp_db',
    'user': 'postgres',
    'password': '2510',  # Change this
    'host': 'localhost',
    'port': '5432'
}

remover = KhmerStopwordRemover()

# Language dictionary - Fixed to avoid Python method names
LANGUAGES = {
    'km': {
        'app_name': 'ប្រព័ន្ធលុបពាក្យគន្លឹះភាសាខ្មែរ',
        'home': 'ទំព័រដើម',
        'history': 'ប្រវត្តិ',
        'language': 'ភាសា',
        'analysis': 'ការវិភាគ',
        'input_text': 'បញ្ចូលអត្ថបទខ្មែរ',
        'original_text': 'អត្ថបទដើម',
        'text_placeholder': 'សូមបញ្ចូលអត្ថបទភាសាខ្មែររបស់អ្នកនៅទីនេះ...',
        'analyze_btn': 'វិភាគអត្ថបទ',
        'clear_btn': 'ជម្រះ',
        'loading': 'កំពុងវិភាគ...',
        'total_words': 'ពាក្យសរុប',
        'filtered_words': 'ពាក្យបន្ទាប់ពីច្រោះ',
        'removed_words': 'ពាក្យដែលលុប',
        'reduction': 'ការថយចុះ',
        'filtered_tokens': 'ពាក្យដែលបានច្រោះ',
        'removed_tokens': 'ពាក្យដែលលុប',
        'word_frequency': 'ប្រេកង់ពាក្យ',
        'statistics': 'ការវិភាគ',
        'linguistic_features': 'លក្ខណៈភាសា',
        'segmented_text': 'អត្ថបទដែលបានចែកផ្នែក',
        'total_tokens': 'ពាក្យសរុប',
        'unique_tokens': 'ពាក្យតែមួយគត់',
        'duplicate_words': 'ពាក្យស្ទួន',
        'export_results': 'នាំចេញលទ្ធផល',
        'chars': 'អក្សរ',
        'words': 'ពាក្យ',
        'date': 'កាលបរិច្ឆេទ',
        'no_history': 'មិនមានប្រវត្តិការវិភាគ',
        'analyze_new_text': 'វិភាគអត្ថបទថ្មី',
        'analysis_details': 'ការវិភាគលម្អិត',
        'original_text_label': 'អត្ថបទដើម:',
        'stopwords_removed': 'ពាក្យគន្លឹះលុប',
        'percentage': 'ការថយចុះ',
        'time': 'កាលបរិច្ឆេទ',
        'khmer': 'ភាសាខ្មែរ',
        'english': 'ភាសាអង់គ្លេស',
        'switch_language': 'ប្តូរភាសា',
        'footer_text': 'ប្រព័ន្ធវិភាគភាសាធម្មជាតិខ្មែរ',
        'copyright': '© 2026 កម្មវិធីវិភាគអត្ថបទខ្មែរ',
        'contact': 'ទំនាក់ទំនង: info@AMS.edu.kh',
        'saved_to_db': 'លទ្ធផលត្រូវបានរក្សាទុកក្នុងមូលដ្ឋានទិន្នន័យ',
        'copy_token': 'បានចម្លងពាក្យទៅក្ដារតម្បៀតខ្ទាស់',
        'exported': 'បាននាំចេញជាទ្រង់ទ្រាយ',
        'enter_text': 'សូមបញ្ចូលអត្ថបទមុនពេលវិភាគ',
        'no_data': 'មិនមានទិន្នន័យសម្រាប់នាំចេញ',
        'word': 'ពាក្យ',
        'frequency': 'ប្រេកង់',
        'stars': 'ផ្កាយ'
    },
    'en': {
        'app_name': 'Khmer Stop-Word Removal System',
        'home': 'Home',
        'history': 'History',
        'language': 'Language',
        'analysis': 'Analysis',
        'input_text': 'Input Khmer Text',
        'original_text': 'Original Text',
        'text_placeholder': 'Please enter your Khmer text here...',
        'analyze_btn': 'Analyze Text',
        'clear_btn': 'Clear',
        'loading': 'Analyzing...',
        'total_words': 'Total Words',
        'filtered_words': 'Filtered Words',
        'removed_words': 'Words Removed',
        'reduction': 'Reduction',
        'filtered_tokens': 'Filtered Tokens',
        'removed_tokens': 'Removed Tokens',
        'word_frequency': 'Word Frequency',
        'statistics': 'Statistics',
        'linguistic_features': 'Linguistic Features',
        'segmented_text': 'Segmented Text',
        'total_tokens': 'Total Tokens',
        'unique_tokens': 'Unique Tokens',
        'duplicate_words': 'Duplicate Words',
        'export_results': 'Export Results',
        'chars': 'Characters',
        'words': 'Words',
        'date': 'Date',
        'no_history': 'No Analysis History',
        'analyze_new_text': 'Analyze New Text',
        'analysis_details': 'Analysis Details',
        'original_text_label': 'Original Text:',
        'stopwords_removed': 'Stopwords Removed',
        'percentage': 'Reduction',
        'time': 'Timestamp',
        'khmer': 'Khmer',
        'english': 'English',
        'switch_language': 'Switch Language',
        'footer_text': 'Khmer Natural Language Processing System',
        'copyright': '© 2026 Khmer Text Analysis Program',
        'contact': 'Contact: info@AMS.edu.kh',
        'saved_to_db': 'Results saved to database',
        'copy_token': 'Copied word to clipboard',
        'exported': 'Exported as format',
        'enter_text': 'Please enter text before analyzing',
        'no_data': 'No data available for export',
        'word': 'Word',
        'frequency': 'Frequency',
        'stars': 'Stars'
    }
}

def get_db_connection():
    """Create a database connection"""
    conn = psycopg2.connect(**DB_CONFIG)
    return conn

def create_tables():
    """Create necessary tables if they don't exist"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS text_analysis (
            id SERIAL PRIMARY KEY,
            original_text TEXT NOT NULL,
            filtered_tokens JSONB,
            removed_tokens JSONB,
            frequency_stats JSONB,
            linguistic_stats JSONB,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            text_length INTEGER,
            stopwords_removed INTEGER,
            reduction_percentage FLOAT
        )
    ''')
    
    conn.commit()
    cur.close()
    conn.close()

def get_language():
    """Get current language from session, default to Khmer"""
    return session.get('language', 'km')

@app.route('/', methods=['GET', 'POST'])
def home():
    # Set default language if not set
    if 'language' not in session:
        session['language'] = 'km'
    
    lang = get_language()
    result = {}
    
    if request.method == 'POST':
        text = request.form.get('text', '')
        
        if not text.strip():
            return render_template('index.html', 
                                 result=None, 
                                 error=LANGUAGES[lang]['enter_text'],
                                 lang=LANGUAGES[lang],
                                 current_lang=lang)
        
        # Process text
        original_tokens = remover.segmenter.segment(normalize_text(text))
        filtered_tokens = remover.remove_stopwords(text)
        removed_tokens = [t for t in original_tokens if t not in filtered_tokens]
        frequency_tokens = remover.Frequency(filtered_tokens)
        linguistic_ = remover.linguistic_features(filtered_tokens)
        segmented_ = remover.segmented_text(text)
        
        # Calculate statistics
        removed_count = len(removed_tokens)
        reduction_percentage = (removed_count / len(original_tokens) * 100) if original_tokens else 0
        
        # Prepare result
        result = {
            'original_text': text,
            'filtered_text': filtered_tokens,
            'removed_text': removed_tokens,
            'frequency_tokens': frequency_tokens,
            'linguistic_': linguistic_,
            'segmented_': segmented_,
            'stats': {
                'original_tokens': len(original_tokens),
                'filtered_tokens': len(filtered_tokens),
                'removed_tokens': removed_count,
                'reduction_percentage': round(reduction_percentage, 2)
            }
        }
        
        # Save to database
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            cur.execute('''
                INSERT INTO text_analysis 
                (original_text, filtered_tokens, removed_tokens, frequency_stats, 
                 linguistic_stats, text_length, stopwords_removed, reduction_percentage)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                text,
                json.dumps(filtered_tokens, ensure_ascii=False),
                json.dumps(removed_tokens, ensure_ascii=False),
                json.dumps(frequency_tokens, ensure_ascii=False),
                json.dumps(linguistic_, ensure_ascii=False),
                len(text),
                removed_count,
                reduction_percentage
            ))
            
            conn.commit()
            cur.close()
            conn.close()
            
            result['saved_to_db'] = True
        except Exception as e:
            result['saved_to_db'] = False
            result['db_error'] = str(e)
    
    return render_template('index.html', 
                         result=result, 
                         lang=LANGUAGES[lang],
                         current_lang=lang)

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """API endpoint for AJAX requests"""
    data = request.get_json()
    text = data.get('text', '')
    
    if not text.strip():
        return jsonify({'error': 'Text is required'}), 400
    
    # Process text
    original_tokens = remover.segmenter.segment(normalize_text(text))
    filtered_tokens = remover.remove_stopwords(text)
    removed_tokens = [t for t in original_tokens if t not in filtered_tokens]
    frequency_tokens = remover.Frequency(filtered_tokens)
    linguistic_ = remover.linguistic_features(filtered_tokens)
    segmented_ = remover.segmented_text(text)
    
    return jsonify({
        'filtered_tokens': filtered_tokens,
        'removed_tokens': removed_tokens,
        'frequency_tokens': frequency_tokens,
        'linguistic_features': linguistic_,
        'segmented_text': segmented_,
        'stats': {
            'original_tokens': len(original_tokens),
            'filtered_tokens': len(filtered_tokens),
            'removed_tokens': len(removed_tokens)
        }
    })

@app.route('/history', methods=['GET'])
def get_history():
    """Get analysis history"""
    lang = get_language()
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute('''
        SELECT id, original_text, timestamp, text_length, 
               stopwords_removed, reduction_percentage
        FROM text_analysis 
        ORDER BY timestamp DESC 
        LIMIT 10
    ''')
    
    history = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template('history.html', 
                         history=history,
                         lang=LANGUAGES[lang],
                         current_lang=lang)

@app.route('/history/<int:id>', methods=['GET'])
def get_analysis_details(id):
    """Get detailed analysis by ID"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute('''
        SELECT * FROM text_analysis WHERE id = %s
    ''', (id,))
    
    analysis = cur.fetchone()
    
    cur.close()
    conn.close()
    
    if analysis:
        return jsonify(dict(analysis))
    return jsonify({'error': 'Analysis not found'}), 404

@app.route('/set_language/<lang>', methods=['POST'])
def set_language(lang):
    """Set language preference"""
    if lang in LANGUAGES:
        session['language'] = lang
        return jsonify({'success': True, 'language': lang})
    return jsonify({'success': False, 'error': 'Invalid language'}), 400

@app.route('/get_language', methods=['GET'])
def get_current_language():
    """Get current language"""
    lang = get_language()
    return jsonify({'language': lang, 'strings': LANGUAGES[lang]})

if __name__ == '__main__':
    create_tables()  # Create tables on startup
    app.run(debug=True)