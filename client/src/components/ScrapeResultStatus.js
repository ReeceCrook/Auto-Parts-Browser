import { useEffect } from 'react';
import '../css/ScrapeResultsStatus.css';

function ScrapeResultsStatus({ taskIds, setStatus, status }) {
  useEffect(() => {
    if (!taskIds?.length) return;
    const params = new URLSearchParams();
    taskIds.forEach(id => params.append('task_id', id));
    const es = new EventSource(`/scrape/stream?${params.toString()}`);
    es.onmessage = e => {
      const data = JSON.parse(e.data);
      setStatus(data);
      if (data.all_ready) es.close();
    };
    es.onerror = err => {
      if (es.readyState !== EventSource.CLOSED) {
        console.error('SSE error:', err);
      }
    };
    return () => es.close();
  }, [taskIds, setStatus]);

  const renderResults = () => {
    if (!status.results) return null;
    return Object.entries(status.results).map(([taskId, results]) => (
      <div key={taskId} className="taskGroup">
        <h3>Task: {taskId}</h3>
        {results.map((res, i) => (
          <div key={i} className={res.title.includes("O'Reilly") ? "resultCard oreilly" : "resultCard advance"}>
            <p><strong>URL:</strong> {res.url}</p>
            <p><strong>Title:</strong> {res.title}</p>
            {res.store && (
              <p>
                <strong>Store:</strong>{' '}
                {Array.isArray(res.store)
                  ? res.store.join(', ')
                  : res.store}
              </p>
            )}
            {res.title.includes("Advance") ? (
              <div> 
                <p><strong>Total Results:</strong> {res.total_prices}</p>
                <p><strong>Time Taken:</strong> {res.time_taken}</p>
                <div className="listings">
                  {res.prices.map((listing, idx) => (
                    <div
                      key={idx}
                      className="listing advance"
                    >
                      <a href={`https://shop.advanceautoparts.com${listing.link}`} target='_blank' rel="noreferrer" className='listingLink'>
                        Name: {listing.name} <br />
                        Price: ${listing.price} <br />
                        Part#: {listing.part_number} <br /> <br /> 
                        Availability: {listing.availability} <br /> <br />
                        
                        <img src={listing.image} alt="listingImage" className="listingImage" />
                      </a>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div> 
                <p><strong>Total Results:</strong> {res.total_prices}</p>
                <p><strong>Time Taken:</strong> {res.time_taken}</p>
                <div className="listings">
                  {res.prices.map((listing, idx) => (
                    <div
                      key={idx}
                      className="listing oreilly"
                    >
                      <a href={`https://www.oreillyauto.com${listing.link}`} target='_blank' rel="noreferrer">
                        Name: {listing.name} <br /> Price: {listing.price} <br /> {listing.part_number} <br /> <br /> Availability: {listing.availability} <br /> <br />
                        <img src={listing.image} alt='listingImage' className="listingImage"  />
                      </a>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    ));
  };

  return (
    <div className="scrapeResultsStatus">
      {status ? (
        status.all_ready ? (
          <>
            {renderResults()}
          </>
        ) : (
          <>
            <h2>Scrape Task Updating</h2>
            <pre className="statusJson">
              {JSON.stringify(status, null, 2)}
            </pre>
          </>
        )
      ) : (
        <div>Waiting for scrape updates…</div>
      )}
    </div>  
  );
}

export default ScrapeResultsStatus;
