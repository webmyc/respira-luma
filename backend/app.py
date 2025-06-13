import os
import sys
from flask import Flask, jsonify
from flask_cors import CORS

# Import routes directly from local directory
from routes.facebook import facebook_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'asdf#FGSgvasgf$5$WGT')

# Enable CORS for all routes with proper configuration
CORS(app, resources={r"/*": {"origins": "*"}})

# Register blueprint with API prefix
app.register_blueprint(facebook_bp, url_prefix='/api')

@app.route('/')
def index():
    return jsonify({
        "status": "ok", 
        "message": "Respira Events Importer API is running",
        "version": "1.0.0"
    })

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy", 
        "service": "Respira Events Importer API"
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)


