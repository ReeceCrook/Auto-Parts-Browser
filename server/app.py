import time
import json
from flask import Flask, request, session, Response, jsonify, stream_with_context
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

    @app.route('/scrape/status', methods=['POST'])
    def scrape_status():
        from .celery_app import celery
        data = request.get_json()
        group_id = data.get('group_id')
        task_ids = data.get('task_ids', [])
        
        if isinstance(task_ids, str):
            task_ids = [task_ids]
        
        states = {}
        results = {}
        for task_id in task_ids:
            async_result = celery.AsyncResult(task_id)
            state = async_result.state
            states[task_id] = state
            if state == "SUCCESS":
                results[task_id] = async_result.result

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
        if isinstance(task_ids, str):
            task_ids = [task_ids]
        if len(task_ids) == 1 and ',' in task_ids[0]:
            task_ids = task_ids[0].split(',')
        from .celery_app import celery

        def flatten_results(results):
            flat = {}
            for key, value in results.items():
                if isinstance(value, dict) and 'results' in value and isinstance(value['results'], dict):
                    flat.update(value['results'])
                else:
                    flat[key] = value
            return flat

        def event_stream():
            while True:
                states = {}
                results = {}
                all_nested_ready = True

                for task_id in task_ids:
                    async_result = celery.AsyncResult(task_id)
                    state = async_result.state
                    states[task_id] = state

                    if state == "SUCCESS":
                        res = async_result.result

                        if isinstance(res, list) and res:
                            if isinstance(res[0], str):
                                nested_ready = True
                                nested_results = {}
                                for nested_id in res:
                                    nested_async = celery.AsyncResult(nested_id)
                                    if nested_async.state != "SUCCESS":
                                        nested_ready = False
                                    else:
                                        nested_results[nested_id] = nested_async.result
                                if nested_ready:
                                    results[task_id] = nested_results
                                else:
                                    results[task_id] = res
                                    all_nested_ready = False
                            else:
                                results[task_id] = res
                        elif isinstance(res, str):
                            nested_async = celery.AsyncResult(res)
                            if nested_async.state == "SUCCESS":
                                results[task_id] = nested_async.result
                            else:
                                results[task_id] = res
                                all_nested_ready = False
                        else:
                            results[task_id] = res


                all_ready = all(state == "SUCCESS" for state in states.values()) and all_nested_ready

                if all_ready:
                    flat_results = flatten_results(results)
                    message = {
                        "group_id": group_id,
                        "states": states,
                        "results": flat_results,
                        "all_ready": True
                    }
                    yield f"data: {json.dumps(message)}\n\n"
                    break
                time.sleep(1)

        
        return Response(
            stream_with_context(event_stream()),
            mimetype="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no"
            }
        )


    @app.route('/places', methods=['POST'])
    def fetch_places():
        data = request.get_json()
        location_data = data.get("location", {})
        lat = location_data.get("lat")
        lng = location_data.get("lng")
        radius = data.get("radius")
        if lat is None or lng is None:
            return jsonify({"error": "Invalid location data"}), 400
        location_tuple = (lat, lng)
        queries = ["O'Reilly Auto Parts", "Advance Auto Parts"]
        
        from .tasks.get_places import fetch_places_and_details
        task = fetch_places_and_details.delay(location_tuple, radius, queries)
        print(task.id)
        return jsonify({ "group_task_id": None, "task_id": [task.id]}), 202


    @app.route('/scrape/selected', methods=['POST'])
    def scrape_selected():
        data = request.get_json()
        search = data.get("search")
        oreilly_locations = data.get("oreilly", [])
        advance_locations = data.get("advance", [])

        from .tasks.oreilly_scraper import scrape_oreilly
        from .tasks.advance_scraper import scrape_advance

        oreilly_task_ids = []
        advance_task_ids = []

        for loc in oreilly_locations:
            url = loc.get("website")
            if url:
                task = scrape_oreilly.delay(search, url)
                oreilly_task_ids.append(task.id)
        
        for loc in advance_locations:
            url = loc.get("website")
            if url:
                task = scrape_advance.delay(search, url)
                advance_task_ids.append(task.id)
        
        payload = {
            "oreilly": oreilly_task_ids,
            "advance": advance_task_ids,
            "search": search,
        }
        return jsonify(payload), 202


    return app






if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)