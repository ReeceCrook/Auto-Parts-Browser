from celery import group
from ..tasks import scrape_oreilly, scrape_advance

def run_parallel_scrapes(search):
    job = group(
        scrape_oreilly.s(search),
        scrape_advance.s(search)
    )
    group_result = job.apply_async()
    
    return {
        "group_id": group_result.id,
        "task_ids": [result.id for result in group_result.results]
    }
