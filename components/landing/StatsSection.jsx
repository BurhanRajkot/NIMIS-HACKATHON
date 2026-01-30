import React from 'react';
import { motion } from 'framer-motion';

const stats = [
  { value: '99.2%', label: 'Address Resolution', suffix: '' },
  { value: '50', label: 'API Latency', suffix: 'ms' },
  { value: '12M+', label: 'Addresses Processed', suffix: '' },
  { value: '500+', label: 'Cities Covered', suffix: '' },
];

export default function StatsSection() {
  return (
    <section className="py-16 lg:py-24 bg-[#0A0A0C]">
      <div className="max-w-7xl mx-auto px-6 lg:px-8">
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-8 lg:gap-12">
          {stats.map((stat, index) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.1 }}
              className="text-center"
            >
              <div className="text-3xl sm:text-4xl lg:text-5xl font-bold text-gradient">
                {stat.value}
                {stat.suffix && <span className="text-gray-500 text-xl">{stat.suffix}</span>}
              </div>
              <div className="mt-2 text-sm text-gray-400">{stat.label}</div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
