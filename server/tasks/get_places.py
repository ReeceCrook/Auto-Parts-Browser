import os
import googlemaps
from celery import group, chain
from server.celery_app import celery
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

API_KEY = os.environ.get('GOOGLE_API_KEY')
gmaps = googlemaps.Client(key=API_KEY)


@celery.task(bind=True)
def fetch_place_details(self, place_id):
    try:
        details = gmaps.place(place_id=place_id, fields=['website'])
        website = details.get('result', {}).get('website')
        return {'place_id': place_id, 'website': website}
    except Exception as e:
        logger.error(f"Error fetching details for {place_id}: {e}")
        self.retry(countdown=2, max_retries=3, exc=e)


@celery.task(bind=True)
def merge_results(self, detail_results, text_search_results):
    if (isinstance(detail_results, list) and detail_results and isinstance(detail_results[0], str)):
        unwrapped = []
        for task_id in detail_results:
            async_res = celery.AsyncResult(task_id)
            unwrapped.append(async_res.result)
        detail_results = unwrapped

    merged = {}
    for result in text_search_results:
        place_id = result.get('place_id')
        detail = next((d for d in detail_results if d.get('place_id') == place_id), {})
        result['website'] = detail.get('website')
        merged[place_id] = result

    return {
        "all_ready": True,
        "results": merged,
    }


@celery.task(bind=True)
def combine_results(self, results_list):
    combined = {}
    for result in results_list:
        if result and isinstance(result, dict) and "results" in result:
            combined.update(result["results"])
        elif isinstance(result, dict):
            combined.update(result)
    return {
        "all_ready": True,
        "results": combined,
    }


@celery.task(bind=True)
def fetch_places_and_details(self, location, radius, queries):
    per_query_chains = []

    for query in queries:
        text_search = gmaps.places(query=query, location=location, radius=radius)
        results = text_search.get("results", [])
        if results:
            detail_tasks = [
                fetch_place_details.s(result['place_id'])
                for result in results if result.get('place_id')
            ]
            chain_sig = chain(
                group(detail_tasks),
                merge_results.s(text_search_results=results)
            )
            per_query_chains.append(chain_sig)

    if not per_query_chains:
        return None

    if len(per_query_chains) == 1:
        final_result = per_query_chains[0].apply_async()
        return final_result.id
    else:
        group_sig = group(per_query_chains)
        final_chain = chain(group_sig, combine_results.s())
        result = final_chain.apply_async()
        return result.id
