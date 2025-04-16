import '../css/App.css';
import React, { useState } from "react";
import ScrapeStatus from './PlacesStatus';
import PlacesMap from './PlacesMap';
import PlacesResults from './PlacesResults';
import ScrapeResultsStatus from './ScrapeResultStatus';
import { APIProvider } from "@vis.gl/react-google-maps";

function App() {
  const [searchQuery, setSearchQuery] = useState('');
  const [placesResponse, setPlacesResponse] = useState(null);
  const [scrapeResponse, setScrapeResponse] = useState(null);
  const [selectedPlace, setSelectedPlace] = useState(null);
  const [selectedLocations, setSelectedLocations] = useState({});
  const [error, setError] = useState(null);
  const [SSEStatus, setSSEStatus] = useState(null);
  console.log(selectedLocations, "SELECTED")

  const handleLocationToggle = (placeId, result, checked) => {
    setSelectedLocations(prev => {
      console.log(result, "PREV", prev)
      const updated = { ...prev };
      if (checked) {
        updated[placeId] = result;
      } else {
        delete updated[placeId];
      }
      return updated;
    });
  };

  const handleScrapeSelected = async () => {
    const oreilly = [];
    const advance = [];
    Object.values(selectedLocations).forEach(loc => {
      if (loc.name.includes("O'Reilly")) {
        oreilly.push(loc);
      } else if (loc.name.includes("Advance")) {
        advance.push(loc);
      }
    });
  
    const payload = {
      search: searchQuery,
      oreilly,
      advance,
    };
  
    try {
      const res = await fetch('/scrape/selected', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (!res.ok) throw new Error("Scrape selected request failed");
      const data = await res.json();
      console.log("Scrape Selected Task IDs:", data);
      setScrapeResponse(data);
    } catch (err) {
      console.error("Error submitting selected locations:", err);
      setError(err)
    }
  };
  
  

  return (
    <div className="App">
      <h1>Auto Parts Browser</h1>
      <div className="GooglesPlacesMapContainer">
        <APIProvider apiKey="AIzaSyCv3Wf69VArh-8eQlJGzOGRlFpiZz4dYOU">
          <PlacesMap 
          selectedPlace={selectedPlace} 
          setSelectedPlace={setSelectedPlace} 
          placesResponse={placesResponse}
          setPlacesResponse={setPlacesResponse}
        />
        </APIProvider>
      </div>
      <div className='places-wrapper'>
        <PlacesResults 
          response={SSEStatus} 
          onLocationToggle={handleLocationToggle}
          selectedLocations={selectedLocations}
        />
      </div>
      <div className="search-wrapper">
        <form>
          <label htmlFor="searchInput">Search:</label>
          <input
            id="searchInput"
            type="text"
            name="search"
            placeholder="Enter search query"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          <button type='button' onClick={handleScrapeSelected}>Scrape Selected Locations</button>
        </form>
        {error && <p className="error">Error: {error}</p>}
      </div>
      <div style={{ marginTop: '20px' }}>
        {scrapeResponse && (
          <ScrapeResultsStatus
            taskIds={[...(scrapeResponse.oreilly || []), ...(scrapeResponse.advance || [])]}
            status={scrapeResponse}
            setStatus={setScrapeResponse}
          />
        )}
      </div>
      <div>
        {placesResponse?.task_id ? (
          <ScrapeStatus
            groupId={placesResponse.group_task_id} 
            taskId={placesResponse.task_id} 
            status={SSEStatus}
            setStatus={setSSEStatus}
          />
        ) : null}
      </div>
    </div>
  );
}

export default App;
