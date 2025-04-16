/* global google */
import React, { useState, useEffect } from "react";
import {
  APIProvider,
  Map,
  AdvancedMarker,
  MapControl,
  ControlPosition,
  useMap
} from "@vis.gl/react-google-maps";
import AutoCompleteCustom from "./AutoCompleteCustom";

function MapController({ selectedPlace }) {
  const map = useMap();
  useEffect(() => {
    const loc = selectedPlace?.geometry?.location;
    if (!map || !loc) return;
    if (selectedPlace.geometry.viewport) {
      const { north, south, east, west } = selectedPlace.geometry.viewport;
      const bounds = new google.maps.LatLngBounds(
        { lat: south, lng: west },
        { lat: north, lng: east }
      );
      map.fitBounds(bounds);
    } else {
      map.panTo(loc);
      map.setZoom(14);
    }
  }, [map, selectedPlace]);
  return null;
}

function PlacesMap({ selectedPlace, setSelectedPlace, placesResponse, setPlacesResponse }) {
  const [radius, setRadius] = useState("");

  const handleLocateMe = () => {
    if (!navigator.geolocation) return;
    navigator.geolocation.getCurrentPosition(({ coords }) => {
      const loc = { lat: coords.latitude, lng: coords.longitude };
      setSelectedPlace({
        geometry: { location: loc, viewport: null },
        name: "My Location",
        formatted_address: null,
        radius: parseFloat(radius || 0) * 1609.34
      });
    });
  };

  const handlePlaceSelect = (place) => {
    const loc = {
      lat: place.geometry.location.lat(),
      lng: place.geometry.location.lng()
    };
    const viewport = place.geometry.viewport?.toJSON();
    setSelectedPlace({
      geometry: { location: loc, viewport },
      name: place.name,
      formatted_address: place.formatted_address,
      radius: parseFloat(radius || 0) * 1609.34
    });
  };

  const handleFetchPlaces = () => {
    const loc = selectedPlace.geometry.location;
    const metersRadius = Math.round(parseFloat(radius) * 1609.34);
    if (!loc || !metersRadius) return;
  
    fetch("/places", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        location: loc,
        radius:   metersRadius
      })
    })
    .then(r => r.ok ? r.json() : Promise.reject(r))
      .then(setPlacesResponse)
      .catch(console.error);
  };
  

  return (
    <APIProvider apiKey="AIzaSyCv3Wf69VArh-8eQlJGzOGRlFpiZz4dYOU">
      <Map
        mapId="ad030c5dd452d96c"
        defaultCenter={{ lat: 22.5, lng: 0 }}
        defaultZoom={3}
        disableDefaultUI
        gestureHandling="greedy"
      >
        <MapController selectedPlace={selectedPlace} />

        {selectedPlace?.geometry?.location && (
          <AdvancedMarker
            position={selectedPlace.geometry.location}
          />
        )}
      </Map>

      <MapControl position={ControlPosition.TOP_CENTER}>
        <div style={{ alignItems: "center"}}>
          <AutoCompleteCustom onPlaceSelect={handlePlaceSelect} />
          <input
            type="number"
            placeholder="Miles"
            value={radius}
            onChange={e => setRadius(e.target.value)}
          />
          <button onClick={handleFetchPlaces} disabled={!selectedPlace?.geometry?.location || !radius}>Search Nearby</button>
          <button onClick={handleLocateMe}>My Location</button>
        </div>
      </MapControl>
    </APIProvider>
  );
}

export default PlacesMap