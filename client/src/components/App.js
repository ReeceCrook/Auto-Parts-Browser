import '../css/App.css';
import React, { useEffect, useState } from "react";
import ScrapeStatus from './ScrapeStatus';
import PlacesMap from './PlacesMap';

function App() {
  const [formData, setFormData] = useState([])
  const [response, setResponse] = useState({})
  const [selectedPlace, setSelectedPlace] = useState(null);
  const [coordinates, setCoordinates] = useState(null)

  function handleSubmit(e) {
    e.preventDefault()
    if(formData !== "") {
      fetch(`/scrape/${formData}`).then((r) => {
        if (r.ok) {
          r.json().then((res) => setResponse(res));
        }
      });
    } else {
      alert("Please enter search")
    }
  }

 
  console.log(coordinates);
  console.log(formData, "<== formData || Response ==>", response)
  return (
    <div className="App">
      <div className='GooglesPlacesMapContainer'>
        <PlacesMap selectedPlace={selectedPlace} setSelectedPlace={setSelectedPlace} />
      </div>
      <header className="App-header">
        Auto Parts Browser
        <form onSubmit={(e) => handleSubmit(e)}>
          <label>
            Search:
            <input type='text' name='Search' onChange={(e) => setFormData(e.target.value)} />
          </label>
          <input type="submit" value="Submit" />
        </form>
      </header>
      <div>
        {response.individal_task_ids ? <ScrapeStatus groupId={response.group_task_id} taskIds={response.individal_task_ids} /> : null}
      </div>
    </div>
  );
}

export default App;