import React from 'react';
import { motion } from 'framer-motion';

export default function DeliveryOptimizationVisual({ progress }) {
  const isActive = progress > 0;

  // Delivery points
  const deliveryPoints = [
    { x: 20, y: 30 },
    { x: 35, y: 45 },
    { x: 28, y: 60 },
    { x: 45, y: 35 },
    { x: 55, y: 55 },
    { x: 70, y: 40 },
    { x: 65, y: 65 },
    { x: 80, y: 50 },
  ];

  // Hub position
  const hub = { x: 50, y: 80 };

  // Optimized route order
  const optimizedOrder = [0, 3, 5, 7, 6, 4, 2, 1];

  return (
    <div className="absolute inset-0 flex items-center justify-center">
      <div className="relative w-full max-w-4xl aspect-video">
        {/* Map background */}
        <div className="absolute inset-0 rounded-2xl overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-[#0A0A0C] to-[#050505]" />

          {/* Street grid pattern */}
          <svg className="absolute inset-0 w-full h-full opacity-10" viewBox="0 0 100 100">
            {[...Array(20)].map((_, i) => (
              <React.Fragment key={i}>
                <line
                  x1={i * 5} y1="0" x2={i * 5} y2="100"
                  stroke="#fff"
                  strokeWidth="0.2"
                />
                <line
                  x1="0" y1={i * 5} x2="100" y2={i * 5}
                  stroke="#fff"
                  strokeWidth="0.2"
                />
              </React.Fragment>
            ))}
          </svg>
        </div>

        {/* Route paths */}
        <svg className="absolute inset-0 w-full h-full" viewBox="0 0 100 100">
          {/* Old inefficient routes (fade out) */}
          {deliveryPoints.map((point, i) => (
            <motion.line
              key={`old-${i}`}
              x1={hub.x}
              y1={hub.y}
              x2={point.x}
              y2={point.y}
              stroke="#FF4444"
              strokeWidth="0.5"
              strokeDasharray="2,2"
              initial={{ opacity: 0.5 }}
              animate={isActive ? { opacity: 0 } : {}}
              transition={{ duration: 1, delay: i * 0.1 }}
            />
          ))}

          {/* Optimized route */}
          <motion.path
            d={createOptimizedPath(hub, deliveryPoints, optimizedOrder)}
            fill="none"
            stroke="#00FF88"
            strokeWidth="1"
            strokeLinecap="round"
            initial={{ pathLength: 0, opacity: 0 }}
            animate={isActive ? { pathLength: 1, opacity: 1 } : {}}
            transition={{ duration: 2, delay: 0.5, ease: "easeInOut" }}
          />

          {/* Moving delivery vehicle */}
          <motion.circle
            r="2"
            fill="#00FF88"
            initial={{ opacity: 0 }}
            animate={isActive ? {
              opacity: 1,
              offsetDistance: ['0%', '100%'],
            } : {}}
            transition={{
              duration: 4,
              delay: 1,
              repeat: Infinity,
              ease: "linear"
            }}
            style={{
              offsetPath: `path("${createOptimizedPath(hub, deliveryPoints, optimizedOrder)}")`,
            }}
          >
            <animate
              attributeName="r"
              values="2;3;2"
              dur="0.5s"
              repeatCount="indefinite"
            />
          </motion.circle>
        </svg>

        {/* Hub marker */}
        <motion.div
          initial={{ opacity: 0, scale: 0 }}
          animate={isActive ? { opacity: 1, scale: 1 } : {}}
          className="absolute"
          style={{ left: `${hub.x}%`, top: `${hub.y}%`, transform: 'translate(-50%, -50%)' }}
        >
          <div className="w-6 h-6 rounded-full bg-white flex items-center justify-center">
            <div className="w-3 h-3 rounded-full bg-[#0050FF]" />
          </div>
          <div className="absolute -bottom-6 left-1/2 -translate-x-1/2 text-xs text-gray-400 whitespace-nowrap">
            Distribution Hub
          </div>
        </motion.div>

        {/* Delivery points */}
        {deliveryPoints.map((point, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, scale: 0 }}
            animate={isActive ? {
              opacity: 1,
              scale: 1,
            } : {}}
            transition={{ delay: 0.8 + i * 0.1 }}
            className="absolute"
            style={{ left: `${point.x}%`, top: `${point.y}%`, transform: 'translate(-50%, -50%)' }}
          >
            <motion.div
              initial={{ backgroundColor: 'rgba(255, 68, 68, 0.5)' }}
              animate={isActive ? { backgroundColor: 'rgba(0, 255, 136, 0.8)' } : {}}
              transition={{ delay: 1 + i * 0.2 }}
              className="w-3 h-3 rounded-full"
              style={{
                boxShadow: '0 0 10px currentColor',
              }}
            />
          </motion.div>
        ))}

        {/* Stats panel */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={isActive ? { opacity: 1, y: 0 } : {}}
          transition={{ delay: 1.5 }}
          className="absolute bottom-4 right-4 glass-panel rounded-xl p-4"
        >
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <motion.div
                initial={{ opacity: 0 }}
                animate={isActive ? { opacity: 1 } : {}}
                className="text-lg font-bold text-[#00FF88]"
              >
                -32%
              </motion.div>
              <div className="text-xs text-gray-500">Distance</div>
            </div>
            <div>
              <motion.div
                initial={{ opacity: 0 }}
                animate={isActive ? { opacity: 1 } : {}}
                transition={{ delay: 0.2 }}
                className="text-lg font-bold text-[#00D6FF]"
              >
                +45%
              </motion.div>
              <div className="text-xs text-gray-500">Deliveries</div>
            </div>
            <div>
              <motion.div
                initial={{ opacity: 0 }}
                animate={isActive ? { opacity: 1 } : {}}
                transition={{ delay: 0.4 }}
                className="text-lg font-bold text-white"
              >
                0
              </motion.div>
              <div className="text-xs text-gray-500">Failed</div>
            </div>
          </div>
        </motion.div>

        {/* Before/After toggle */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={isActive ? { opacity: 1, x: 0 } : {}}
          transition={{ delay: 1 }}
          className="absolute top-4 left-4 glass-panel rounded-lg px-3 py-2"
        >
          <div className="flex items-center gap-3 text-xs">
            <span className="text-red-400 line-through opacity-50">Before</span>
            <span className="text-[#00FF88] font-medium">Optimized</span>
          </div>
        </motion.div>
      </div>
    </div>
  );
}

function createOptimizedPath(hub, points, order) {
  let path = `M ${hub.x} ${hub.y}`;
  order.forEach(idx => {
    path += ` L ${points[idx].x} ${points[idx].y}`;
  });
  path += ` L ${hub.x} ${hub.y}`;
  return path;
}
