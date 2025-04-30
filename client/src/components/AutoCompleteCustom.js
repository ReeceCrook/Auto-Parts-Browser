import React, { useState, useRef, useEffect, useCallback } from "react";
import debounce from "lodash.debounce";

function AutoCompleteCustom({ onPlaceSelect }) {
  const [input, setInput] = useState("");
  const [predictions, setPredictions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);

  const serviceRef = useRef(null);
  const tokenRef = useRef(null);
  const placesRef = useRef(null);

  useEffect(() => {
    const id = setInterval(() => {
      const lib = window.google?.maps?.places;
      if (lib) {
        clearInterval(id);
        serviceRef.current = new lib.AutocompleteService();
        tokenRef.current = new lib.AutocompleteSessionToken();
        placesRef.current = new lib.PlacesService(document.createElement("div"));
      }
    }, 100);
    return () => clearInterval(id);
  }, []);

  const fetchPredictions = useCallback(
    debounce((text) => {
      if (!serviceRef.current) return;
      serviceRef.current.getPlacePredictions(
        { input: text, sessionToken: tokenRef.current },
        (results, status) => {
          if (status === window.google.maps.places.PlacesServiceStatus.OK) {
            setPredictions(results);
          } else {
            console.warn("Places Autocomplete error:", status);
            setPredictions([]);
          }
        }
      );
    }, 300),
    []
  );

  useEffect(() => {
    if (input.length >= 2 && showSuggestions) {
      fetchPredictions(input);
    } else {
      setPredictions([]);
    }
  }, [input, showSuggestions, fetchPredictions]);

  function choose(pred) {
    if (!placesRef.current) return;
    placesRef.current.getDetails(
      {
        placeId: pred.place_id,
        sessionToken: tokenRef.current,
        fields: ["geometry", "name", "formatted_address"]
      },
      (place, status) => {
        if (status === window.google.maps.places.PlacesServiceStatus.OK && place.geometry) {
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
    <div style={{ position: "relative", width: "100%" }}>
      <input
        type="text"
        value={input}
        onChange={e => {
          setInput(e.target.value);
          setShowSuggestions(true);
        }}
        placeholder="Search for a place..."
        style={{ width: "100%", padding: "6px 8px" }}
      />
      {showSuggestions && predictions.length > 0 && (
        <ul style={{
          position: "absolute", top: "100%", left: 0, right: 0,
          background: "white", margin: 0, padding: 4, listStyle: "none",
          boxShadow: "0 1px 4px rgba(0,0,0,0.2)", zIndex: 1000
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