import React, { useRef, useEffect } from 'react';
import { useMapsLibrary } from '@vis.gl/react-google-maps';

function PlaceSearch({ onPlaceSelect }) {
  const containerRef = useRef(null);
  const placesLib     = useMapsLibrary('places');

  useEffect(() => {
    if (!placesLib) return;

    const widget = new placesLib.PlaceAutocompleteElement({
    });
    widget.placeholder = 'Search for a place…';

    const container = containerRef.current;
    container.appendChild(widget);

    widget.addEventListener('gmp-select', async (e) => {
      const prediction = e.detail.placePrediction;
      const place = prediction.toPlace();
      await place.fetchFields({
        fields: ['geometry', 'name', 'formatted_address']
      });
      onPlaceSelect(place);
    });

    return () => {
      widget.removeEventListener('gmp-select', () => {});
      container.removeChild(widget);
    };
  }, [placesLib, onPlaceSelect]);

  return <div ref={containerRef} style={{ width: '100%' }} />;
}

export default PlaceSearch;
