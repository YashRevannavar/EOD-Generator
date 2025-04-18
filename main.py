import logging
import sys
import os
from flask import Flask, render_template, request, Response, jsonify, send_from_directory
from flask_cors import CORS
import json
import traceback
import signal
from git_components.git_service import GitLogFetcher
# Remove old LLM connector import
from history_components.history_service import HistoryService # HistoryEntry is now in models
# Import models from central models.py
from models import HistoryEntry, DailySummary, SprintReviewSummary
from llm_components.llm_service import LlmService # Import new LlmService
from services.generation_service import GenerationService # Import new GenerationService
from typing import List # Import List for type hinting
import os

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Instantiate concrete services
git_service: GitLogFetcher = GitLogFetcher()
history_service: HistoryService = HistoryService()
llm_service: LlmService = LlmService() 

# Instantiate GenerationService with dependency injection
generation_service: GenerationService = GenerationService(
    git_service=git_service,
    llm_service=llm_service,
    history_service=history_service
)

def format_error(error):
    return {
        'error': str(error),
        'traceback': traceback.format_exc()
    }

# Remove helper functions format_daily_summary and format_sprint_review
# as this logic is now within GenerationService (or potentially a dedicated formatter)

@app.route('/')
def home():
    return app.send_static_file('index.html')

@app.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory('static/images', filename)

@app.route('/run-eod', methods=['POST'])
def run_eod():
    def generate():
        logging.info("Route /run-eod called.")
        yield "Starting EOD Generator...\n"
        try:
            # Delegate to GenerationService
            formatted_response, error_message = generation_service.generate_eod_report()

            if error_message:
                yield f"Error: {error_message}\n"
            else:
                yield "EOD report generated successfully.\n"
                yield "History updated.\n" # History is updated within the service
                yield f"RESPONSE_START\n{formatted_response}\nRESPONSE_END"

        except Exception as e:
            # Catch potential errors during service call setup or unexpected issues
            error_details = format_error(e)
            logging.error(f"Unexpected error in /run-eod route: {error_details}")
            yield f"Unexpected Error: {str(e)}\n"
            # Optionally add history entry here if service failed before adding its own

    return Response(generate(), mimetype='text/event-stream')

@app.route('/run-sprint-review', methods=['POST'])
def run_sprint_review():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    start_date = data.get('startDate')
    end_date = data.get('endDate')
    # Convert tickets list/dict to string if needed by LLM service, or adjust service
    tickets_data = data.get('tickets', [])
    tickets_str = json.dumps(tickets_data) # Assuming service expects stringified JSON

    if not all([start_date, end_date]):
        return jsonify({'error': 'Missing required date parameters'}), 400

    def generate():
        logging.info("Route /run-sprint-review called.")
        yield f"Starting Sprint Review generation for {start_date} to {end_date}...\n"
        try:
            # Delegate to GenerationService
            formatted_summary, error_message = generation_service.generate_sprint_review_report(
                start_date=start_date,
                end_date=end_date,
                tickets=tickets_str # Pass stringified tickets
            )

            if error_message:
                yield f"Error: {error_message}\n"
            else:
                yield "Sprint Review report generated successfully.\n"
                yield "History updated.\n" # History is updated within the service
                yield f"RESPONSE_START\n{formatted_summary}\nRESPONSE_END"

        except Exception as e:
            # Catch potential errors during service call setup or unexpected issues
            error_details = format_error(e)
            logging.error(f"Unexpected error in /run-sprint-review route: {error_details}")
            yield f"Unexpected Error: {str(e)}\n"
            # Optionally add history entry here if service failed before adding its own

    return Response(generate(), mimetype='text/event-stream')
    # Removed outer try-except as errors are handled within generate() or by Flask's handler

@app.errorhandler(Exception)
def handle_error(e):
    error_details = format_error(e)
    logging.error(f"Unhandled error: {error_details}")
    return jsonify({'error': str(e)}), 500

@app.route('/history', methods=['GET'])
def get_history():
    try:
        entries = history_service.get_all_entries()
        return jsonify([entry.to_dict() for entry in entries])
    except Exception as e:
        error_details = format_error(e)
        logging.error(f"Error retrieving history: {error_details}")
        return jsonify({'error': str(e)}), 500

@app.route('/history/<entry_id>', methods=['GET'])
def get_history_entry(entry_id):
    try:
        entry = history_service.get_entry_by_id(entry_id)
        if entry:
            return jsonify(entry.to_dict())
        return jsonify({'error': 'Entry not found'}), 404
    except Exception as e:
        error_details = format_error(e)
        logging.error(f"Error retrieving history entry: {error_details}")
        return jsonify({'error': str(e)}), 500

@app.route('/history/<entry_id>', methods=['DELETE'])
def delete_history_entry(entry_id):
    try:
        if history_service.delete_entry(entry_id):
            return jsonify({'status': 'success'})
        return jsonify({'error': 'Entry not found'}), 404
    except Exception as e:
        error_details = format_error(e)
        logging.error(f"Error deleting history entry: {error_details}")
        return jsonify({'error': str(e)}), 500

@app.route('/history/clear', methods=['POST'])
def clear_history():
    try:
        history_service.clear_history()
        return jsonify({'status': 'success'})
    except Exception as e:
        error_details = format_error(e)
        logging.error(f"Error clearing history: {error_details}")
        return jsonify({'error': str(e)}), 500

@app.route('/terminate', methods=['POST'])
def terminate():
    try:
        # Send SIGTERM to the current process
        logging.info("Terminating server...")
        pid = os.getpid()
        if sys.platform == 'win32':
            os.kill(pid, signal.CTRL_C_EVENT)
        else:
            os.kill(pid, signal.SIGTERM)
        return jsonify({'status': 'Server termination initiated'}), 200
    except Exception as e:
        error_details = format_error(e)
        logging.error(f"Error during termination: {error_details}")
        return jsonify({'error': str(e)}), 500

def signal_handler(signum, frame):
    logging.info(f"Received signal {signum}. Shutting down...")
    sys.exit(0)

if __name__ == "__main__":
    # Register signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    if sys.platform == 'win32':
        signal.signal(signal.CTRL_C_EVENT, signal_handler)
    else:
        signal.signal(signal.SIGINT, signal_handler)
    
    app.run(debug=True, port=5001)
