"""
app.py
Flask application template for the warm-up assignment

Students need to implement the API endpoints as specified in the assignment.
"""

from flask import Flask, request, jsonify, render_template
from starter_preprocess import TextPreprocessor
import traceback

app = Flask(__name__)
preprocessor = TextPreprocessor()


@app.route('/')
def home():
    """Render a simple HTML form for URL input"""
    return render_template('index.html')


@app.route('/health')
def health_check():
    """Simple health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "Text preprocessing service is running"
    })


@app.route('/api/clean', methods=['POST'])
def clean_text():
    """
    API endpoint that accepts a URL and returns cleaned text

    Expected JSON input:
    {"url": "https://www.gutenberg.org/files/1342/1342-0.txt"}

    Returns JSON:
    {
        "success": true/false,
        "cleaned_text": "...",
        "statistics": {...},
        "summary": "...",
        "error": "..." (if applicable)
    }
    """
    try:
        data = request.get_json()

        # Validate that JSON body and url field exist
        if not data or 'url' not in data:
            return jsonify({
                "success": False,
                "error": "Missing 'url' field in request body"
            }), 400

        url = data['url'].strip()

        # Fetch raw text from the URL
        raw_text = preprocessor.fetch_from_url(url)

        # Clean Gutenberg headers/footers
        cleaned = preprocessor.clean_gutenberg_text(raw_text)

        # Normalize the cleaned text
        normalized = preprocessor.normalize_text(cleaned)

        # Get statistics and summary
        statistics = preprocessor.get_text_statistics(normalized)
        summary = preprocessor.create_summary(normalized, num_sentences=3)

        return jsonify({
            "success": True,
            "cleaned_text": normalized,
            "statistics": statistics,
            "summary": summary
        })

    except ValueError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to process URL: {str(e)}"
        }), 500


@app.route('/api/analyze', methods=['POST'])
def analyze_text():
    """
    API endpoint that accepts raw text and returns statistics only

    Expected JSON input:
    {"text": "Your raw text here..."}

    Returns JSON:
    {
        "success": true/false,
        "statistics": {...},
        "error": "..." (if applicable)
    }
    """
    try:
        data = request.get_json()

        # Validate that JSON body and text field exist
        if not data or 'text' not in data:
            return jsonify({
                "success": False,
                "error": "Missing 'text' field in request body"
            }), 400

        text = data['text'].strip()

        if not text:
            return jsonify({
                "success": False,
                "error": "Text field cannot be empty"
            }), 400

        # Normalize and get statistics
        normalized = preprocessor.normalize_text(text)
        statistics = preprocessor.get_text_statistics(normalized)

        return jsonify({
            "success": True,
            "statistics": statistics
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to analyze text: {str(e)}"
        }), 500


if __name__ == '__main__':
    print("🚀 Starting Text Preprocessing Web Service...")
    print("📖 Available endpoints:")
    print("   GET  /           - Web interface")
    print("   GET  /health     - Health check")
    print("   POST /api/clean  - Clean text from URL")
    print("   POST /api/analyze - Analyze raw text")
    print()
    print("🌐 Open your browser to: http://localhost:5000")
    print("⏹️  Press Ctrl+C to stop the server")

    app.run(debug=True, port=5000, host='0.0.0.0')
