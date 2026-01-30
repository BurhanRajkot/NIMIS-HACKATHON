import React from 'react';
import { motion } from 'framer-motion';
import {
  Package,
  Truck,
  MapPin,
  CheckCircle,
  Clock,
  AlertCircle,
  Navigation
} from 'lucide-react';
import { format } from 'date-fns';

const statusSteps = [
  { key: 'pending', label: 'Order Placed', icon: Package },
  { key: 'picked_up', label: 'Picked Up', icon: Package },
  { key: 'in_transit', label: 'In Transit', icon: Truck },
  { key: 'out_for_delivery', label: 'Out for Delivery', icon: Navigation },
  { key: 'delivered', label: 'Delivered', icon: CheckCircle },
];

export default function TrackingTimeline({ delivery, updates = [] }) {
  const currentStatusIndex = statusSteps.findIndex(s => s.key === delivery.status);
  const isFailed = delivery.status === 'failed';

  return (
    <div className="relative">
      {/* Timeline */}
      <div className="space-y-0">
        {statusSteps.map((step, index) => {
          const isCompleted = index <= currentStatusIndex && !isFailed;
          const isCurrent = index === currentStatusIndex && !isFailed;
          const StepIcon = step.icon;

          // Find update for this step
          const update = updates.find(u => u.status === step.key);

          return (
            <div key={step.key} className="relative flex gap-4">
              {/* Connector line */}
              {index < statusSteps.length - 1 && (
                <div
                  className={`absolute left-5 top-10 w-0.5 h-full -ml-px ${
                    isCompleted && index < currentStatusIndex
                      ? 'bg-[#00FF88]'
                      : 'bg-white/10'
                  }`}
                />
              )}

              {/* Icon */}
              <motion.div
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ delay: index * 0.1 }}
                className={`relative z-10 flex items-center justify-center w-10 h-10 rounded-full border-2 ${
                  isCompleted
                    ? 'bg-[#00FF88]/20 border-[#00FF88] text-[#00FF88]'
                    : isCurrent
                    ? 'bg-[#0050FF]/20 border-[#0050FF] text-[#0050FF] animate-pulse'
                    : 'bg-white/5 border-white/10 text-gray-500'
                }`}
              >
                <StepIcon className="w-5 h-5" />
              </motion.div>

              {/* Content */}
              <div className="flex-1 pb-8">
                <div className={`font-medium ${isCompleted || isCurrent ? 'text-white' : 'text-gray-500'}`}>
                  {step.label}
                </div>
                {update && (
                  <div className="text-sm text-gray-400 mt-1">
                    {format(new Date(update.timestamp), 'MMM d, h:mm a')}
                  </div>
                )}
                {update?.location && (
                  <div className="text-sm text-gray-500 mt-1 flex items-center gap-1">
                    <MapPin className="w-3 h-3" /> {update.location}
                  </div>
                )}
                {isCurrent && !isFailed && (
                  <motion.div
                    initial={{ opacity: 0, y: 5 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mt-2 inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-[#0050FF]/20 border border-[#0050FF]/30 text-xs text-[#00D6FF]"
                  >
                    <span className="w-1.5 h-1.5 rounded-full bg-[#00D6FF] animate-pulse" />
                    Current Status
                  </motion.div>
                )}
              </div>
            </div>
          );
        })}

        {/* Failed status */}
        {isFailed && (
          <div className="relative flex gap-4">
            <div className="relative z-10 flex items-center justify-center w-10 h-10 rounded-full bg-red-500/20 border-2 border-red-500 text-red-500">
              <AlertCircle className="w-5 h-5" />
            </div>
            <div className="flex-1 pb-8">
              <div className="font-medium text-red-400">Delivery Failed</div>
              <div className="text-sm text-gray-400 mt-1">
                Please contact support for assistance
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
