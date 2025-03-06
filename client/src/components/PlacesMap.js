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

function PlacesMap({ selectedPlace, setSelectedPlace }) {
  const [markerRef, marker] = useAdvancedMarkerRef();
  const [radius, setRadius] = useState(50000);

  const handleRadiusChange = (e) => {
    setRadius(e.target.value);
  };

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
          <PlaceAutocomplete onPlaceSelect={setSelectedPlace} />
          <div>
            <input 
              type="number" 
              placeholder="Enter radius in meters" 
              value={radius} 
              onChange={handleRadiusChange} 
            />
          </div>
        </div>
      </MapControl>
      <MapHandler place={selectedPlace} marker={marker} radius={radius} />
    </APIProvider>
  );
}

function MapHandler({ place, marker, radius }) {
  const map = useMap();

  function performGetDetails(service, placeId) {
    const detailRequest = {
      placeId: placeId,
      fields: ["website"],
    };
    service.getDetails(detailRequest, (placeDetails, status) => {
      if (status === google.maps.places.PlacesServiceStatus.OK) {
        console.log(`Details for ${placeId}:`, placeDetails);
      } else {
        console.error("Place details request failed:", status);
      }
    });
  }
    
  function performTextSearch(map, place, radius) {
    const location = place?.geometry?.location ? place.geometry.location : map.getCenter();
    const service = new google.maps.places.PlacesService(map);
    const queries = ["O'Reilly Auto Parts", "Advance Auto Parts"];
    
    queries.forEach((query) => {
      const request = {
        query: query,
        location: location,
        radius: radius,
      };

      service.textSearch(request, (results, status) => {
        if (status === google.maps.places.PlacesServiceStatus.OK) {
          console.log(`Text search results for ${query}:`, results);
          results.forEach((result) => {
            performGetDetails(service, result.place_id);
          });
        } else {
          console.error(`Text search failed for ${query}:`, status);
        }
      });
    });
  }

  useEffect(() => {
    if (!map || !place || !marker) return;

    if (place.geometry?.viewport) {
      map.fitBounds(place.geometry.viewport);
    }
    marker.position = place.geometry?.location;

    performTextSearch(map, place, radius);
  }, [map, place, marker, radius]);

  return null;
}

function PlaceAutocomplete({ onPlaceSelect }) {
  const [placeAutocomplete, setPlaceAutocomplete] = useState(null);
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
      onPlaceSelect(placeAutocomplete.getPlace());
    });
    return () => listener.remove();
  }, [onPlaceSelect, placeAutocomplete]);

  return (
    <div className="autocomplete-container">
      <input ref={inputRef} placeholder="Search for a place..." />
    </div>
  );
}

export default PlacesMap;
