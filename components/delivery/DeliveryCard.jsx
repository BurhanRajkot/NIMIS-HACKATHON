import React from 'react';
import { motion } from 'framer-motion';
import {
  Package,
  MapPin,
  Clock,
  Truck,
  CheckCircle,
  AlertCircle,
  ArrowRight,
  User,
  Phone
} from 'lucide-react';
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { format } from 'date-fns';

const statusConfig = {
  pending: {
    label: 'Pending',
    color: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
    icon: Clock
  },
  picked_up: {
    label: 'Picked Up',
    color: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
    icon: Package
  },
  in_transit: {
    label: 'In Transit',
    color: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
    icon: Truck
  },
  out_for_delivery: {
    label: 'Out for Delivery',
    color: 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30',
    icon: Truck
  },
  delivered: {
    label: 'Delivered',
    color: 'bg-green-500/20 text-green-400 border-green-500/30',
    icon: CheckCircle
  },
  failed: {
    label: 'Failed',
    color: 'bg-red-500/20 text-red-400 border-red-500/30',
    icon: AlertCircle
  },
};

const priorityConfig = {
  standard: { label: 'Standard', color: 'bg-gray-500/20 text-gray-400' },
  express: { label: 'Express', color: 'bg-orange-500/20 text-orange-400' },
  same_day: { label: 'Same Day', color: 'bg-red-500/20 text-red-400' },
};

export default function DeliveryCard({
  delivery,
  onClick,
  showActions = true,
  compact = false
}) {
  const status = statusConfig[delivery.status] || statusConfig.pending;
  const priority = priorityConfig[delivery.priority] || priorityConfig.standard;
  const StatusIcon = status.icon;

  if (compact) {
    return (
      <motion.div
        whileHover={{ scale: 1.01 }}
        onClick={onClick}
        className="p-4 rounded-xl bg-white/[0.02] border border-white/5 hover:border-white/10 cursor-pointer transition-all"
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className={`p-2 rounded-lg ${status.color}`}>
              <StatusIcon className="w-4 h-4" />
            </div>
            <div>
              <div className="font-medium text-sm">{delivery.tracking_id}</div>
              <div className="text-xs text-gray-500">{delivery.receiver_name}</div>
            </div>
          </div>
          <Badge variant="outline" className={status.color}>
            {status.label}
          </Badge>
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div
      whileHover={{ scale: 1.005 }}
      className="p-6 rounded-2xl bg-gradient-to-br from-white/[0.03] to-transparent border border-white/5 hover:border-white/10 transition-all"
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className={`p-3 rounded-xl ${status.color}`}>
            <StatusIcon className="w-5 h-5" />
          </div>
          <div>
            <div className="font-semibold text-lg">{delivery.tracking_id}</div>
            <div className="text-sm text-gray-500">
              Created {delivery.created_date && format(new Date(delivery.created_date), 'MMM d, h:mm a')}
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="outline" className={priority.color}>
            {priority.label}
          </Badge>
          <Badge variant="outline" className={status.color}>
            {status.label}
          </Badge>
        </div>
      </div>

      {/* Route visualization */}
      <div className="relative pl-6 mb-6">
        <div className="absolute left-2 top-2 bottom-2 w-0.5 bg-gradient-to-b from-[#0050FF] to-[#00FF88]" />

        {/* Origin */}
        <div className="relative mb-4">
          <div className="absolute -left-4 top-1 w-3 h-3 rounded-full bg-[#0050FF] border-2 border-[#0A0A0C]" />
          <div className="ml-2">
            <div className="text-xs text-gray-500 mb-1">PICKUP</div>
            <div className="font-medium">{delivery.sender_name}</div>
            <div className="text-sm text-gray-400">{delivery.sender_address}</div>
            {delivery.sender_phone && (
              <div className="flex items-center gap-1 mt-1 text-xs text-gray-500">
                <Phone className="w-3 h-3" /> {delivery.sender_phone}
              </div>
            )}
          </div>
        </div>

        {/* Destination */}
        <div className="relative">
          <div className="absolute -left-4 top-1 w-3 h-3 rounded-full bg-[#00FF88] border-2 border-[#0A0A0C]" />
          <div className="ml-2">
            <div className="text-xs text-gray-500 mb-1">DELIVERY</div>
            <div className="font-medium">{delivery.receiver_name}</div>
            <div className="text-sm text-gray-400">{delivery.receiver_address}</div>
            {delivery.receiver_phone && (
              <div className="flex items-center gap-1 mt-1 text-xs text-gray-500">
                <Phone className="w-3 h-3" /> {delivery.receiver_phone}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Footer info */}
      <div className="flex items-center justify-between pt-4 border-t border-white/5">
        <div className="flex items-center gap-4 text-sm text-gray-400">
          {delivery.distance_km && (
            <span>{delivery.distance_km.toFixed(1)} km</span>
          )}
          {delivery.price && (
            <span className="font-medium text-white">₹{delivery.price}</span>
          )}
          {delivery.estimated_delivery && (
            <span>ETA: {format(new Date(delivery.estimated_delivery), 'MMM d, h:mm a')}</span>
          )}
        </div>

        {showActions && onClick && (
          <Button
            variant="ghost"
            size="sm"
            onClick={onClick}
            className="text-[#00D6FF] hover:text-white hover:bg-white/10"
          >
            View Details
            <ArrowRight className="w-4 h-4 ml-1" />
          </Button>
        )}
      </div>
    </motion.div>
  );
}
