import React from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown } from 'lucide-react';

export default function StatsCard({
  title,
  value,
  change,
  changeType = 'positive',
  icon: Icon,
  color = '#0050FF',
  suffix = '',
  prefix = ''
}) {
  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      className="relative p-6 rounded-2xl bg-gradient-to-br from-white/[0.03] to-transparent border border-white/5 overflow-hidden"
    >
      {/* Background accent */}
      <div
        className="absolute -top-10 -right-10 w-32 h-32 rounded-full opacity-10"
        style={{ background: `radial-gradient(circle, ${color}, transparent)` }}
      />

      <div className="relative">
        <div className="flex items-start justify-between mb-4">
          <div
            className="p-3 rounded-xl"
            style={{
              background: `linear-gradient(135deg, ${color}20, transparent)`,
              border: `1px solid ${color}30`
            }}
          >
            <Icon className="w-5 h-5" style={{ color }} />
          </div>

          {change && (
            <div className={`flex items-center gap-1 text-sm ${
              changeType === 'positive' ? 'text-[#00FF88]' : 'text-red-400'
            }`}>
              {changeType === 'positive' ? (
                <TrendingUp className="w-4 h-4" />
              ) : (
                <TrendingDown className="w-4 h-4" />
              )}
              {change}
            </div>
          )}
        </div>

        <div className="text-3xl font-bold">
          {prefix}{typeof value === 'number' ? value.toLocaleString() : value}{suffix}
        </div>
        <div className="text-sm text-gray-400 mt-1">{title}</div>
      </div>
    </motion.div>
  );
}
