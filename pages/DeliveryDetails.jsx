import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createPageUrl } from '../utils';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { base44 } from '@/api/base44Client';
import { motion } from 'framer-motion';
import {
  ArrowLeft,
  Package,
  MapPin,
  Clock,
  Truck,
  CheckCircle,
  AlertCircle,
  Phone,
  User,
  Edit,
  Trash2,
  Share2,
  Copy,
  Navigation,
  Calendar,
  DollarSign
} from 'lucide-react';
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import DeliveryMap from '../components/map/DeliveryMap';
import TrackingTimeline from '../components/delivery/TrackingTimeline';
import { format } from 'date-fns';
import { toast } from "sonner";

const statusConfig = {
  pending: { label: 'Pending', color: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30', icon: Clock },
  picked_up: { label: 'Picked Up', color: 'bg-blue-500/20 text-blue-400 border-blue-500/30', icon: Package },
  in_transit: { label: 'In Transit', color: 'bg-purple-500/20 text-purple-400 border-purple-500/30', icon: Truck },
  out_for_delivery: { label: 'Out for Delivery', color: 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30', icon: Navigation },
  delivered: { label: 'Delivered', color: 'bg-green-500/20 text-green-400 border-green-500/30', icon: CheckCircle },
  failed: { label: 'Failed', color: 'bg-red-500/20 text-red-400 border-red-500/30', icon: AlertCircle },
};

export default function DeliveryDetails() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const urlParams = new URLSearchParams(window.location.search);
  const deliveryId = urlParams.get('id');

  const { data: delivery, isLoading, error } = useQuery({
    queryKey: ['delivery', deliveryId],
    queryFn: () => base44.entities.Delivery.list().then(deliveries => deliveries.find(d => d.id === deliveryId)),
    enabled: !!deliveryId,
  });

  const { data: drivers = [] } = useQuery({
    queryKey: ['drivers'],
    queryFn: () => base44.entities.Driver.list(),
  });

  const updateMutation = useMutation({
    mutationFn: (data) => base44.entities.Delivery.update(deliveryId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['delivery', deliveryId] });
      toast.success('Delivery updated');
    }
  });

  const deleteMutation = useMutation({
    mutationFn: () => base44.entities.Delivery.delete(deliveryId),
    onSuccess: () => {
      navigate(createPageUrl('Deliveries'));
      toast.success('Delivery deleted');
    }
  });

  const copyTrackingLink = () => {
    const url = window.location.origin + createPageUrl(`Tracking?tracking_id=${delivery.tracking_id}`);
    navigator.clipboard.writeText(url);
    toast.success('Tracking link copied!');
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#050505] pt-20 flex items-center justify-center">
        <div className="animate-pulse text-gray-400">Loading...</div>
      </div>
    );
  }

  if (!delivery || error) {
    return (
      <div className="min-h-screen bg-[#050505] pt-20">
        <div className="max-w-7xl mx-auto px-6 py-8 text-center">
          <Package className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <h2 className="text-2xl font-bold mb-2">Delivery not found</h2>
          <p className="text-gray-400 mb-6">The delivery you're looking for doesn't exist.</p>
          <Button onClick={() => navigate(createPageUrl('Deliveries'))}>
            View All Deliveries
          </Button>
        </div>
      </div>
    );
  }

  const status = statusConfig[delivery.status] || statusConfig.pending;
  const StatusIcon = status.icon;
  const driver = drivers.find(d => d.id === delivery.driver_id);

  // Generate tracking updates based on status
  const trackingUpdates = [
    { status: 'pending', timestamp: delivery.created_date, location: 'Order received' },
    delivery.status !== 'pending' && { status: 'picked_up', timestamp: new Date(new Date(delivery.created_date).getTime() + 2 * 60 * 60 * 1000).toISOString(), location: delivery.sender_address },
    ['in_transit', 'out_for_delivery', 'delivered'].includes(delivery.status) && { status: 'in_transit', timestamp: new Date(new Date(delivery.created_date).getTime() + 4 * 60 * 60 * 1000).toISOString(), location: 'Distribution center' },
    ['out_for_delivery', 'delivered'].includes(delivery.status) && { status: 'out_for_delivery', timestamp: new Date(new Date(delivery.created_date).getTime() + 6 * 60 * 60 * 1000).toISOString(), location: 'Out for delivery' },
    delivery.status === 'delivered' && { status: 'delivered', timestamp: delivery.actual_delivery || new Date().toISOString(), location: delivery.receiver_address },
  ].filter(Boolean);

  return (
    <div className="min-h-screen bg-[#050505] pt-20">
      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-4 mb-8">
          <div>
            <Button
              variant="ghost"
              onClick={() => navigate(-1)}
              className="mb-4 text-gray-400 hover:text-white"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back
            </Button>
            <div className="flex items-center gap-4">
              <div className={`p-4 rounded-2xl ${status.color}`}>
                <StatusIcon className="w-8 h-8" />
              </div>
              <div>
                <div className="text-sm text-gray-500">Tracking ID</div>
                <h1 className="text-2xl font-bold">{delivery.tracking_id}</h1>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <Button
              variant="outline"
              size="sm"
              onClick={copyTrackingLink}
              className="border-white/10"
            >
              <Share2 className="w-4 h-4 mr-2" />
              Share
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                if (confirm('Delete this delivery?')) {
                  deleteMutation.mutate();
                }
              }}
              className="border-red-500/30 text-red-400 hover:bg-red-500/10"
            >
              <Trash2 className="w-4 h-4 mr-2" />
              Delete
            </Button>
          </div>
        </div>

        <div className="grid lg:grid-cols-3 gap-6">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Status Card */}
            <div className="p-6 rounded-2xl bg-gradient-to-br from-white/[0.03] to-transparent border border-white/5">
              <div className="flex items-center justify-between mb-6">
                <h3 className="font-semibold text-lg">Delivery Status</h3>
                <Select
                  value={delivery.status}
                  onValueChange={(status) => updateMutation.mutate({ status })}
                >
                  <SelectTrigger className="w-48 bg-white/5 border-white/10">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="pending">Pending</SelectItem>
                    <SelectItem value="picked_up">Picked Up</SelectItem>
                    <SelectItem value="in_transit">In Transit</SelectItem>
                    <SelectItem value="out_for_delivery">Out for Delivery</SelectItem>
                    <SelectItem value="delivered">Delivered</SelectItem>
                    <SelectItem value="failed">Failed</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-4 rounded-xl bg-white/5">
                  <div className="text-xs text-gray-500 mb-1">Status</div>
                  <Badge variant="outline" className={status.color}>{status.label}</Badge>
                </div>
                <div className="p-4 rounded-xl bg-white/5">
                  <div className="text-xs text-gray-500 mb-1">Priority</div>
                  <div className="font-medium capitalize">{delivery.priority?.replace('_', ' ') || 'Standard'}</div>
                </div>
                <div className="p-4 rounded-xl bg-white/5">
                  <div className="text-xs text-gray-500 mb-1">Distance</div>
                  <div className="font-medium">{delivery.distance_km?.toFixed(1) || '--'} km</div>
                </div>
                <div className="p-4 rounded-xl bg-white/5">
                  <div className="text-xs text-gray-500 mb-1">Price</div>
                  <div className="font-medium text-[#00D6FF]">₹{delivery.price || '--'}</div>
                </div>
              </div>
            </div>

            {/* Route Details */}
            <div className="p-6 rounded-2xl bg-gradient-to-br from-white/[0.03] to-transparent border border-white/5">
              <h3 className="font-semibold text-lg mb-6">Route Details</h3>

              <div className="grid md:grid-cols-2 gap-6">
                {/* Sender */}
                <div className="p-4 rounded-xl bg-[#0050FF]/5 border border-[#0050FF]/20">
                  <div className="flex items-center gap-2 mb-3">
                    <div className="w-8 h-8 rounded-full bg-[#0050FF]/20 flex items-center justify-center">
                      <User className="w-4 h-4 text-[#0050FF]" />
                    </div>
                    <span className="text-xs text-gray-500 uppercase">Pickup</span>
                  </div>
                  <div className="font-semibold text-lg mb-1">{delivery.sender_name}</div>
                  <div className="text-sm text-gray-400 mb-2">{delivery.sender_address}</div>
                  {delivery.sender_phone && (
                    <a href={`tel:${delivery.sender_phone}`} className="inline-flex items-center gap-1 text-sm text-[#00D6FF] hover:underline">
                      <Phone className="w-3 h-3" /> {delivery.sender_phone}
                    </a>
                  )}
                </div>

                {/* Receiver */}
                <div className="p-4 rounded-xl bg-[#00FF88]/5 border border-[#00FF88]/20">
                  <div className="flex items-center gap-2 mb-3">
                    <div className="w-8 h-8 rounded-full bg-[#00FF88]/20 flex items-center justify-center">
                      <MapPin className="w-4 h-4 text-[#00FF88]" />
                    </div>
                    <span className="text-xs text-gray-500 uppercase">Delivery</span>
                  </div>
                  <div className="font-semibold text-lg mb-1">{delivery.receiver_name}</div>
                  <div className="text-sm text-gray-400 mb-2">{delivery.receiver_address}</div>
                  {delivery.receiver_phone && (
                    <a href={`tel:${delivery.receiver_phone}`} className="inline-flex items-center gap-1 text-sm text-[#00D6FF] hover:underline">
                      <Phone className="w-3 h-3" /> {delivery.receiver_phone}
                    </a>
                  )}
                </div>
              </div>

              {/* Map */}
              <div className="mt-6">
                <DeliveryMap
                  origin={delivery.sender_lat && delivery.sender_lng ? {
                    lat: delivery.sender_lat,
                    lng: delivery.sender_lng,
                    address: delivery.sender_address
                  } : null}
                  destination={delivery.receiver_lat && delivery.receiver_lng ? {
                    lat: delivery.receiver_lat,
                    lng: delivery.receiver_lng,
                    address: delivery.receiver_address
                  } : null}
                  driverLocation={delivery.current_lat && delivery.current_lng ? {
                    lat: delivery.current_lat,
                    lng: delivery.current_lng
                  } : null}
                  height="350px"
                />
              </div>
            </div>

            {/* Package Details */}
            <div className="p-6 rounded-2xl bg-gradient-to-br from-white/[0.03] to-transparent border border-white/5">
              <h3 className="font-semibold text-lg mb-4">Package Details</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <div className="text-xs text-gray-500 mb-1">Type</div>
                  <div className="font-medium capitalize">{delivery.package_type?.replace('_', ' ') || 'Parcel'}</div>
                </div>
                <div>
                  <div className="text-xs text-gray-500 mb-1">Weight</div>
                  <div className="font-medium">{delivery.package_weight || '--'} kg</div>
                </div>
                <div>
                  <div className="text-xs text-gray-500 mb-1">Created</div>
                  <div className="font-medium">
                    {delivery.created_date && format(new Date(delivery.created_date), 'MMM d, h:mm a')}
                  </div>
                </div>
                <div>
                  <div className="text-xs text-gray-500 mb-1">ETA</div>
                  <div className="font-medium">
                    {delivery.estimated_delivery
                      ? format(new Date(delivery.estimated_delivery), 'MMM d, h:mm a')
                      : '--'}
                  </div>
                </div>
              </div>

              {delivery.notes && (
                <div className="mt-4 p-4 rounded-xl bg-white/5">
                  <div className="text-xs text-gray-500 mb-1">Special Instructions</div>
                  <div className="text-sm">{delivery.notes}</div>
                </div>
              )}
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Timeline */}
            <div className="p-6 rounded-2xl bg-gradient-to-br from-white/[0.03] to-transparent border border-white/5">
              <h3 className="font-semibold text-lg mb-6">Tracking Timeline</h3>
              <TrackingTimeline delivery={delivery} updates={trackingUpdates} />
            </div>

            {/* Driver Assignment */}
            <div className="p-6 rounded-2xl bg-gradient-to-br from-white/[0.03] to-transparent border border-white/5">
              <h3 className="font-semibold text-lg mb-4">Driver Assignment</h3>

              <Select
                value={delivery.driver_id || ''}
                onValueChange={(driver_id) => updateMutation.mutate({ driver_id })}
              >
                <SelectTrigger className="w-full bg-white/5 border-white/10">
                  <SelectValue placeholder="Assign driver" />
                </SelectTrigger>
                <SelectContent>
                  {drivers.map(d => (
                    <SelectItem key={d.id} value={d.id}>
                      {d.name} ({d.vehicle_type})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              {driver && (
                <div className="mt-4 p-4 rounded-xl bg-white/5">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-full bg-[#0050FF]/20 flex items-center justify-center">
                      <Truck className="w-6 h-6 text-[#0050FF]" />
                    </div>
                    <div className="flex-1">
                      <div className="font-medium">{driver.name}</div>
                      <div className="text-sm text-gray-400 capitalize">
                        {driver.vehicle_type} • {driver.vehicle_number}
                      </div>
                    </div>
                  </div>
                  {driver.phone && (
                    <a
                      href={`tel:${driver.phone}`}
                      className="mt-3 flex items-center justify-center gap-2 p-2 rounded-lg bg-[#0050FF]/20 text-[#00D6FF] text-sm"
                    >
                      <Phone className="w-4 h-4" />
                      Call Driver
                    </a>
                  )}
                </div>
              )}
            </div>

            {/* Quick Actions */}
            <div className="p-6 rounded-2xl bg-gradient-to-br from-white/[0.03] to-transparent border border-white/5">
              <h3 className="font-semibold text-lg mb-4">Quick Actions</h3>
              <div className="space-y-2">
                {delivery.status !== 'delivered' && (
                  <Button
                    className="w-full justify-start bg-[#00FF88]/20 text-[#00FF88] hover:bg-[#00FF88]/30"
                    onClick={() => updateMutation.mutate({ status: 'delivered' })}
                  >
                    <CheckCircle className="w-4 h-4 mr-2" />
                    Mark as Delivered
                  </Button>
                )}
                {delivery.status !== 'failed' && delivery.status !== 'delivered' && (
                  <Button
                    variant="outline"
                    className="w-full justify-start border-red-500/30 text-red-400 hover:bg-red-500/10"
                    onClick={() => updateMutation.mutate({ status: 'failed' })}
                  >
                    <AlertCircle className="w-4 h-4 mr-2" />
                    Mark as Failed
                  </Button>
                )}
                <Button
                  variant="outline"
                  className="w-full justify-start border-white/10"
                  onClick={copyTrackingLink}
                >
                  <Copy className="w-4 h-4 mr-2" />
                  Copy Tracking Link
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
