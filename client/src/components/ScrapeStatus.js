import '../css/App.css'
import React, { useEffect, useState } from 'react';

function ScrapeStatus({ groupId, taskIds }) {
  const [status, setStatus] = useState(null);

  useEffect(() => {
    const params = new URLSearchParams();
    params.append('group_id', groupId);
    taskIds.forEach(id => params.append('task_id', id));
    
    const eventSource = new EventSource(`/scrape/stream?${params.toString()}`);
    
    eventSource.onmessage = event => {
      const data = JSON.parse(event.data);
      setStatus(data);
      if (data.all_ready) {
        eventSource.close();
      }
    };
    
    eventSource.onerror = err => {
      console.error('EventSource failed:', err);
      eventSource.close();
    };

    return () => {
      eventSource.close();
    };
  }, [groupId, taskIds]);


  let tasksData = [];
  if (status && status.all_ready) {
    tasksData = Object.entries(status.results).map(([taskId, taskData]) => {
      console.log(taskData)
      const results = taskData.result.map((item, index) => ({
        id: `${taskId}-${index}`,
        prices: item.prices
      }));
      return { taskId, results };
    });
  }


  console.log(tasksData)

  return (
    <div>
      {status ? (
        status.all_ready ? (
          <div>
            <h2>Results:</h2>
            {tasksData.map(({ taskId, results }) => (
              <div key={taskId}>
                <h3>Task ID: {taskId}</h3>
                {results.map(result => (
                  <div key={result.id}>
                    {result.prices.map((priceHtml, idx) => (
                      <div key={idx} dangerouslySetInnerHTML={{ __html: priceHtml }} />
                    ))}
                  </div>
                ))}
              </div>
            ))}
          </div>
        ) : (
          <div>Tasks are still running...</div>
        )
      ) : (
        <div>Waiting for updates...</div>
      )}
    </div>
  );
}

export default ScrapeStatus;
