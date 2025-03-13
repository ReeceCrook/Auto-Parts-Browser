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
            "task_id": group_result['task_ids'],
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
        group_id = request.args.get('group_id')
        task_ids = request.args.getlist('task_id')
        if len(task_ids) == 1 and ',' in task_ids[0]:
            task_ids = task_ids[0].split(',')
        from .celery_app import celery

        def event_stream():
            while True:
                states = {}
                results = {}

                for task_id in task_ids:
                    async_result = celery.AsyncResult(task_id)
                    state = async_result.state
                    states[task_id] = state

                    if state == "SUCCESS":
                        res = async_result.result

                        if isinstance(res, list) and res:
                            # Check if the list items are dictionaries, indicating final results, not nested task IDs.
                            if all(isinstance(item, dict) for item in res):
                                results[task_id] = res  # Directly assign the result list.
                            else:
                                # Otherwise assume it’s a list of nested task IDs.
                                nested_states = {}
                                nested_results = {}
                                for nested_id in res:
                                    nested_async = celery.AsyncResult(nested_id)
                                    nested_state = nested_async.state
                                    nested_states[nested_id] = nested_state
                                    if nested_state == "SUCCESS":
                                        nested_results[nested_id] = nested_async.result
                                if all(s == "SUCCESS" for s in nested_states.values()):
                                    results[task_id] = nested_results
                                else:
                                    results[task_id] = res


                all_ready = all(state == "SUCCESS" for state in states.values())
                if all_ready:
                    message = {
                        "group_id": group_id,
                        "states": states,
                        "results": results,
                        "all_ready": True
                    }
                    yield f"data: {json.dumps(message)}\n\n"
                    break
                else:
                    message = {
                        "group_id": group_id,
                        "states": states,
                        "all_ready": False
                    }
                    yield f"data: {json.dumps(message)}\n\n"
                time.sleep(1)

        return Response(event_stream(), mimetype="text/event-stream")


    @app.route('/places', methods=['POST'])
    def fetch_places():
        data = request.get_json()
        location_data = data.get("location", {})
        lat = location_data.get("lat")
        lng = location_data.get("lng")
        if lat is None or lng is None:
            return jsonify({"error": "Invalid location data"}), 400
        location_tuple = (lat, lng)
        radius = data.get("radius")
        queries = ["O'Reilly Auto Parts", "Advance Auto Parts"]
        
        from .tasks.get_places import fetch_places_and_details
        task = fetch_places_and_details.delay(location_tuple, radius, queries)
        return jsonify({"task_id": task.id}), 202


    return app



if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)