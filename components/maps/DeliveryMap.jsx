import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap, Circle } from 'react-leaflet';
import { Navigation, Package, MapPin, Truck } from 'lucide-react';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Fix leaflet default markers
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// Custom marker icons
const createCustomIcon = (color, type = 'pin') => {
  const svg = type === 'driver'
    ? `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="${color}" width="32" height="32"><circle cx="12" cy="12" r="10" fill="${color}"/><path d="M8 14h8M7 10l2-2 1 1 3-3 3 3 1-1 2 2" stroke="white" fill="none" stroke-width="1.5"/></svg>`
    : `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="${color}" width="32" height="40"><path d="M12 0C7.31 0 3.5 3.81 3.5 8.5c0 6.38 8.5 15.5 8.5 15.5s8.5-9.12 8.5-15.5C20.5 3.81 16.69 0 12 0zm0 12a3.5 3.5 0 110-7 3.5 3.5 0 010 7z"/></svg>`;

  return L.divIcon({
    html: svg,
    className: 'custom-marker',
    iconSize: [32, type === 'driver' ? 32 : 40],
    iconAnchor: [16, type === 'driver' ? 16 : 40],
    popupAnchor: [0, type === 'driver' ? -16 : -40],
  });
};

const originIcon = createCustomIcon('#0050FF');
const destinationIcon = createCustomIcon('#00FF88');
const driverIcon = createCustomIcon('#FF9500', 'driver');

// Component to fit bounds
function FitBounds({ points }) {
  const map = useMap();

  useEffect(() => {
    if (points.length >= 2) {
      const bounds = L.latLngBounds(points.map(p => [p.lat, p.lng]));
      map.fitBounds(bounds, { padding: [50, 50] });
    } else if (points.length === 1) {
      map.setView([points[0].lat, points[0].lng], 14);
    }
  }, [points, map]);

  return null;
}

export default function DeliveryMap({
  origin,
  destination,
  driverLocation,
  route,
  zones = [],
  showZones = false,
  height = '400px',
  interactive = true
}) {
  const defaultCenter = { lat: 28.6139, lng: 77.2090 }; // Delhi

  const points = [
    origin && { lat: origin.lat, lng: origin.lng },
    destination && { lat: destination.lat, lng: destination.lng },
    driverLocation && { lat: driverLocation.lat, lng: driverLocation.lng },
  ].filter(Boolean);

  const center = points.length > 0 ? points[0] : defaultCenter;

  return (
    <div className="relative rounded-2xl overflow-hidden" style={{ height }}>
      <style>{`
        .custom-marker {
          background: transparent;
          border: none;
        }
        .leaflet-container {
          background: #1a1a2e;
          font-family: inherit;
        }
        .leaflet-popup-content-wrapper {
          background: rgba(10, 10, 12, 0.95);
          color: white;
          border-radius: 12px;
          border: 1px solid rgba(255,255,255,0.1);
        }
        .leaflet-popup-tip {
          background: rgba(10, 10, 12, 0.95);
        }
        .leaflet-popup-content {
          margin: 12px;
        }
      `}</style>

      <MapContainer
        center={[center.lat, center.lng]}
        zoom={13}
        style={{ height: '100%', width: '100%' }}
        zoomControl={interactive}
        dragging={interactive}
        scrollWheelZoom={interactive}
      >
        <TileLayer
          attribution='&copy; <a href="https://carto.com/">CARTO</a>'
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        />

        {points.length > 0 && <FitBounds points={points} />}

        {/* Delivery zones */}
        {showZones && zones.map((zone, idx) => (
          <Circle
            key={idx}
            center={[zone.center_lat, zone.center_lng]}
            radius={zone.radius_km * 1000}
            pathOptions={{
              color: '#0050FF',
              fillColor: '#0050FF',
              fillOpacity: 0.1,
              weight: 1,
            }}
          />
        ))}

        {/* Origin marker */}
        {origin && (
          <Marker position={[origin.lat, origin.lng]} icon={originIcon}>
            <Popup>
              <div className="text-sm">
                <div className="font-semibold text-[#0050FF] mb-1">Pickup Location</div>
                <div className="text-gray-300">{origin.address || 'Origin'}</div>
              </div>
            </Popup>
          </Marker>
        )}

        {/* Destination marker */}
        {destination && (
          <Marker position={[destination.lat, destination.lng]} icon={destinationIcon}>
            <Popup>
              <div className="text-sm">
                <div className="font-semibold text-[#00FF88] mb-1">Delivery Location</div>
                <div className="text-gray-300">{destination.address || 'Destination'}</div>
              </div>
            </Popup>
          </Marker>
        )}

        {/* Driver marker */}
        {driverLocation && (
          <Marker position={[driverLocation.lat, driverLocation.lng]} icon={driverIcon}>
            <Popup>
              <div className="text-sm">
                <div className="font-semibold text-[#FF9500] mb-1">Driver Location</div>
                <div className="text-gray-300">{driverLocation.name || 'Driver'}</div>
              </div>
            </Popup>
          </Marker>
        )}

        {/* Route line */}
        {route && route.length > 1 && (
          <Polyline
            positions={route.map(p => [p.lat, p.lng])}
            pathOptions={{
              color: '#0050FF',
              weight: 4,
              opacity: 0.8,
              dashArray: '10, 10',
            }}
          />
        )}

        {/* Simple line between origin and destination if no route */}
        {!route && origin && destination && (
          <Polyline
            positions={[
              [origin.lat, origin.lng],
              [destination.lat, destination.lng]
            ]}
            pathOptions={{
              color: '#0050FF',
              weight: 3,
              opacity: 0.6,
              dashArray: '5, 10',
            }}
          />
        )}
      </MapContainer>

      {/* Map overlay legend */}
      <div className="absolute bottom-4 left-4 z-[1000] bg-[#0A0A0C]/90 backdrop-blur-xl rounded-xl p-3 border border-white/10">
        <div className="flex items-center gap-4 text-xs">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-[#0050FF]" />
            <span className="text-gray-400">Pickup</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-[#00FF88]" />
            <span className="text-gray-400">Delivery</span>
          </div>
          {driverLocation && (
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-[#FF9500]" />
              <span className="text-gray-400">Driver</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
