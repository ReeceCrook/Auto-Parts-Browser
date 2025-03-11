import '../css/App.css';
import React, { useState } from "react";
import ScrapeStatus from './ScrapeStatus';
import PlacesMap from './PlacesMap';

function App() {
  const [searchQuery, setSearchQuery] = useState('');
  const [response, setResponse] = useState(null);
  const [selectedPlace, setSelectedPlace] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (searchQuery.trim() === "") {
      alert("Please enter search");
      return;
    }
    setIsSubmitting(true);
    setError(null);
    try {
      const res = await fetch(`/scrape/${encodeURIComponent(searchQuery)}`);
      if (!res.ok) {
        throw new Error('Network response was not ok');
      }
      const data = await res.json();
      setResponse(data);
    } catch (err) {
      console.error("Error fetching scrape data:", err);
      setError(err.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  console.log(selectedPlace, '<== Selected Place');
  console.log(searchQuery, "<== searchQuery || Response ==>", response?.task_id);

  return (
    <div className="App">
      <div className="GooglesPlacesMapContainer">
        <PlacesMap 
          selectedPlace={selectedPlace} 
          setSelectedPlace={setSelectedPlace} 
          response={response}
          setResponse={setResponse}
        />
      </div>
      <header className="App-header">
        <h1>Auto Parts Browser</h1>
        <form onSubmit={handleSubmit}>
          <label htmlFor="searchInput">Search:</label>
          <input
            id="searchInput"
            type="text"
            name="search"
            placeholder="Enter search query"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          <button type="submit" disabled={isSubmitting}>
            {isSubmitting ? "Submitting..." : "Submit"}
          </button>
        </form>
        {error && <p className="error">Error: {error}</p>}
      </header>
      <div>
        {response?.task_id ? (
          <ScrapeStatus
            groupId={response.group_task_id} 
            taskId={response.task_id} 
          />
        ) : null}
      </div>
    </div>
  );
}

export default App;
