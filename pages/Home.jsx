import React, { useEffect, useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowDown, Play } from 'lucide-react';
import { Button } from "@/components/ui/button";

import FloatingAddresses from '../components/landing/FloatingAddresses';
import AIParsingVisual from '../components/landing/AIParsingVisual';
import SpatialGridVisual from '../components/landing/SpatialGridVisual';
import PredictionVisual from '../components/landing/PredictionVisual';
import DeliveryOptimizationVisual from '../components/landing/DeliveryOptimizationVisual';
import IndiaMapVisual from '../components/landing/IndiaMapVisual';
import ScrollSection from '../components/landing/ScrollSection';
import FeaturesSection from '../components/landing/FeaturesSection';
import CTASection from '../components/landing/CTASection';
import StatsSection from '../components/landing/StatsSection';
import TechStackSection from '../components/landing/TechStackSection';

const sections = [
  {
    id: 'chaos',
    title: "India's last mile is broken.",
    subtitle: "Addresses here are not locations. They are stories.",
    range: [0, 0.15],
  },
  {
    id: 'parsing',
    title: "AI trained for Indian addresses.",
    subtitle: "Understands Hinglish, landmarks, and local navigation patterns.",
    range: [0.15, 0.35],
  },
  {
    id: 'spatial',
    title: "Millions of deliveries become intelligence.",
    subtitle: "Every successful drop trains the system.",
    range: [0.35, 0.55],
  },
  {
    id: 'prediction',
    title: "Prediction, not search.",
    subtitle: "Addresses resolve through learned similarity.",
    range: [0.55, 0.75],
  },
  {
    id: 'optimization',
    title: "More deliveries. Less friction.",
    subtitle: "Optimized routes increase drop density.",
    range: [0.75, 0.90],
  },
  {
    id: 'future',
    title: "Solve the last mile.",
    subtitle: "Smart Address Intelligence.",
    range: [0.90, 1],
  },
];

