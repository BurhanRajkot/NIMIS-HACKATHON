import React from 'react';
import { motion } from 'framer-motion';

const tokenTypes = [
  { label: 'LANDMARK', color: '#0050FF', examples: ['old cinema', 'temple', 'petrol pump'] },
  { label: 'LOCALITY', color: '#00D6FF', examples: ['Sector 5', 'main road', 'market'] },
  { label: 'DIRECTION', color: '#00FF88', examples: ['behind', 'near', 'opposite'] },
  { label: 'BUILDING', color: '#FF9500', examples: ['yellow gate', 'red building', '2nd floor'] },
];

export default function AIParsingVisual({ progress }) {
  const isActive = progress > 0;

  return (
    <div className="absolute inset-0 flex items-center justify-center">
      <div className="relative w-full max-w-4xl px-6">
        {/* Central AI Engine */}
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={isActive ? { opacity: 1, scale: 1 } : {}}
          className="relative mx-auto w-48 h-48 sm:w-64 sm:h-64"
        >
          {/* Outer ring */}
          <motion.div
            animate={isActive ? { rotate: 360 } : {}}
            transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
            className="absolute inset-0 rounded-full border border-[#0050FF]/30"
          />

          {/* Middle ring */}
          <motion.div
            animate={isActive ? { rotate: -360 } : {}}
            transition={{ duration: 15, repeat: Infinity, ease: "linear" }}
            className="absolute inset-4 rounded-full border border-[#00D6FF]/30"
          />

          {/* Inner core */}
          <div className="absolute inset-8 rounded-full bg-gradient-to-br from-[#0050FF]/20 to-[#00D6FF]/20 backdrop-blur-xl border border-white/10 flex items-center justify-center">
            <motion.div
              animate={isActive ? {
                scale: [1, 1.1, 1],
                opacity: [0.5, 1, 0.5]
              } : {}}
              transition={{ duration: 2, repeat: Infinity }}
              className="text-center"
            >
              <div className="text-2xl sm:text-3xl font-bold text-gradient">NLP</div>
              <div className="text-xs text-gray-500 mt-1">Processing</div>
            </motion.div>
          </div>

          {/* Particle effects */}
          {isActive && [...Array(12)].map((_, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, scale: 0 }}
              animate={{
                opacity: [0, 1, 0],
                scale: [0, 1, 0],
                x: Math.cos(i * 30 * Math.PI / 180) * 100,
                y: Math.sin(i * 30 * Math.PI / 180) * 100,
              }}
              transition={{
                duration: 2,
                delay: i * 0.15,
                repeat: Infinity,
              }}
              className="absolute left-1/2 top-1/2 w-2 h-2 rounded-full bg-[#00D6FF]"
              style={{ marginLeft: -4, marginTop: -4 }}
            />
          ))}
        </motion.div>

        {/* Token Categories */}
        <div className="absolute inset-0 pointer-events-none">
          {tokenTypes.map((type, index) => {
            const angle = (index / tokenTypes.length) * 360;
            const radius = 180;
            const x = Math.cos((angle - 90) * Math.PI / 180) * radius;
            const y = Math.sin((angle - 90) * Math.PI / 180) * radius;

            return (
              <motion.div
                key={type.label}
                initial={{ opacity: 0, scale: 0 }}
                animate={isActive ? {
                  opacity: 1,
                  scale: 1,
                  x: x,
                  y: y
                } : {}}
                transition={{
                  duration: 0.8,
                  delay: 0.2 + index * 0.15,
                  type: "spring",
                  stiffness: 100
                }}
                className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 hidden sm:block"
              >
                <div
                  className="px-4 py-3 rounded-xl backdrop-blur-xl border"
                  style={{
                    borderColor: `${type.color}40`,
                    background: `linear-gradient(135deg, ${type.color}10, transparent)`,
                  }}
                >
                  <div
                    className="text-xs font-semibold mb-2"
                    style={{ color: type.color }}
                  >
                    {type.label}
                  </div>
                  <div className="space-y-1">
                    {type.examples.slice(0, 2).map((ex, i) => (
                      <motion.div
                        key={i}
                        initial={{ opacity: 0, x: -10 }}
                        animate={isActive ? { opacity: 1, x: 0 } : {}}
                        transition={{ delay: 0.5 + index * 0.1 + i * 0.1 }}
                        className="text-xs text-gray-400"
                      >
                        {ex}
                      </motion.div>
                    ))}
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>

        {/* Mobile Token Display */}
        <div className="sm:hidden grid grid-cols-2 gap-3 mt-8">
          {tokenTypes.map((type, index) => (
            <motion.div
              key={type.label}
              initial={{ opacity: 0, y: 20 }}
              animate={isActive ? { opacity: 1, y: 0 } : {}}
              transition={{ delay: 0.3 + index * 0.1 }}
              className="px-3 py-2 rounded-lg backdrop-blur-xl border"
              style={{
                borderColor: `${type.color}40`,
                background: `linear-gradient(135deg, ${type.color}10, transparent)`,
              }}
            >
              <div className="text-xs font-semibold" style={{ color: type.color }}>
                {type.label}
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}
