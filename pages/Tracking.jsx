import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { createPageUrl } from '../utils';
import { motion } from 'framer-motion';
import { useQuery } from '@tanstack/react-query';
import { base44 } from '@/api/base44Client';
import {
  Search,
  Package,
  MapPin,
  Clock,
  Truck,
  CheckCircle,
  AlertCircle,
  Navigation,
  Phone,
  ArrowRight
} from 'lucide-react';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import DeliveryMap from '../components/map/DeliveryMap';
import TrackingTimeline from '../components/delivery/TrackingTimeline';
import { Badge } from "@/components/ui/badge";
import { format } from 'date-fns';

const statusConfig = {
  pending: { label: 'Pending', color: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30', icon: Clock },
  picked_up: { label: 'Picked Up', color: 'bg-blue-500/20 text-blue-400 border-blue-500/30', icon: Package },
  in_transit: { label: 'In Transit', color: 'bg-purple-500/20 text-purple-400 border-purple-500/30', icon: Truck },
  out_for_delivery: { label: 'Out for Delivery', color: 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30', icon: Navigation },
  delivered: { label: 'Delivered', color: 'bg-green-500/20 text-green-400 border-green-500/30', icon: CheckCircle },
  failed: { label: 'Failed', color: 'bg-red-500/20 text-red-400 border-red-500/30', icon: AlertCircle },
};

export default function Tracking() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedDelivery, setSelectedDelivery] = useState(null);
  const [hasSearched, setHasSearched] = useState(false);

  const urlParams = new URLSearchParams(window.location.search);
  const trackingIdFromUrl = urlParams.get('tracking_id');

  useEffect(() => {
    if (trackingIdFromUrl) {
      setSearchQuery(trackingIdFromUrl);
      handleSearch(trackingIdFromUrl);
    }
  }, [trackingIdFromUrl]);

  const { data: deliveries = [] } = useQuery({
    queryKey: ['deliveries'],
    queryFn: () => base44.entities.Delivery.list('-created_date', 100),
  });

  const { data: drivers = [] } = useQuery({
    queryKey: ['drivers'],
    queryFn: () => base44.entities.Driver.list(),
  });

  const handleSearch = async (query = searchQuery) => {
    setHasSearched(true);
    const found = deliveries.find(d =>
      d.tracking_id?.toLowerCase() === query.toLowerCase() ||
      d.id === query
    );
    setSelectedDelivery(found || null);
  };

  const getDriver = (driverId) => {
    return drivers.find(d => d.id === driverId);
  };

  const status = selectedDelivery ? statusConfig[selectedDelivery.status] : null;
  const StatusIcon = status?.icon || Package;

  // Sample tracking updates
  const trackingUpdates = selectedDelivery ? [
    { status: 'pending', timestamp: selectedDelivery.created_date, location: 'Order received' },
    selectedDelivery.status !== 'pending' && { status: 'picked_up', timestamp: new Date(new Date(selectedDelivery.created_date).getTime() + 2 * 60 * 60 * 1000).toISOString(), location: selectedDelivery.sender_address },
    ['in_transit', 'out_for_delivery', 'delivered'].includes(selectedDelivery.status) && { status: 'in_transit', timestamp: new Date(new Date(selectedDelivery.created_date).getTime() + 4 * 60 * 60 * 1000).toISOString(), location: 'Distribution center' },
    ['out_for_delivery', 'delivered'].includes(selectedDelivery.status) && { status: 'out_for_delivery', timestamp: new Date(new Date(selectedDelivery.created_date).getTime() + 6 * 60 * 60 * 1000).toISOString(), location: 'Out for delivery' },
    selectedDelivery.status === 'delivered' && { status: 'delivered', timestamp: selectedDelivery.actual_delivery || new Date().toISOString(), location: selectedDelivery.receiver_address },
  ].filter(Boolean) : [];

  return (
    <div className="min-h-screen bg-[#050505] pt-20">
      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-3xl md:text-4xl font-bold mb-4">Track Your Delivery</h1>
          <p className="text-gray-400 max-w-lg mx-auto">
            Enter your tracking ID to see real-time updates on your shipment
          </p>
        </div>

        {/* Search Box */}
        <div className="max-w-2xl mx-auto mb-12">
          <div className="flex gap-3">
            <div className="relative flex-1">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
              <Input
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                placeholder="Enter tracking ID (e.g., SAI1234ABCD)"
                className="pl-12 h-14 bg-white/5 border-white/10 text-lg rounded-xl"
              />
            </div>
            <Button
              onClick={() => handleSearch()}
              className="h-14 px-8 bg-[#0050FF] hover:bg-[#0040DD] rounded-xl"
            >
              Track
            </Button>
          </div>
        </div>

        {/* Results */}
        {hasSearched && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            {selectedDelivery ? (
              <div className="grid lg:grid-cols-2 gap-8">
                {/* Left Column - Details */}
                <div className="space-y-6">
                  {/* Status Card */}
                  <div className="p-6 rounded-2xl bg-gradient-to-br from-white/[0.03] to-transparent border border-white/5">
                    <div className="flex items-start justify-between mb-6">
                      <div className="flex items-center gap-4">
                        <div className={`p-4 rounded-2xl ${status?.color}`}>
                          <StatusIcon className="w-8 h-8" />
                        </div>
                        <div>
                          <div className="text-sm text-gray-500">Tracking ID</div>
                          <div className="text-xl font-bold">{selectedDelivery.tracking_id}</div>
                        </div>
                      </div>
                      <Badge variant="outline" className={`${status?.color} text-sm px-4 py-2`}>
                        {status?.label}
                      </Badge>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div className="p-4 rounded-xl bg-white/5">
                        <div className="text-sm text-gray-500 mb-1">Distance</div>
                        <div className="text-lg font-semibold">{selectedDelivery.distance_km?.toFixed(1) || '--'} km</div>
                      </div>
                      <div className="p-4 rounded-xl bg-white/5">
                        <div className="text-sm text-gray-500 mb-1">ETA</div>
                        <div className="text-lg font-semibold">
                          {selectedDelivery.estimated_delivery
                            ? format(new Date(selectedDelivery.estimated_delivery), 'MMM d, h:mm a')
                            : '--'}
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Route Info */}
                  <div className="p-6 rounded-2xl bg-gradient-to-br from-white/[0.03] to-transparent border border-white/5">
                    <h3 className="font-semibold text-lg mb-4">Route Details</h3>

                    <div className="relative pl-6">
                      <div className="absolute left-2 top-2 bottom-2 w-0.5 bg-gradient-to-b from-[#0050FF] to-[#00FF88]" />

                      <div className="relative mb-6">
                        <div className="absolute -left-4 top-1 w-3 h-3 rounded-full bg-[#0050FF] border-2 border-[#0A0A0C]" />
                        <div className="ml-2">
                          <div className="text-xs text-gray-500 mb-1">PICKUP</div>
                          <div className="font-medium">{selectedDelivery.sender_name}</div>
                          <div className="text-sm text-gray-400">{selectedDelivery.sender_address}</div>
                          {selectedDelivery.sender_phone && (
                            <a href={`tel:${selectedDelivery.sender_phone}`} className="flex items-center gap-1 mt-1 text-xs text-[#00D6FF] hover:underline">
                              <Phone className="w-3 h-3" /> {selectedDelivery.sender_phone}
                            </a>
                          )}
                        </div>
                      </div>

                      <div className="relative">
                        <div className="absolute -left-4 top-1 w-3 h-3 rounded-full bg-[#00FF88] border-2 border-[#0A0A0C]" />
                        <div className="ml-2">
                          <div className="text-xs text-gray-500 mb-1">DELIVERY</div>
                          <div className="font-medium">{selectedDelivery.receiver_name}</div>
                          <div className="text-sm text-gray-400">{selectedDelivery.receiver_address}</div>
                          {selectedDelivery.receiver_phone && (
                            <a href={`tel:${selectedDelivery.receiver_phone}`} className="flex items-center gap-1 mt-1 text-xs text-[#00D6FF] hover:underline">
                              <Phone className="w-3 h-3" /> {selectedDelivery.receiver_phone}
                            </a>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Timeline */}
                  <div className="p-6 rounded-2xl bg-gradient-to-br from-white/[0.03] to-transparent border border-white/5">
                    <h3 className="font-semibold text-lg mb-6">Tracking Timeline</h3>
                    <TrackingTimeline
                      delivery={selectedDelivery}
                      updates={trackingUpdates}
                    />
                  </div>
                </div>

                {/* Right Column - Map */}
                <div className="space-y-6">
                  <div className="p-6 rounded-2xl bg-gradient-to-br from-white/[0.03] to-transparent border border-white/5">
                    <h3 className="font-semibold text-lg mb-4">Live Location</h3>
                    <DeliveryMap
                      origin={selectedDelivery.sender_lat && selectedDelivery.sender_lng ? {
                        lat: selectedDelivery.sender_lat,
                        lng: selectedDelivery.sender_lng,
                        address: selectedDelivery.sender_address
                      } : null}
                      destination={selectedDelivery.receiver_lat && selectedDelivery.receiver_lng ? {
                        lat: selectedDelivery.receiver_lat,
                        lng: selectedDelivery.receiver_lng,
                        address: selectedDelivery.receiver_address
                      } : null}
                      driverLocation={selectedDelivery.current_lat && selectedDelivery.current_lng ? {
                        lat: selectedDelivery.current_lat,
                        lng: selectedDelivery.current_lng,
                        name: getDriver(selectedDelivery.driver_id)?.name || 'Driver'
                      } : null}
                      height="500px"
                    />
                  </div>

                  {/* Driver Info */}
                  {selectedDelivery.driver_id && getDriver(selectedDelivery.driver_id) && (
                    <motion.div
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="p-6 rounded-2xl bg-gradient-to-br from-[#0050FF]/10 to-transparent border border-[#0050FF]/20"
                    >
                      <h3 className="font-semibold mb-4">Your Driver</h3>
                      <div className="flex items-center gap-4">
                        <div className="w-16 h-16 rounded-full bg-[#0050FF]/20 flex items-center justify-center">
                          <Truck className="w-8 h-8 text-[#0050FF]" />
                        </div>
                        <div className="flex-1">
                          <div className="font-medium text-lg">{getDriver(selectedDelivery.driver_id)?.name}</div>
                          <div className="text-sm text-gray-400 capitalize">
                            {getDriver(selectedDelivery.driver_id)?.vehicle_type} • {getDriver(selectedDelivery.driver_id)?.vehicle_number}
                          </div>
                          <div className="flex items-center gap-1 mt-1">
                            {[1,2,3,4,5].map(star => (
                              <span key={star} className={`text-sm ${star <= (getDriver(selectedDelivery.driver_id)?.rating || 4) ? 'text-yellow-400' : 'text-gray-600'}`}>
                                ★
                              </span>
                            ))}
                          </div>
                        </div>
                        <Button variant="outline" size="sm" className="border-[#0050FF]/30 text-[#00D6FF]">
                          <Phone className="w-4 h-4 mr-1" />
                          Call
                        </Button>
                      </div>
                    </motion.div>
                  )}
                </div>
              </div>
            ) : (
              <div className="text-center py-16">
                <div className="w-20 h-20 rounded-full bg-white/5 flex items-center justify-center mx-auto mb-6">
                  <AlertCircle className="w-10 h-10 text-gray-500" />
                </div>
                <h3 className="text-xl font-semibold mb-2">No delivery found</h3>
                <p className="text-gray-400 mb-6">
                  We couldn't find a delivery with tracking ID "{searchQuery}"
                </p>
                <Link to={createPageUrl('CreateDelivery')}>
                  <Button className="bg-[#0050FF] hover:bg-[#0040DD]">
                    Create New Delivery
                  </Button>
                </Link>
              </div>
            )}
          </motion.div>
        )}

        {/* Recent Trackings */}
        {!hasSearched && deliveries.length > 0 && (
          <div className="mt-12">
            <h2 className="text-xl font-semibold mb-6">Recent Shipments</h2>
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {deliveries.slice(0, 6).map(delivery => {
                const st = statusConfig[delivery.status];
                const StIcon = st?.icon || Package;
                return (
                  <motion.button
                    key={delivery.id}
                    whileHover={{ scale: 1.02 }}
                    onClick={() => {
                      setSearchQuery(delivery.tracking_id);
                      setSelectedDelivery(delivery);
                      setHasSearched(true);
                    }}
                    className="p-4 rounded-xl bg-white/[0.02] border border-white/5 hover:border-white/10 text-left transition-all"
                  >
                    <div className="flex items-center justify-between mb-3">
                      <div className={`p-2 rounded-lg ${st?.color}`}>
                        <StIcon className="w-4 h-4" />
                      </div>
                      <span className="text-xs text-gray-500">
                        {delivery.created_date && format(new Date(delivery.created_date), 'MMM d')}
                      </span>
                    </div>
                    <div className="font-medium">{delivery.tracking_id}</div>
                    <div className="text-sm text-gray-500 mt-1">{delivery.receiver_name}</div>
                  </motion.button>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
