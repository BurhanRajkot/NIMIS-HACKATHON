import React from 'react';
import { motion } from 'framer-motion';
import {
  Brain,
  MapPin,
  BarChart3,
  Fingerprint,
  Truck,
  Code2,
  ArrowRight
} from 'lucide-react';

const features = [
  {
    icon: Brain,
    title: 'AI Parsing Engine',
    description: 'NLP trained specifically for Indian addresses. Understands Hinglish, landmarks, and local navigation patterns.',
    color: '#0050FF',
  },
  {
    icon: MapPin,
    title: 'Spatial Intelligence',
    description: 'H3 hexagonal grid clustering with density heatmaps. Every delivery trains the system.',
    color: '#00D6FF',
  },
  {
    icon: BarChart3,
    title: 'Confidence Scoring',
    description: 'Real-time prediction confidence with ±2m resolution accuracy for precise deliveries.',
    color: '#00FF88',
  },
  {
    icon: Fingerprint,
    title: 'DIGIPIN Compatible',
    description: 'Seamless integration with India\'s digital addressing infrastructure.',
    color: '#FF9500',
  },
  {
    icon: Truck,
    title: 'Driver Assist',
    description: 'Turn-by-turn guidance with landmark-based navigation for last-mile efficiency.',
    color: '#FF2D55',
  },
  {
    icon: Code2,
    title: 'API Integration',
    description: 'RESTful APIs with SDKs for Python, Node.js, and mobile. 50ms average latency.',
    color: '#BF5AF2',
  },
];

export default function FeaturesSection() {
  return (
    <section id="platform" className="py-24 lg:py-32 bg-[#050505]">
      <div className="max-w-7xl mx-auto px-6 lg:px-8">
        {/* Section header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16 lg:mb-24"
        >
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 mb-6">
            <span className="w-2 h-2 rounded-full bg-[#00FF88] animate-pulse" />
            <span className="text-sm text-gray-400">Platform Capabilities</span>
          </div>
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold tracking-tight">
            Enterprise-grade
            <span className="text-gradient"> AI infrastructure</span>
          </h2>
          <p className="mt-4 text-lg text-gray-400 max-w-2xl mx-auto">
            Built for scale. Designed for India's unique addressing challenges.
          </p>
        </motion.div>

        {/* Features grid */}
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6 lg:gap-8">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.1 }}
              className="group relative"
            >
              <div className="h-full p-6 lg:p-8 rounded-2xl bg-gradient-to-br from-white/[0.03] to-transparent border border-white/5 hover:border-white/10 transition-all duration-300">
                {/* Icon */}
                <div
                  className="w-12 h-12 rounded-xl flex items-center justify-center mb-6"
                  style={{
                    background: `linear-gradient(135deg, ${feature.color}20, transparent)`,
                    border: `1px solid ${feature.color}30`,
                  }}
                >
                  <feature.icon
                    className="w-6 h-6"
                    style={{ color: feature.color }}
                  />
                </div>

                {/* Content */}
                <h3 className="text-xl font-semibold mb-3">{feature.title}</h3>
                <p className="text-gray-400 leading-relaxed">{feature.description}</p>

                {/* Hover arrow */}
                <div className="mt-6 flex items-center gap-2 text-sm font-medium opacity-0 group-hover:opacity-100 transition-opacity" style={{ color: feature.color }}>
                  <span>Learn more</span>
                  <ArrowRight className="w-4 h-4" />
                </div>

                {/* Corner glow on hover */}
                <div
                  className="absolute -top-px -right-px w-24 h-24 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none"
                  style={{
                    background: `radial-gradient(circle at top right, ${feature.color}20, transparent 70%)`,
                  }}
                />
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
