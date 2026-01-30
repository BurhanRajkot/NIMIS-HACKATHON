import React from 'react';
import { motion } from 'framer-motion';

export default function PredictionVisual({ progress }) {
  const isActive = progress > 0;

  // Vector points that will converge
  const points = [...Array(20)].map((_, i) => ({
    id: i,
    startX: Math.random() * 100,
    startY: Math.random() * 100,
    endX: 50 + (Math.random() - 0.5) * 10,
    endY: 50 + (Math.random() - 0.5) * 10,
    delay: i * 0.05,
  }));

  return (
    <div className="absolute inset-0 flex items-center justify-center">
      <div className="relative w-full max-w-3xl aspect-square">
        {/* Vector space background */}
        <div className="absolute inset-0 opacity-20">
          <svg className="w-full h-full" viewBox="0 0 100 100">
            {/* Grid lines */}
            {[...Array(10)].map((_, i) => (
              <React.Fragment key={i}>
                <motion.line
                  x1={i * 10} y1="0" x2={i * 10} y2="100"
                  stroke="#0050FF"
                  strokeWidth="0.2"
                  initial={{ opacity: 0 }}
                  animate={isActive ? { opacity: 0.3 } : {}}
                  transition={{ delay: i * 0.05 }}
                />
                <motion.line
                  x1="0" y1={i * 10} x2="100" y2={i * 10}
                  stroke="#0050FF"
                  strokeWidth="0.2"
                  initial={{ opacity: 0 }}
                  animate={isActive ? { opacity: 0.3 } : {}}
                  transition={{ delay: i * 0.05 }}
                />
              </React.Fragment>
            ))}
          </svg>
        </div>

        {/* Converging vectors */}
        <svg className="absolute inset-0 w-full h-full" viewBox="0 0 100 100">
          {points.map((point) => (
            <React.Fragment key={point.id}>
              {/* Trail line */}
              <motion.line
                x1={point.startX}
                y1={point.startY}
                x2={point.startX}
                y2={point.startY}
                stroke="#00D6FF"
                strokeWidth="0.3"
                strokeOpacity="0.5"
                initial={{ x2: point.startX, y2: point.startY }}
                animate={isActive ? { x2: point.endX, y2: point.endY } : {}}
                transition={{ duration: 1.5, delay: point.delay, ease: "easeInOut" }}
              />

              {/* Moving point */}
              <motion.circle
                r="1"
                fill="#00D6FF"
                initial={{ cx: point.startX, cy: point.startY, opacity: 0 }}
                animate={isActive ? {
                  cx: point.endX,
                  cy: point.endY,
                  opacity: [0, 1, 1],
                } : {}}
                transition={{ duration: 1.5, delay: point.delay, ease: "easeInOut" }}
              />
            </React.Fragment>
          ))}

          {/* Central prediction point */}
          <motion.circle
            cx="50"
            cy="50"
            r="0"
            fill="#00FF88"
            initial={{ r: 0, opacity: 0 }}
            animate={isActive ? { r: 3, opacity: 1 } : {}}
            transition={{ duration: 0.5, delay: 1.5 }}
          />

          {/* Confidence rings */}
          {[1, 2, 3].map((ring) => (
            <motion.circle
              key={ring}
              cx="50"
              cy="50"
              r={ring * 8}
              fill="none"
              stroke="#00FF88"
              strokeWidth="0.3"
              initial={{ opacity: 0, scale: 0 }}
              animate={isActive ? {
                opacity: [0, 0.5, 0.2],
                scale: 1,
              } : {}}
              transition={{
                duration: 1,
                delay: 1.5 + ring * 0.2,
              }}
              style={{ transformOrigin: '50px 50px' }}
            />
          ))}
        </svg>

        {/* Confidence indicator */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={isActive ? { opacity: 1, y: 0 } : {}}
          transition={{ delay: 2 }}
          className="absolute bottom-8 left-1/2 -translate-x-1/2 glass-panel rounded-xl px-6 py-4"
        >
          <div className="flex items-center gap-4">
            <div>
              <div className="text-xs text-gray-500 mb-1">Confidence Score</div>
              <div className="text-2xl font-bold text-[#00FF88]">97.3%</div>
            </div>
            <div className="w-px h-10 bg-white/10" />
            <div>
              <div className="text-xs text-gray-500 mb-1">Resolution</div>
              <div className="text-2xl font-bold text-[#00D6FF]">±2m</div>
            </div>
          </div>
        </motion.div>

        {/* Similarity vectors label */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={isActive ? { opacity: 1, x: 0 } : {}}
          transition={{ delay: 0.5 }}
          className="absolute left-4 top-1/2 -translate-y-1/2 hidden lg:block"
        >
          <div className="glass-panel rounded-lg px-4 py-3">
            <div className="text-xs text-gray-500 mb-2">Vector Similarity</div>
            <div className="space-y-2">
              {['0.94', '0.89', '0.87'].map((score, i) => (
                <div key={i} className="flex items-center gap-2">
                  <div className="w-16 h-1.5 rounded-full bg-white/10 overflow-hidden">
                    <motion.div
                      className="h-full bg-[#0050FF]"
                      initial={{ width: 0 }}
                      animate={isActive ? { width: `${parseFloat(score) * 100}%` } : {}}
                      transition={{ delay: 1 + i * 0.2, duration: 0.8 }}
                    />
                  </div>
                  <span className="text-xs text-gray-400">{score}</span>
                </div>
              ))}
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
