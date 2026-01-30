import React from 'react';
import { motion } from 'framer-motion';

export default function SpatialGridVisual({ progress }) {
  const isActive = progress > 0;

  // Generate hexagonal grid positions
  const hexagons = [];
  const rows = 8;
  const cols = 12;

  for (let row = 0; row < rows; row++) {
    for (let col = 0; col < cols; col++) {
      const offset = row % 2 === 0 ? 0 : 25;
      hexagons.push({
        id: `${row}-${col}`,
        x: col * 50 + offset,
        y: row * 45,
        intensity: Math.random(),
        delay: (row + col) * 0.02,
      });
    }
  }

  // Cluster centers (hotspots)
  const clusters = [
    { x: 30, y: 25, intensity: 1 },
    { x: 60, y: 40, intensity: 0.8 },
    { x: 45, y: 60, intensity: 0.9 },
    { x: 75, y: 30, intensity: 0.7 },
  ];

  return (
    <div className="absolute inset-0 flex items-center justify-center overflow-hidden">
      <div className="relative w-full h-full">
        {/* H3 Hexagonal Grid */}
        <svg className="absolute inset-0 w-full h-full opacity-40" viewBox="0 0 600 400">
          <defs>
            <radialGradient id="clusterGlow" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="#0050FF" stopOpacity="0.8" />
              <stop offset="100%" stopColor="#0050FF" stopOpacity="0" />
            </radialGradient>
          </defs>

          {hexagons.map((hex) => {
            // Calculate proximity to nearest cluster
            let maxProximity = 0;
            clusters.forEach(cluster => {
              const dist = Math.sqrt(
                Math.pow((hex.x / 6) - cluster.x, 2) +
                Math.pow((hex.y / 4) - cluster.y, 2)
              );
              const proximity = Math.max(0, 1 - dist / 30) * cluster.intensity;
              maxProximity = Math.max(maxProximity, proximity);
            });

            return (
              <motion.polygon
                key={hex.id}
                initial={{ opacity: 0, scale: 0 }}
                animate={isActive ? {
                  opacity: 0.1 + maxProximity * 0.7,
                  scale: 1
                } : {}}
                transition={{
                  duration: 0.5,
                  delay: hex.delay
                }}
                points={getHexPoints(hex.x + 300, hex.y + 50, 20)}
                fill={maxProximity > 0.3 ? '#0050FF' : '#1a1a1a'}
                stroke="#0050FF"
                strokeWidth="0.5"
                strokeOpacity={0.3 + maxProximity * 0.5}
              />
            );
          })}
        </svg>

        {/* Cluster indicators */}
        {clusters.map((cluster, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, scale: 0 }}
            animate={isActive ? {
              opacity: [0.3, 0.8, 0.3],
              scale: [0.8, 1.2, 0.8],
            } : {}}
            transition={{
              duration: 3,
              delay: i * 0.3,
              repeat: Infinity,
            }}
            className="absolute rounded-full"
            style={{
              left: `${cluster.x}%`,
              top: `${cluster.y}%`,
              width: 60 * cluster.intensity,
              height: 60 * cluster.intensity,
              background: `radial-gradient(circle, rgba(0, 80, 255, 0.4) 0%, transparent 70%)`,
              transform: 'translate(-50%, -50%)',
            }}
          />
        ))}

        {/* Delivery pins forming clusters */}
        {isActive && clusters.map((cluster, ci) => (
          [...Array(5)].map((_, i) => {
            const angle = (i / 5) * Math.PI * 2;
            const radius = 30 + Math.random() * 20;
            return (
              <motion.div
                key={`pin-${ci}-${i}`}
                initial={{ opacity: 0, scale: 0, y: 20 }}
                animate={{
                  opacity: 1,
                  scale: 1,
                  y: 0,
                }}
                transition={{
                  duration: 0.5,
                  delay: 0.5 + ci * 0.2 + i * 0.1,
                }}
                className="absolute"
                style={{
                  left: `calc(${cluster.x}% + ${Math.cos(angle) * radius}px)`,
                  top: `calc(${cluster.y}% + ${Math.sin(angle) * radius}px)`,
                }}
              >
                <div className="w-2 h-2 rounded-full bg-[#00D6FF]" style={{
                  boxShadow: '0 0 10px rgba(0, 214, 255, 0.5)'
                }} />
              </motion.div>
            );
          })
        ))}

        {/* Stats panel */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={isActive ? { opacity: 1, x: 0 } : {}}
          transition={{ delay: 0.8 }}
          className="absolute right-4 top-1/2 -translate-y-1/2 glass-panel rounded-xl p-4 hidden lg:block"
        >
          <div className="text-xs text-gray-500 mb-3">Cluster Analytics</div>
          <div className="space-y-3">
            <div>
              <div className="text-[#00D6FF] text-lg font-bold">4,847</div>
              <div className="text-xs text-gray-500">Active clusters</div>
            </div>
            <div>
              <div className="text-[#00FF88] text-lg font-bold">98.2%</div>
              <div className="text-xs text-gray-500">Coverage</div>
            </div>
            <div>
              <div className="text-white text-lg font-bold">12M+</div>
              <div className="text-xs text-gray-500">Deliveries mapped</div>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}

function getHexPoints(cx, cy, r) {
  const points = [];
  for (let i = 0; i < 6; i++) {
    const angle = (i * 60 - 30) * Math.PI / 180;
    points.push(`${cx + r * Math.cos(angle)},${cy + r * Math.sin(angle)}`);
  }
  return points.join(' ');
}
