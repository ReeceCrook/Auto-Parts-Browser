import React, { useEffect } from 'react';
import parse from 'html-react-parser';
import he from 'he';

function ScrapeResultsStatus({ taskIds, setStatus, status }) {
  useEffect(() => {
    if (!taskIds || taskIds.length === 0) return;

    const params = new URLSearchParams();
    taskIds.forEach(id => params.append('task_id', id));

    const eventSource = new EventSource(`/scrape/stream?${params.toString()}`);

    eventSource.onmessage = event => {
      const data = JSON.parse(event.data);
      setStatus(data);
      if (data.all_ready === true) {
        console.log("closing sse", data.all_ready)
        eventSource.close();
      }
    };

    eventSource.onerror = err => {
        if (eventSource.readyState === EventSource.CLOSED) {
          console.log("EventSource connection closed as expected.");
        } else {
          console.error('EventSource error:', err);
        }
      };
      

    return () => {
      eventSource.close();
    };
  }, [taskIds, setStatus]);

  function renderResults() {
    if (!status.results) return null;
    return Object.entries(status.results).map(([taskId, resultsArray]) => (
      <div key={taskId} style={{ marginBottom: '2rem' }}>
        <h3>Task: {taskId}</h3>
        {resultsArray.map((result, index) => (
          <div
            key={index}
            style={{
              border: '1px solid #ccc',
              padding: '1rem',
              marginBottom: '1rem'
            }}
          >
            <p>
              <strong>URL:</strong> {result.url}
            </p>
            <p>
              <strong>Title:</strong> {result.title}
            </p>
            {result.store && (
              <p>
                <strong>Store:</strong>{' '}
                {Array.isArray(result.store)
                  ? result.store.join(', ')
                  : result.store}
              </p>
            )}
            <p>
              <strong>Total Results:</strong> {result.total_prices}
            </p>
            <p>
              <strong>Time Taken:</strong> {result.time_taken}
            </p>
            <div>
              <strong>Results:</strong>
              {result.prices.map((priceHtml, i) => (
                <div key={i} className="price-item">
                  {parse(he.decode(priceHtml))}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    ));
  };

  return (
    <div>
      {status ? (
        status.all_ready ? (
          <div>
            <h2>Scrape Final Results:</h2>
            {renderResults()}
          </div>
        ) : (
          <div>
            <h2>Scrape Task Updating:</h2>
            <pre>{JSON.stringify(status, null, 2)}</pre>
          </div>
        )
      ) : (
        <div>Waiting for scrape updates...</div>
      )}
    </div>
  );
}

export default ScrapeResultsStatus;
