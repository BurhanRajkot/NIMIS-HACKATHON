import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MapPin, Loader2, CheckCircle, AlertCircle, Search, Navigation, Sparkles } from 'lucide-react';
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { base44 } from '@/api/base44Client';

export default function AddressInput({
  label,
  placeholder = "Enter address...",
  value,
  onChange,
  onCoordinatesResolved,
  className = "",
  icon: Icon = MapPin,
  accentColor = "#0050FF"
}) {
  const [isResolving, setIsResolving] = useState(false);
  const [resolution, setResolution] = useState(null);
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const inputRef = useRef(null);
  const debounceRef = useRef(null);

  // Sample Indian addresses for suggestions
  const sampleAddresses = [
    "Near old cinema, Sector 5, Lucknow",
    "Behind petrol pump, MG Road, Kanpur",
    "Opposite chai wala, main road, Varanasi",
    "Gali no 3, red building, Allahabad",
    "Temple ke samne, Sadar Bazaar, Jaipur",
    "Purani sabzi mandi wali gali, Agra",
    "Near government school gate, Noida Sector 62",
    "Yellow gate behind temple, Ghaziabad"
  ];

  const resolveAddress = async (address) => {
    if (!address || address.length < 5) return;

    setIsResolving(true);

    try {
      // Use LLM to parse and resolve the address
      const result = await base44.integrations.Core.InvokeLLM({
        prompt: `You are an Indian address resolution AI. Parse this unstructured Indian address and extract coordinates.

Address: "${address}"

Instructions:
1. Identify landmarks, localities, directions, and areas
2. Estimate approximate GPS coordinates for this location in India
3. Provide a confidence score (0-100) based on address clarity

Respond in JSON format only.`,
        response_json_schema: {
          type: "object",
          properties: {
            parsed_landmark: { type: "string" },
            parsed_locality: { type: "string" },
            parsed_city: { type: "string" },
            estimated_lat: { type: "number" },
            estimated_lng: { type: "number" },
            confidence: { type: "number" },
            formatted_address: { type: "string" }
          }
        }
      });

      setResolution({
        ...result,
        success: result.confidence > 50
      });

      if (result.estimated_lat && result.estimated_lng && onCoordinatesResolved) {
        onCoordinatesResolved({
          lat: result.estimated_lat,
          lng: result.estimated_lng,
          confidence: result.confidence,
          formatted: result.formatted_address
        });
      }
    } catch (error) {
      console.error('Address resolution error:', error);
      setResolution({
        success: false,
        error: 'Could not resolve address'
      });
    } finally {
      setIsResolving(false);
    }
  };

  const handleInputChange = (e) => {
    const newValue = e.target.value;
    onChange(newValue);
    setResolution(null);

    // Show suggestions
    if (newValue.length > 2) {
      const filtered = sampleAddresses.filter(addr =>
        addr.toLowerCase().includes(newValue.toLowerCase())
      );
      setSuggestions(filtered.slice(0, 4));
      setShowSuggestions(true);
    } else {
      setShowSuggestions(false);
    }

    // Debounced resolution
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      if (newValue.length >= 10) {
        resolveAddress(newValue);
      }
    }, 1500);
  };

  const selectSuggestion = (suggestion) => {
    onChange(suggestion);
    setShowSuggestions(false);
    resolveAddress(suggestion);
  };

  const getCurrentLocation = () => {
    if (navigator.geolocation) {
      setIsResolving(true);
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const { latitude, longitude } = position.coords;
          onChange("Current Location");
          setResolution({
            success: true,
            confidence: 100,
            formatted_address: "Current GPS Location"
          });
          if (onCoordinatesResolved) {
            onCoordinatesResolved({
              lat: latitude,
              lng: longitude,
              confidence: 100,
              formatted: "Current Location"
            });
          }
          setIsResolving(false);
        },
        (error) => {
          console.error('Geolocation error:', error);
          setIsResolving(false);
        }
      );
    }
  };

  return (
    <div className={`relative ${className}`}>
      {label && (
        <label className="block text-sm font-medium text-gray-300 mb-2">
          {label}
        </label>
      )}

      <div className="relative">
        <Icon
          className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500"
          style={{ color: resolution?.success ? '#00FF88' : undefined }}
        />

        <Input
          ref={inputRef}
          value={value}
          onChange={handleInputChange}
          placeholder={placeholder}
          className="pl-12 pr-24 h-14 bg-white/5 border-white/10 focus:border-[#0050FF] rounded-xl text-white placeholder:text-gray-500"
          onFocus={() => value.length > 2 && setShowSuggestions(true)}
          onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
        />

        <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-1">
          {isResolving ? (
            <div className="p-2">
              <Loader2 className="w-5 h-5 animate-spin text-[#0050FF]" />
            </div>
          ) : resolution ? (
            <div className="p-2">
              {resolution.success ? (
                <CheckCircle className="w-5 h-5 text-[#00FF88]" />
              ) : (
                <AlertCircle className="w-5 h-5 text-yellow-500" />
              )}
            </div>
          ) : null}

          <Button
            type="button"
            variant="ghost"
            size="icon"
            onClick={getCurrentLocation}
            className="h-10 w-10 hover:bg-white/10"
          >
            <Navigation className="w-4 h-4 text-gray-400" />
          </Button>
        </div>
      </div>

      {/* AI Resolution feedback */}
      <AnimatePresence>
        {resolution && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="mt-2"
          >
            {resolution.success ? (
              <div className="flex items-center gap-2 text-sm">
                <Sparkles className="w-4 h-4 text-[#00D6FF]" />
                <span className="text-gray-400">
                  AI Confidence: <span className="text-[#00FF88] font-medium">{resolution.confidence}%</span>
                </span>
                {resolution.parsed_city && (
                  <span className="text-gray-500">• {resolution.parsed_city}</span>
                )}
              </div>
            ) : (
              <div className="text-sm text-yellow-500">
                Please provide more details for accurate resolution
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Suggestions dropdown */}
      <AnimatePresence>
        {showSuggestions && suggestions.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="absolute z-50 w-full mt-2 bg-[#0A0A0C] border border-white/10 rounded-xl overflow-hidden shadow-2xl"
          >
            {suggestions.map((suggestion, idx) => (
              <button
                key={idx}
                onClick={() => selectSuggestion(suggestion)}
                className="w-full px-4 py-3 text-left text-sm text-gray-300 hover:bg-white/5 flex items-center gap-3 transition-colors"
              >
                <MapPin className="w-4 h-4 text-gray-500" />
                {suggestion}
              </button>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
