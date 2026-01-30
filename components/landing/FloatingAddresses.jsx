import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';

const chaosAddresses = [
  "Near old cinema, Sector 5",
  "Yellow gate behind temple",
  "Piche wali gali, near neem tree",
  "Opposite chai wala, main road",
  "Behind petrol pump, 2nd floor",
  "Near Sharma ji ka ghar",
  "Gali no 3, red building",
  "Tiraha ke paas",
  "Purani sabzi mandi wali gali",
  "Near government school gate",
  "Temple ke samne",
  "Nala ke peeche",
  "Gurudwara road, blue house",
  "Market ke andar",
];

export default function FloatingAddresses({ isActive }) {
  const [addresses, setAddresses] = useState([]);

  useEffect(() => {
    const generated = chaosAddresses.map((text, i) => ({
      id: i,
      text,
      x: Math.random() * 80 + 10,
      y: Math.random() * 60 + 20,
      rotation: Math.random() * 20 - 10,
      delay: Math.random() * 2,
      duration: 3 + Math.random() * 4,
    }));
    setAddresses(generated);
  }, []);

  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      {addresses.map((addr) => (
        <motion.div
          key={addr.id}
          initial={{ opacity: 0, scale: 0.8 }}
          animate={isActive ? {
            opacity: [0.3, 0.7, 0.3],
            scale: [0.9, 1, 0.9],
            x: [0, Math.random() * 40 - 20, 0],
            y: [0, Math.random() * 30 - 15, 0],
          } : { opacity: 0 }}
          transition={{
            duration: addr.duration,
            delay: addr.delay,
            repeat: Infinity,
            ease: "easeInOut"
          }}
          className="absolute px-4 py-2 rounded-lg bg-white/5 border border-white/10 backdrop-blur-sm"
          style={{
            left: `${addr.x}%`,
            top: `${addr.y}%`,
            transform: `rotate(${addr.rotation}deg)`,
          }}
        >
          <span className="text-xs sm:text-sm text-gray-400 whitespace-nowrap">{addr.text}</span>
        </motion.div>
      ))}

      {/* Failed delivery indicators */}
      {isActive && [1, 2, 3, 4, 5].map((i) => (
        <motion.div
          key={`fail-${i}`}
          initial={{ opacity: 0, scale: 0 }}
          animate={{
            opacity: [0, 1, 0],
            scale: [0.5, 1, 0.5],
          }}
          transition={{
            duration: 2,
            delay: i * 0.8,
            repeat: Infinity,
          }}
          className="absolute w-3 h-3 rounded-full bg-red-500/80"
          style={{
            left: `${20 + i * 15}%`,
            top: `${30 + (i % 3) * 20}%`,
            boxShadow: '0 0 20px rgba(255, 68, 68, 0.5)',
          }}
        />
      ))}
    </div>
  );
}
