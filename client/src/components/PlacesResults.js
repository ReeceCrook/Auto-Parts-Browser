import '../css/App.css';
import React from 'react';

function PlacesResults({ response, onLocationToggle, selectedLocations }) {
  return (
    <div className='places-results-wrapper'>
      <h2>Places Results</h2>
      {response ? Object.entries(response.results).map(([taskId, result]) => (
        <div key={taskId} className='places-results-card'>
          <div style={{ textAlign: 'right' }}>
            <input 
              type="checkbox" 
              checked={selectedLocations[result.place_id] ? true : false}
              onChange={(e) => onLocationToggle(result.place_id, result, e.target.checked)}
            />
          </div>
          <h2>{result.name}</h2>
          <h3>Task ID: {taskId}</h3>
          <h4>Address: {result.vicinity}</h4>
          <div>
            {result.opening_hours && result.opening_hours.open_now !== undefined
              ? `Open: ${result.opening_hours.open_now}`
              : "No open result"} 
            <br />
            Website: {result.website || "N/A"}
          </div>
          <pre>{JSON.stringify(result, null, 2)}</pre>
        </div>
      ))
      : "No results"}
    </div>
  );
}

export default PlacesResults;
