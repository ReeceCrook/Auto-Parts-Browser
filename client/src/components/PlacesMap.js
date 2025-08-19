/* global google */
import { useState, useEffect } from "react";
import "../css/PlacesMap.css"
import {
  Map, 
  AdvancedMarker,
  MapControl,
  ControlPosition,
  useMap
} from "@vis.gl/react-google-maps";
import PlaceSearch from "./PlaceSearch";

const API = process.env.API_URL;

function MapController({ selectedPlace }) {
  const map = useMap();
  useEffect(() => {
    const loc = selectedPlace?.location;
    if (!map || !loc) return;
    if (selectedPlace.viewport) {
      const { north, south, east, west } = selectedPlace.viewport;
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
        location: loc,
        viewport: null,
        name: "My Location",
        formatted_address: null,
        radius: parseFloat(radius || 0) * 1609.34
      });
    });
  };

  const handlePlaceSelect = (place) => {
    const loc = {
      lat: place.location.lat(),
      lng: place.location.lng()
    };
    console.log(place.location, "<=== place.location || loc ===>", loc)
    const viewport = place.viewport?.toJSON();
    console.log("Viewport ==>", viewport)
    setSelectedPlace({
      location: loc,
      viewport: viewport,
      name: place.displayName,
      formatted_address: place.formattedAddress,
      radius: parseFloat(radius || 0) * 1609.34
    });
  };

  const handleFetchPlaces = () => {
    const loc = selectedPlace.location;
    const metersRadius = Math.round(parseFloat(radius) * 1609.34);
    if (!loc || !metersRadius) return;
  
    fetch(`${API}/places`, {
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
    <div>
      <Map
        mapId="ad030c5dd452d96c"
        defaultCenter={{ lat: 44.967243, lng: -103.771556 }}
        defaultZoom={3}
        disableDefaultUI
        gestureHandling="greedy"
        style={{ width: '100%', height: '400px' }}
      >
        <MapController selectedPlace={selectedPlace} />

        {selectedPlace?.location && (
          <AdvancedMarker
            position={selectedPlace.location}
          />
        )}
      </Map>

      <MapControl position={ControlPosition.TOP_CENTER}>
        <div style={{ alignItems: "center"}}>
          <PlaceSearch onPlaceSelect={handlePlaceSelect} />
          <input
            type="number"
            min="1"
            className="milesInput"
            placeholder="Miles"
            value={radius}
            onChange={e => setRadius(e.target.value)}
          />
          <button onClick={handleFetchPlaces} className={!selectedPlace?.location || !radius ? "fetchPlacesButtonDisabled" : "fetchPlacesButtonEnabeled"} disabled={!selectedPlace?.location || !radius}>Search Nearby</button>
          <button onClick={handleLocateMe} className="locateMeButton">My Location</button>
        </div>
      </MapControl>
    </div>
  );
}

export default PlacesMap