/* global google */
import React, { useState, useEffect, useRef } from "react";
import {
  APIProvider,
  ControlPosition,
  MapControl,
  AdvancedMarker,
  Map,
  useMap,
  useMapsLibrary,
  useAdvancedMarkerRef,
} from "@vis.gl/react-google-maps";

const API_KEY = "AIzaSyCv3Wf69VArh-8eQlJGzOGRlFpiZz4dYOU";


function PlacesMap({ selectedPlace, setSelectedPlace, placesResponse, setPlacesResponse }) {
  const [markerRef, marker] = useAdvancedMarkerRef();
  const [radius, setRadius] = useState("");
  function transformPlace(place) {
    if (!place || !place.geometry || !place.geometry.location) return null;
    const metersRadius = parseFloat(radius) * 1609.34
    return {
      formatted_address: place.formatted_address,
      name: place.name,
      location: {
        lat: place.geometry.location.lat(),
        lng: place.geometry.location.lng()
      },
      radius: metersRadius
    };
  }

  function handlePlaceSelect(place) {
    const transformedPlace = transformPlace(place);
    console.log(transformedPlace)
    if (!transformedPlace) return;
    setSelectedPlace(transformedPlace);
    
    fetch('/places', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(transformedPlace)
    })
      .then((r) => {
        if (r.ok) return r.json();
        throw new Error('Network response was not ok');
      })
      .then((res) => setPlacesResponse(res))
      .catch((error) => console.error('Error:', error));
  }
  
  return (
    <APIProvider
      apiKey={API_KEY}
      solutionChannel="GMP_devsite_samples_v3_rgmautocomplete"
    >
      <Map
        mapId="bf51a910020fa25a"
        defaultZoom={3}
        defaultCenter={{ lat: 22.54992, lng: 0 }}
        gestureHandling="greedy"
        disableDefaultUI={true}
      >
        <AdvancedMarker ref={markerRef} position={null} />
      </Map>
      <MapControl position={ControlPosition.TOP}>
        <div className="autocomplete-control">
          <PlaceAutocomplete onPlaceSelect={handlePlaceSelect} />
          <div>
            <input 
              type="number" 
              placeholder="Enter radius in miles" 
              value={radius} 
              onChange={(e) => setRadius(e.target.value)}
            />
          </div>
          <div>
          </div>
        </div>
      </MapControl>
      <MapHandler place={selectedPlace} marker={marker} radius={radius} />
    </APIProvider>
  );
}

function MapHandler({ place, marker, radius }) {
  const map = useMap();

  useEffect(() => {
    if (!map || !place || !marker) return;

    if (place.geometry?.viewport) {
      map.fitBounds(place.geometry.viewport);
    }
    marker.position = place.geometry?.location;

  }, [map, place, marker, radius]);

  return null;
}

function PlaceAutocomplete({ onPlaceSelect }) {
  const [placeAutocomplete, setPlaceAutocomplete] = useState(null);
  const [selectedPlace, setSelectedPlace] = useState(null);
  const inputRef = useRef(null);
  const places = useMapsLibrary("places");

  useEffect(() => {
    if (!places || !inputRef.current) return;
    const options = {
      fields: ["geometry", "name", "formatted_address"],
    };
    setPlaceAutocomplete(new places.Autocomplete(inputRef.current, options));
  }, [places]);

  useEffect(() => {
    if (!placeAutocomplete) return;
    const listener = placeAutocomplete.addListener("place_changed", () => {
      const place = placeAutocomplete.getPlace();
      setSelectedPlace(place);
    });
    return () => listener.remove();
  }, [placeAutocomplete]);

  return (
    <div className="autocomplete-container">
      <input ref={inputRef} placeholder="Search for a place..." />
      <button onClick={() => onPlaceSelect(selectedPlace)} disabled={!selectedPlace} style={{"backgroundColor": "white"}}>
        Submit
      </button>
    </div>
  );
}

export default PlacesMap;
