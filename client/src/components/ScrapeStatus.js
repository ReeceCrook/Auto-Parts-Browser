import React, { useEffect, useState } from 'react';

function ScrapeStatus({ taskId }) {
  console.log("taskID ==>", taskId, "<== taskID")

  const [status, setStatus] = useState(null);

  useEffect(() => {
    const params = new URLSearchParams();
    params.append('task_id', taskId);

    const eventSource = new EventSource(`/scrape/stream?${params.toString()}`);

    eventSource.onmessage = event => {
      const data = JSON.parse(event.data);
      setStatus(data);
      if (data.all_ready) {
        eventSource.close();
      }
    };

    eventSource.onerror = err => {
      console.error('EventSource error:', err);
      eventSource.close();
    };

    return () => {
      eventSource.close();
    };
  }, [taskId]);

  console.log("status ==>", status, "<== status")

  return (
    <div>
      {status ? (
        status.all_ready ? (
          <div>
            <h2>Final Results:</h2>
            <pre>{JSON.stringify(status.results, null, 2)}</pre>
          </div>
        ) : (
          <div>
            <h2>Updating Task Status:</h2>
            <pre>{JSON.stringify(status, null, 2)}</pre>
          </div>
        )
      ) : (
        <div>Waiting for updates...</div>
      )}
    </div>
  );
}

export default ScrapeStatus;
