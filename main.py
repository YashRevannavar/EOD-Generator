import logging
import sys
import os
from flask import Flask, render_template, request, Response, jsonify, send_from_directory
from flask_cors import CORS
import json
import traceback
import signal
from git_components.git_service import GitLogFetcher
from llm_components.llm_connector import llm_eod_summary_generator, llm_sprint_review_summary_generator
import os

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

git_log_fetcher: GitLogFetcher = GitLogFetcher()

def format_error(error):
    return {
        'error': str(error),
        'traceback': traceback.format_exc()
    }

@app.route('/')
def home():
    return app.send_static_file('index.html')

@app.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory('static/images', filename)

@app.route('/run-eod', methods=['POST'])
def run_eod():
    def generate():
        try:
            logging.info("Starting EOD Generator")
            yield "Starting EOD Generator...\n"
            
            eod_logs = git_log_fetcher.get_git_logs(days=1)
            yield "Git logs retrieved successfully\n"
            
            responses = llm_eod_summary_generator(collected_commits=eod_logs)
            logging.info(f"Generated response length: {len(responses)}")
            logging.info(f"Response preview: {responses[:100]}...")
            
            formatted_response = responses.strip().replace('\r\n', '\n').replace('\r', '\n')
            yield "Summary generated successfully\n"
            
            yield f"RESPONSE_START\n{formatted_response}\nRESPONSE_END"
            
        except Exception as e:
            error_details = format_error(e)
            logging.error(f"Error in run_eod: {error_details}")
            yield f"Error: {str(e)}\n"
    
    return Response(generate(), mimetype='text/event-stream')

@app.route('/run-sprint-review', methods=['POST'])
def run_sprint_review():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        start_date = data.get('startDate')
        end_date = data.get('endDate')
        tickets = data.get('tickets', [])

        if not all([start_date, end_date]):
            return jsonify({'error': 'Missing required date parameters'}), 400

        def generate():
            try:
                yield f"Fetching Git logs from {start_date} to {end_date}...\n"
                
                sprint_review_logs = git_log_fetcher.get_git_logs_by_date_range(start_date, end_date)
                yield "Git logs retrieved successfully\n"
                
                summary = llm_sprint_review_summary_generator(
                    collected_commits=sprint_review_logs, 
                    tickets=tickets
                )
                logging.info(f"Generated sprint review length: {len(summary)}")
                logging.info(f"Sprint review preview: {summary[:100]}...")
                
                formatted_summary = summary.strip().replace('\r\n', '\n').replace('\r', '\n')
                yield "Summary generated successfully\n"
                
                yield f"RESPONSE_START\n{formatted_summary}\nRESPONSE_END"
                
            except Exception as e:
                error_details = format_error(e)
                logging.error(f"Error in run_sprint_review: {error_details}")
                yield f"Error: {str(e)}\n"
        
        return Response(generate(), mimetype='text/event-stream')
    except Exception as e:
        error_details = format_error(e)
        logging.error(f"Error processing sprint review request: {error_details}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(Exception)
def handle_error(e):
    error_details = format_error(e)
    logging.error(f"Unhandled error: {error_details}")
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
