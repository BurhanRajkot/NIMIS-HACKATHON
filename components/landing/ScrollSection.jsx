import React from 'react';
import { motion } from 'framer-motion';

export default function ScrollSection({
  title,
  subtitle,
  isActive,
  alignment = 'left',
  children
}) {
  return (
    <div className="absolute inset-0 flex items-center pointer-events-none">
      <div className={`w-full max-w-7xl mx-auto px-6 lg:px-8 ${
        alignment === 'center' ? 'text-center' : ''
      }`}>
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={isActive ? { opacity: 1, y: 0 } : { opacity: 0, y: 40 }}
          transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
          className={`max-w-xl ${alignment === 'center' ? 'mx-auto' : ''} ${
            alignment === 'right' ? 'ml-auto' : ''
          }`}
        >
          <h2 className="text-3xl sm:text-4xl lg:text-5xl xl:text-6xl font-bold leading-tight tracking-tight">
            {title}
          </h2>
          {subtitle && (
            <p className="mt-4 lg:mt-6 text-lg sm:text-xl text-gray-400 leading-relaxed">
              {subtitle}
            </p>
          )}
          {children}
        </motion.div>
      </div>
    </div>
  );
}
