import React from 'react';
import { motion } from 'framer-motion';

export default function IndiaMapVisual({ progress }) {
  const isActive = progress > 0;

  // Major cities/regions
  const cities = [
    { name: 'Delhi NCR', x: 48, y: 25 },
    { name: 'Mumbai', x: 35, y: 50 },
    { name: 'Bangalore', x: 42, y: 72 },
    { name: 'Chennai', x: 52, y: 75 },
    { name: 'Kolkata', x: 65, y: 40 },
    { name: 'Hyderabad', x: 47, y: 58 },
    { name: 'Pune', x: 38, y: 55 },
    { name: 'Jaipur', x: 40, y: 30 },
    { name: 'Lucknow', x: 55, y: 30 },
    { name: 'Ahmedabad', x: 30, y: 40 },
  ];

  return (
    <div className="absolute inset-0 flex items-center justify-center">
      <div className="relative w-full max-w-2xl aspect-[3/4]">
        {/* Simplified India outline */}
        <svg className="absolute inset-0 w-full h-full" viewBox="0 0 100 120">
          <defs>
            <linearGradient id="mapGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#0050FF" stopOpacity="0.3" />
              <stop offset="100%" stopColor="#00D6FF" stopOpacity="0.1" />
            </linearGradient>
            <filter id="glow">
              <feGaussianBlur stdDeviation="2" result="coloredBlur" />
              <feMerge>
                <feMergeNode in="coloredBlur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>

          {/* India shape (simplified) */}
          <motion.path
            d="M50 5 L75 15 L85 25 L80 45 L75 55 L70 70 L55 90 L50 100 L45 95 L35 80 L25 65 L20 50 L25 35 L30 20 L40 10 Z"
            fill="url(#mapGradient)"
            stroke="#0050FF"
            strokeWidth="0.5"
            initial={{ pathLength: 0, opacity: 0 }}
            animate={isActive ? { pathLength: 1, opacity: 1 } : {}}
            transition={{ duration: 2, ease: "easeInOut" }}
            filter="url(#glow)"
          />

          {/* Network connections */}
          {isActive && cities.map((city, i) => (
            cities.slice(i + 1).map((target, j) => {
              if (Math.random() > 0.6) return null;
              return (
                <motion.line
                  key={`${i}-${j}`}
                  x1={city.x}
                  y1={city.y}
                  x2={target.x}
                  y2={target.y}
                  stroke="#00D6FF"
                  strokeWidth="0.3"
                  strokeOpacity="0.3"
                  initial={{ pathLength: 0 }}
                  animate={{ pathLength: 1 }}
                  transition={{ duration: 1, delay: 1 + (i + j) * 0.1 }}
                />
              );
            })
          ))}
        </svg>

        {/* City nodes */}
        {cities.map((city, i) => (
          <motion.div
            key={city.name}
            initial={{ opacity: 0, scale: 0 }}
            animate={isActive ? {
              opacity: 1,
              scale: 1,
            } : {}}
            transition={{ delay: 0.5 + i * 0.1, type: "spring" }}
            className="absolute group"
            style={{
              left: `${city.x}%`,
              top: `${city.y}%`,
              transform: 'translate(-50%, -50%)',
            }}
          >
            {/* Pulse ring */}
            <motion.div
              animate={isActive ? {
                scale: [1, 2, 1],
                opacity: [0.5, 0, 0.5],
              } : {}}
              transition={{
                duration: 2,
                delay: i * 0.2,
                repeat: Infinity,
              }}
              className="absolute inset-0 w-4 h-4 rounded-full bg-[#00FF88]/30 -translate-x-1/2 -translate-y-1/2"
              style={{ left: '50%', top: '50%' }}
            />

            {/* Point */}
            <div
              className="w-3 h-3 rounded-full bg-[#00FF88]"
              style={{ boxShadow: '0 0 15px rgba(0, 255, 136, 0.6)' }}
            />

            {/* Label */}
            <div className="absolute left-1/2 -translate-x-1/2 top-5 opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
              <div className="text-xs text-white font-medium px-2 py-1 rounded bg-black/50 backdrop-blur-sm">
                {city.name}
              </div>
            </div>
          </motion.div>
        ))}

        {/* Stats overlay */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={isActive ? { opacity: 1, y: 0 } : {}}
          transition={{ delay: 2 }}
          className="absolute bottom-0 left-1/2 -translate-x-1/2 w-full max-w-md"
        >
          <div className="glass-panel rounded-2xl p-6">
            <div className="text-center mb-4">
              <motion.div
                initial={{ scale: 0 }}
                animate={isActive ? { scale: 1 } : {}}
                transition={{ delay: 2.2, type: "spring" }}
                className="text-4xl font-bold text-gradient"
              >
                500+ Cities
              </motion.div>
              <div className="text-sm text-gray-400 mt-1">Tier 2 & Tier 3 coverage</div>
            </div>

            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <div className="text-xl font-bold text-white">12M+</div>
                <div className="text-xs text-gray-500">Addresses</div>
              </div>
              <div>
                <div className="text-xl font-bold text-[#00FF88]">99.2%</div>
                <div className="text-xs text-gray-500">Accuracy</div>
              </div>
              <div>
                <div className="text-xl font-bold text-[#00D6FF]">50ms</div>
                <div className="text-xs text-gray-500">Latency</div>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