export default function Home() {
  const [scrollProgress, setScrollProgress] = useState(0);
  const [currentSection, setCurrentSection] = useState(0);
  const containerRef = useRef(null);
  const [showScrollHint, setShowScrollHint] = useState(true);

  useEffect(() => {
    const handleScroll = () => {
      if (!containerRef.current) return;

      const container = containerRef.current;
      const scrollTop = window.scrollY - container.offsetTop;
      const scrollHeight = container.offsetHeight - window.innerHeight;
      const progress = Math.max(0, Math.min(1, scrollTop / scrollHeight));

      setScrollProgress(progress);

      // Find current section
      const sectionIndex = sections.findIndex(
        s => progress >= s.range[0] && progress < s.range[1]
      );
      if (sectionIndex !== -1) {
        setCurrentSection(sectionIndex);
      }

      if (progress > 0.05) {
        setShowScrollHint(false);
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const getSectionProgress = (sectionId) => {
    const section = sections.find(s => s.id === sectionId);
    if (!section) return 0;

    const [start, end] = section.range;
    if (scrollProgress < start) return 0;
    if (scrollProgress > end) return 1;
    return (scrollProgress - start) / (end - start);
  };

  const isSectionActive = (sectionId) => {
    const section = sections.find(s => s.id === sectionId);
    if (!section) return false;
    return scrollProgress >= section.range[0] && scrollProgress < section.range[1];
  };

  return (
    <div className="bg-[#050505]">
      {/* Hero Section */}
      <section className="relative h-screen flex items-center justify-center overflow-hidden">
        {/* Background grid */}
        <div className="absolute inset-0 hex-grid opacity-50" />

        {/* Radial gradient overlay */}
        <div
          className="absolute inset-0"
          style={{
            background: 'radial-gradient(ellipse at center, transparent 0%, #050505 70%)',
          }}
        />

        {/* Content */}
        <div className="relative z-10 text-center max-w-5xl mx-auto px-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 mb-8">
              <span className="w-2 h-2 rounded-full bg-[#00FF88] animate-pulse" />
              <span className="text-sm text-gray-400">Now serving 500+ cities across India</span>
            </div>
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.1 }}
            className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold tracking-tight leading-[1.1]"
          >
            Intelligent address
            <br />
            <span className="text-gradient">resolution for India</span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="mt-6 text-lg sm:text-xl text-gray-400 max-w-2xl mx-auto leading-relaxed"
          >
            AI-powered platform solving unstructured address challenges and last-mile delivery inefficiencies in Tier 2 & Tier 3 cities.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.3 }}
            className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4"
          >
            <Button
              size="lg"
              className="h-14 px-8 bg-white text-[#050505] hover:bg-gray-100 rounded-full font-medium text-base"
              onClick={() => document.getElementById('demo')?.scrollIntoView({ behavior: 'smooth' })}
            >
              Request Demo
            </Button>
            <Button
              size="lg"
              variant="outline"
              className="h-14 px-8 border-white/20 text-white hover:bg-white/5 rounded-full font-medium text-base"
            >
              <Play className="w-5 h-5 mr-2" />
              Watch Demo
            </Button>
          </motion.div>
        </div>

        {/* Scroll hint */}
        <AnimatePresence>
          {showScrollHint && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="absolute bottom-8 left-1/2 -translate-x-1/2"
            >
              <motion.div
                animate={{ y: [0, 10, 0] }}
                transition={{ duration: 2, repeat: Infinity }}
                className="flex flex-col items-center gap-2 text-gray-500"
              >
                <span className="text-xs">Scroll to explore</span>
                <ArrowDown className="w-5 h-5" />
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </section>

      {/* Scroll-driven storytelling section */}
      <section
        ref={containerRef}
        className="relative"
        style={{ height: '500vh' }}
      >
        {/* Sticky canvas */}
        <div className="sticky top-0 h-screen overflow-hidden">
          {/* Progress bar */}
          <div className="absolute top-0 left-0 right-0 h-1 bg-white/5 z-50">
            <motion.div
              className="h-full bg-gradient-to-r from-[#0050FF] to-[#00D6FF]"
              style={{ width: `${scrollProgress * 100}%` }}
            />
          </div>

          {/* Section indicators */}
          <div className="absolute right-6 top-1/2 -translate-y-1/2 z-50 hidden lg:flex flex-col gap-3">
            {sections.map((section, index) => (
              <div
                key={section.id}
                className={`w-2 h-2 rounded-full transition-all duration-300 ${
                  currentSection === index
                    ? 'bg-[#00D6FF] scale-125'
                    : 'bg-white/20'
                }`}
              />
            ))}
          </div>

          {/* Background gradient */}
          <div
            className="absolute inset-0 transition-opacity duration-1000"
            style={{
              background: `radial-gradient(ellipse at center, rgba(0, 80, 255, ${0.05 + scrollProgress * 0.1}) 0%, transparent 60%)`,
            }}
          />

          {/* Visual layers */}
          <div className="absolute inset-0">
            {/* Section 1: Address Chaos */}
            <motion.div
              className="absolute inset-0"
              animate={{ opacity: isSectionActive('chaos') ? 1 : 0 }}
              transition={{ duration: 0.5 }}
            >
              <FloatingAddresses isActive={isSectionActive('chaos')} />
            </motion.div>

            {/* Section 2: AI Parsing */}
            <motion.div
              className="absolute inset-0"
              animate={{ opacity: isSectionActive('parsing') ? 1 : 0 }}
              transition={{ duration: 0.5 }}
            >
              <AIParsingVisual progress={getSectionProgress('parsing')} />
            </motion.div>

            {/* Section 3: Spatial Intelligence */}
            <motion.div
              className="absolute inset-0"
              animate={{ opacity: isSectionActive('spatial') ? 1 : 0 }}
              transition={{ duration: 0.5 }}
            >
              <SpatialGridVisual progress={getSectionProgress('spatial')} />
            </motion.div>

            {/* Section 4: Location Prediction */}
            <motion.div
              className="absolute inset-0"
              animate={{ opacity: isSectionActive('prediction') ? 1 : 0 }}
              transition={{ duration: 0.5 }}
            >
              <PredictionVisual progress={getSectionProgress('prediction')} />
            </motion.div>

            {/* Section 5: Delivery Optimization */}
            <motion.div
              className="absolute inset-0"
              animate={{ opacity: isSectionActive('optimization') ? 1 : 0 }}
              transition={{ duration: 0.5 }}
            >
              <DeliveryOptimizationVisual progress={getSectionProgress('optimization')} />
            </motion.div>

            {/* Section 6: Future Vision */}
            <motion.div
              className="absolute inset-0"
              animate={{ opacity: isSectionActive('future') ? 1 : 0 }}
              transition={{ duration: 0.5 }}
            >
              <IndiaMapVisual progress={getSectionProgress('future')} />
            </motion.div>
          </div>

          {/* Text overlays */}
          {sections.map((section) => (
            <ScrollSection
              key={section.id}
              title={section.title}
              subtitle={section.subtitle}
              isActive={isSectionActive(section.id)}
              alignment={section.id === 'future' ? 'center' : 'left'}
            >
              {section.id === 'future' && isSectionActive('future') && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.5 }}
                  className="mt-8 pointer-events-auto"
                >
                  <Button
                    size="lg"
                    className="h-14 px-8 bg-white text-[#050505] hover:bg-gray-100 rounded-full font-medium"
                    onClick={() => document.getElementById('demo')?.scrollIntoView({ behavior: 'smooth' })}
                  >
                    Request Enterprise Demo
                  </Button>
                </motion.div>
              )}
            </ScrollSection>
          ))}
        </div>
      </section>

      {/* Stats Section */}
      <StatsSection />

      {/* Features Section */}
      <FeaturesSection />

      {/* Tech Stack Section */}
      <TechStackSection />

      {/* CTA Section */}
      <CTASection />
    </div>
  );
}
