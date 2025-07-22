from app import create_app, db
from flask import jsonify

app = create_app()

@app.route('/')
def index():
    return jsonify({
        'message': 'EmailDrafter API',
        'version': '1.0.0',
        'status': 'running'
    })

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'database': 'connected' if db.engine else 'disconnected'
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)