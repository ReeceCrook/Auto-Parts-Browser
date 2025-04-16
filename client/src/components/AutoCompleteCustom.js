import React, { useState, useRef, useEffect } from "react";

function AutoCompleteCustom({ onPlaceSelect }) {
  const [input, setInput] = useState("");
  const [predictions, setPredictions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const serviceRef = useRef(null);
  const tokenRef = useRef(null);
  const placesServiceRef = useRef(null);

  useEffect(() => {
    const lib = window.google?.maps?.places;
    if (!lib) return;
    serviceRef.current = new lib.AutocompleteService();
    tokenRef.current = new lib.AutocompleteSessionToken();
    placesServiceRef.current = new lib.PlacesService(
      document.createElement("div")
    );
  }, []);

  useEffect(() => {
    const svc = serviceRef.current;
    const token = tokenRef.current;
    if (!svc) return;
    if (input.length < 2 || !showSuggestions) {
      setPredictions([]);
      return;
    }
    svc.getPlacePredictions(
      { input, sessionToken: token },
      (results) => setPredictions(results || [])
    );
  }, [input, showSuggestions]);

  function choose(pred) {
    const ps = placesServiceRef.current;
    const token = tokenRef.current;
    if (!ps) return;

    ps.getDetails(
      { placeId: pred.place_id, sessionToken: token,
        fields: ["geometry","name","formatted_address"]
      },
      (place, status) => {
        if (status === "OK" && place.geometry) {
          onPlaceSelect(place);
          setInput(place.formatted_address);
          setShowSuggestions(false);
          setPredictions([]);
          tokenRef.current = new window.google.maps.places.AutocompleteSessionToken();
        }
      }
    );
  }

  return (
    <div style={{ position: "relative", width: "auto", marginRight: "2%" }}>
      <input
        type="text"
        value={input}
        onChange={e => {
          setInput(e.target.value);
          setShowSuggestions(true);
        }}
        placeholder="Search for a place or click 'My Location'"
        style={{ width: "100%", padding: "6px 8px" }}
      />
      {(showSuggestions && predictions.length > 0) && (
        <ul style={{
          position: "absolute",
          top: "100%",
          left: 0,
          right: 0,
          zIndex: 1000,
          background: "white",
          margin: 0,
          padding: 4,
          listStyle: "none",
          boxShadow: "0 1px 4px rgba(0,0,0,0.2)"
        }}>
          {predictions.map(p => (
            <li
              key={p.place_id}
              onClick={() => choose(p)}
              style={{ padding: "4px 6px", cursor: "pointer" }}
            >
              {p.description}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default AutoCompleteCustom