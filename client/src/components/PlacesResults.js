import '../css/PlacesResults.css';
import React, { useState, useEffect } from 'react';

function PlacesResults({ response, onLocationToggle, selectedLocations, isDetailsViewEnabled, setIsDetailsViewEnabled }) {
  const [resultText, setResultText] = useState("");
  const [selectedDetails, setSelectedDetails] = useState([]);

  useEffect(() => {
    if (response && response.results) {
      const keys = Object.keys(response.results);
      if (keys.length > 0) {
        const firstKey = keys[0];
        const resultValue = response.results[firstKey].results;
        if (typeof resultValue === 'string') {
          setResultText(resultValue);
        } else {
          setResultText("");
        }
      }
    }
  }, [response]);

  function handleApply() {
    const details = Object.entries(selectedLocations).map(([place_id, place]) => ({
      id:      place_id,
      name:    place.name,
      rating:  place.rating,
      openNow: place.opening_hours?.open_now,
      website: place.website,
      location: place.vicinity
    }));
    setSelectedDetails(details);
    setIsDetailsViewEnabled(true);
  }


  const MainUI = () => (
    <>
      <div className='mainUIWrapper'>
        <h2>Places Results</h2>
        <div className='mainUIInnerWrapper'>
          <button onClick={handleApply} className='mainUIApplyButton'>Apply</button>
          <button onClick={handleApply} className='mainUIApplyButton bottom'>Apply</button>
          <div className='placesResultsWrapper'>
            {resultText !== "" ? <div>{resultText}</div> : response ? Object.entries(response.results).map(([taskId, result]) => (
              <div key={taskId} className='placesResultsCard'>
                <div style={{ textAlign: 'right' }}>
                  <input 
                    type="checkbox" 
                    checked={!!selectedLocations[result.place_id]}
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
        </div>
      </div>
    </>
  )


  const DetailsUI = () => (
    <>
    <div className='detailsUIWrapper'>
      <div className='detailsUIInnerWrapper'>
        <button className='detailsUIEditButton' onClick={() => setIsDetailsViewEnabled(false)}>Edit</button>
        <div className="cardGrid">
          {selectedDetails.map(place => (
            <div key={place.id} className="card detailCard">
              <h2>{place.name}</h2>
              <h3>{place.location}</h3>
              <h4>{place.openNow}</h4>
              <h4>{place.rating}⭐</h4>
              <a href={place.website} target='_blank' rel="noreferrer">Official Website</a>
            </div>
          ))}
        </div>
      </div>
    </div>

    </>
  ) 
  
  return !response ? "^ Please do a place search ^" : isDetailsViewEnabled ? <DetailsUI /> : <MainUI />;
}
  
export default PlacesResults;
