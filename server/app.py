import time
import json
from flask import Flask, request, session, Response, jsonify
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api

from .config import Config


db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
api = Api()

def create_app():

    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    bcrypt.init_app(app)
    api.init_app(app)
    CORS(app)

    @app.route('/scrape/<search>', methods=['GET'])
    def scrape(search):
        from .Helpers.parallel_scrape_helper import run_parallel_scrapes
        group_result = run_parallel_scrapes(search)
        response = {
            "group_task_id": group_result['group_id'],
            "individal_task_ids": group_result['task_ids'],
            "Search": search if search else None
        }
        return jsonify(response), 202



    @app.route('/scrape/status', methods=['POST'])
    def scrape_status():
        from .celery_app import celery
        data = request.get_json()
        group_id = data.get('group_id')
        task_ids = data.get('task_ids', [])
        
        states = {}
        results = {}
        for task_id in task_ids:
            async_results = celery.AsyncResult(task_id)
            state = async_results.state
            states[task_id] = state
            if state == "SUCCESS":
                results[task_id] = async_results.result


        all_ready = all(state == "SUCCESS" for state in states.values())
        
        response = {
            "group_id": group_id,
            "states": states,
            "all_ready": all_ready,
            "results": results if all_ready else None
        }
        return jsonify(response), 200

    @app.route('/scrape/stream', methods=['GET'])
    def stream():
        # Get group_id and task_ids from query parameters
        group_id = request.args.get('group_id')
        # For multiple task_ids, you can pass them as repeated query parameters (e.g., ?task_id=1&task_id=2)
        task_ids = request.args.getlist('task_id')
        from .celery_app import celery

        def event_stream():
            while True:
                states = {}
                results = {}
                for task_id in task_ids:
                    async_results = celery.AsyncResult(task_id)
                    state = async_results.state
                    states[task_id] = state
                    if state == "SUCCESS":
                        results[task_id] = async_results.result

                # Build the message
                if all(state == "SUCCESS" for state in states.values()):
                    message = {
                        "group_id": group_id,
                        "states": states,
                        "results": results,
                        "all_ready": True
                    }
                    # Yield the final message and then break the loop
                    yield f"data: {json.dumps(message)}\n\n"
                    break
                else:
                    message = {
                        "group_id": group_id,
                        "states": states,
                        "all_ready": False
                    }
                    yield f"data: {json.dumps(message)}\n\n"
                # Pause briefly before the next status check
                time.sleep(1)

        # Return a streaming response with the appropriate MIME type
        return Response(event_stream(), mimetype="text/event-stream")

    return app



if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)