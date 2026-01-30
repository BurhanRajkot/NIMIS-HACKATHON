import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { base44 } from '@/api/base44Client';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  MapPin,
  Sparkles,
  Loader2,
  CheckCircle,
  AlertCircle,
  Copy,
  History,
  Trash2,
  Brain,
  Navigation,
  Building2,
  Compass
} from 'lucide-react';
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import DeliveryMap from '../components/map/DeliveryMap';
import { toast } from "sonner";

export default function AddressResolver() {
  const queryClient = useQueryClient();
  const [rawAddress, setRawAddress] = useState('');
  const [city, setCity] = useState('');
  const [resolution, setResolution] = useState(null);
  const [isResolving, setIsResolving] = useState(false);

  const { data: recentResolutions = [] } = useQuery({
    queryKey: ['addressResolutions'],
    queryFn: () => base44.entities.AddressResolution.list('-created_date', 20),
  });

  const saveResolutionMutation = useMutation({
    mutationFn: (data) => base44.entities.AddressResolution.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['addressResolutions'] });
    }
  });

  const deleteResolutionMutation = useMutation({
    mutationFn: (id) => base44.entities.AddressResolution.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['addressResolutions'] });
    }
  });

  const resolveAddress = async () => {
    if (!rawAddress.trim()) return;

    setIsResolving(true);
    setResolution(null);

    try {
      const result = await base44.integrations.Core.InvokeLLM({
        prompt: `You are an expert Indian address resolution AI system. Analyze this unstructured Indian address and resolve it to coordinates.

Address: "${rawAddress}"
${city ? `City hint: ${city}` : ''}

Tasks:
1. Parse the address into components (landmark, locality, building, direction, pincode)
2. Identify Indian-specific elements (Hinglish terms, local landmarks)
3. Estimate GPS coordinates for this location
4. Provide confidence score (0-100) based on:
   - Address clarity and specificity
   - Landmark identifiability
   - Location uniqueness

Common Indian address patterns:
- "Near [landmark]" - proximity reference
- "Behind/Opposite [building]" - directional reference
- "[Gali/Lane] no [X]" - street reference
- "[Area] ke paas" - Hinglish proximity
- "Sector [X]" - planned city sectors

Return detailed parsed results.`,
        response_json_schema: {
          type: "object",
          properties: {
            parsed_components: {
              type: "object",
              properties: {
                landmark: { type: "string" },
                locality: { type: "string" },
                building: { type: "string" },
                direction: { type: "string" },
                pincode: { type: "string" },
                city: { type: "string" },
                state: { type: "string" }
              }
            },
            estimated_lat: { type: "number" },
            estimated_lng: { type: "number" },
            confidence_score: { type: "number" },
            formatted_address: { type: "string" },
            resolution_notes: { type: "string" },
            alternative_interpretations: {
              type: "array",
              items: { type: "string" }
            }
          }
        }
      });

      setResolution(result);

      // Save to database
      await saveResolutionMutation.mutateAsync({
        raw_address: rawAddress,
        parsed_landmark: result.parsed_components?.landmark || '',
        parsed_locality: result.parsed_components?.locality || '',
        parsed_city: result.parsed_components?.city || city,
        parsed_pincode: result.parsed_components?.pincode || '',
        resolved_lat: result.estimated_lat,
        resolved_lng: result.estimated_lng,
        confidence_score: result.confidence_score,
        resolution_method: 'ai_nlp',
        verified: false
      });

    } catch (error) {
      console.error('Resolution error:', error);
      toast.error('Failed to resolve address');
    } finally {
      setIsResolving(false);
    }
  };

  const copyCoordinates = () => {
    if (resolution?.estimated_lat && resolution?.estimated_lng) {
      navigator.clipboard.writeText(`${resolution.estimated_lat}, ${resolution.estimated_lng}`);
      toast.success('Coordinates copied!');
    }
  };

  const loadPreviousResolution = (res) => {
    setRawAddress(res.raw_address);
    setCity(res.parsed_city || '');
    setResolution({
      parsed_components: {
        landmark: res.parsed_landmark,
        locality: res.parsed_locality,
        city: res.parsed_city,
        pincode: res.parsed_pincode
      },
      estimated_lat: res.resolved_lat,
      estimated_lng: res.resolved_lng,
      confidence_score: res.confidence_score
    });
  };

  return (
    <div className="min-h-screen bg-[#050505] pt-20">
      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-[#0050FF]/20 border border-[#0050FF]/30 mb-6">
            <Brain className="w-4 h-4 text-[#00D6FF]" />
            <span className="text-sm text-[#00D6FF]">AI-Powered Address Intelligence</span>
          </div>
          <h1 className="text-3xl md:text-4xl font-bold mb-4">Address Resolver</h1>
          <p className="text-gray-400 max-w-2xl mx-auto">
            Convert unstructured Indian addresses into precise GPS coordinates using our AI engine
          </p>
        </div>

        <div className="grid lg:grid-cols-5 gap-8">
          {/* Input Section */}
          <div className="lg:col-span-2 space-y-6">
            <div className="p-6 rounded-2xl bg-gradient-to-br from-white/[0.03] to-transparent border border-white/5">
              <h3 className="font-semibold text-lg mb-4 flex items-center gap-2">
                <MapPin className="w-5 h-5 text-[#0050FF]" />
                Enter Address
              </h3>

              <div className="space-y-4">
                <div>
                  <Textarea
                    value={rawAddress}
                    onChange={(e) => setRawAddress(e.target.value)}
                    placeholder="Enter unstructured address...&#10;&#10;Examples:&#10;• Near old cinema, Sector 5&#10;• Piche wali gali, red building&#10;• Opposite chai wala, main road"
                    className="min-h-32 bg-white/5 border-white/10 resize-none"
                  />
                </div>

                <div>
                  <Input
                    value={city}
                    onChange={(e) => setCity(e.target.value)}
                    placeholder="City (optional)"
                    className="bg-white/5 border-white/10"
                  />
                </div>

                <Button
                  onClick={resolveAddress}
                  disabled={isResolving || !rawAddress.trim()}
                  className="w-full h-12 bg-gradient-to-r from-[#0050FF] to-[#00D6FF] hover:opacity-90"
                >
                  {isResolving ? (
                    <>
                      <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                      Resolving...
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-5 h-5 mr-2" />
                      Resolve Address
                    </>
                  )}
                </Button>
              </div>
            </div>

            {/* Recent Resolutions */}
            {recentResolutions.length > 0 && (
              <div className="p-6 rounded-2xl bg-gradient-to-br from-white/[0.03] to-transparent border border-white/5">
                <h3 className="font-semibold text-lg mb-4 flex items-center gap-2">
                  <History className="w-5 h-5 text-gray-500" />
                  Recent Resolutions
                </h3>
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {recentResolutions.slice(0, 10).map((res) => (
                    <div
                      key={res.id}
                      className="group flex items-center justify-between p-3 rounded-xl bg-white/5 hover:bg-white/10 cursor-pointer transition-all"
                      onClick={() => loadPreviousResolution(res)}
                    >
                      <div className="flex-1 min-w-0">
                        <div className="text-sm truncate">{res.raw_address}</div>
                        <div className="text-xs text-gray-500 flex items-center gap-2 mt-1">
                          <span className={res.confidence_score > 70 ? 'text-[#00FF88]' : res.confidence_score > 50 ? 'text-yellow-400' : 'text-red-400'}>
                            {res.confidence_score}%
                          </span>
                          {res.parsed_city && <span>• {res.parsed_city}</span>}
                        </div>
                      </div>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="opacity-0 group-hover:opacity-100 h-8 w-8"
                        onClick={(e) => {
                          e.stopPropagation();
                          deleteResolutionMutation.mutate(res.id);
                        }}
                      >
                        <Trash2 className="w-4 h-4 text-red-400" />
                      </Button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Results Section */}
          <div className="lg:col-span-3 space-y-6">
            <AnimatePresence mode="wait">
              {resolution ? (
                <motion.div
                  key="results"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  className="space-y-6"
                >
                  {/* Confidence Banner */}
                  <div className={`p-4 rounded-xl flex items-center justify-between ${
                    resolution.confidence_score > 80
                      ? 'bg-[#00FF88]/10 border border-[#00FF88]/30'
                      : resolution.confidence_score > 50
                      ? 'bg-yellow-500/10 border border-yellow-500/30'
                      : 'bg-red-500/10 border border-red-500/30'
                  }`}>
                    <div className="flex items-center gap-3">
                      {resolution.confidence_score > 80 ? (
                        <CheckCircle className="w-6 h-6 text-[#00FF88]" />
                      ) : resolution.confidence_score > 50 ? (
                        <AlertCircle className="w-6 h-6 text-yellow-400" />
                      ) : (
                        <AlertCircle className="w-6 h-6 text-red-400" />
                      )}
                      <div>
                        <div className="font-semibold">
                          {resolution.confidence_score > 80
                            ? 'High Confidence Resolution'
                            : resolution.confidence_score > 50
                            ? 'Moderate Confidence'
                            : 'Low Confidence - Needs Verification'}
                        </div>
                        <div className="text-sm text-gray-400">
                          AI Confidence Score: {resolution.confidence_score}%
                        </div>
                      </div>
                    </div>
                    <Badge variant="outline" className={
                      resolution.confidence_score > 80
                        ? 'border-[#00FF88] text-[#00FF88]'
                        : resolution.confidence_score > 50
                        ? 'border-yellow-400 text-yellow-400'
                        : 'border-red-400 text-red-400'
                    }>
                      {resolution.confidence_score}%
                    </Badge>
                  </div>

                  {/* Map */}
                  <div className="p-6 rounded-2xl bg-gradient-to-br from-white/[0.03] to-transparent border border-white/5">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="font-semibold text-lg">Resolved Location</h3>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={copyCoordinates}
                        className="border-white/10"
                      >
                        <Copy className="w-4 h-4 mr-1" />
                        Copy Coords
                      </Button>
                    </div>
                    <DeliveryMap
                      origin={{
                        lat: resolution.estimated_lat,
                        lng: resolution.estimated_lng,
                        address: resolution.formatted_address || rawAddress
                      }}
                      height="350px"
                    />
                    <div className="mt-4 p-3 rounded-xl bg-white/5 flex items-center justify-between">
                      <div className="text-sm text-gray-400">GPS Coordinates</div>
                      <div className="font-mono text-[#00D6FF]">
                        {resolution.estimated_lat?.toFixed(6)}, {resolution.estimated_lng?.toFixed(6)}
                      </div>
                    </div>
                  </div>

                  {/* Parsed Components */}
                  <div className="p-6 rounded-2xl bg-gradient-to-br from-white/[0.03] to-transparent border border-white/5">
                    <h3 className="font-semibold text-lg mb-4">Parsed Components</h3>
                    <div className="grid sm:grid-cols-2 gap-3">
                      {resolution.parsed_components?.landmark && (
                        <div className="p-3 rounded-xl bg-[#0050FF]/10 border border-[#0050FF]/30">
                          <div className="flex items-center gap-2 text-xs text-gray-500 mb-1">
                            <Navigation className="w-3 h-3" />
                            LANDMARK
                          </div>
                          <div className="font-medium text-[#00D6FF]">
                            {resolution.parsed_components.landmark}
                          </div>
                        </div>
                      )}
                      {resolution.parsed_components?.locality && (
                        <div className="p-3 rounded-xl bg-[#00FF88]/10 border border-[#00FF88]/30">
                          <div className="flex items-center gap-2 text-xs text-gray-500 mb-1">
                            <MapPin className="w-3 h-3" />
                            LOCALITY
                          </div>
                          <div className="font-medium text-[#00FF88]">
                            {resolution.parsed_components.locality}
                          </div>
                        </div>
                      )}
                      {resolution.parsed_components?.building && (
                        <div className="p-3 rounded-xl bg-[#FF9500]/10 border border-[#FF9500]/30">
                          <div className="flex items-center gap-2 text-xs text-gray-500 mb-1">
                            <Building2 className="w-3 h-3" />
                            BUILDING
                          </div>
                          <div className="font-medium text-[#FF9500]">
                            {resolution.parsed_components.building}
                          </div>
                        </div>
                      )}
                      {resolution.parsed_components?.direction && (
                        <div className="p-3 rounded-xl bg-purple-500/10 border border-purple-500/30">
                          <div className="flex items-center gap-2 text-xs text-gray-500 mb-1">
                            <Compass className="w-3 h-3" />
                            DIRECTION
                          </div>
                          <div className="font-medium text-purple-400">
                            {resolution.parsed_components.direction}
                          </div>
                        </div>
                      )}
                      {resolution.parsed_components?.city && (
                        <div className="p-3 rounded-xl bg-white/5 border border-white/10">
                          <div className="text-xs text-gray-500 mb-1">CITY</div>
                          <div className="font-medium">{resolution.parsed_components.city}</div>
                        </div>
                      )}
                      {resolution.parsed_components?.pincode && (
                        <div className="p-3 rounded-xl bg-white/5 border border-white/10">
                          <div className="text-xs text-gray-500 mb-1">PINCODE</div>
                          <div className="font-medium">{resolution.parsed_components.pincode}</div>
                        </div>
                      )}
                    </div>

                    {resolution.formatted_address && (
                      <div className="mt-4 p-4 rounded-xl bg-white/5">
                        <div className="text-xs text-gray-500 mb-2">FORMATTED ADDRESS</div>
                        <div className="text-lg">{resolution.formatted_address}</div>
                      </div>
                    )}

                    {resolution.resolution_notes && (
                      <div className="mt-4 p-3 rounded-lg bg-[#0050FF]/5 border border-[#0050FF]/20">
                        <div className="text-xs text-gray-500 mb-1">AI NOTES</div>
                        <div className="text-sm text-gray-300">{resolution.resolution_notes}</div>
                      </div>
                    )}
                  </div>
                </motion.div>
              ) : (
                <motion.div
                  key="placeholder"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="p-6 rounded-2xl bg-gradient-to-br from-white/[0.03] to-transparent border border-white/5 h-[600px] flex flex-col items-center justify-center text-center"
                >
                  <div className="w-20 h-20 rounded-full bg-[#0050FF]/10 flex items-center justify-center mb-6">
                    <MapPin className="w-10 h-10 text-[#0050FF]" />
                  </div>
                  <h3 className="text-xl font-semibold mb-2">Enter an address to resolve</h3>
                  <p className="text-gray-500 max-w-md">
                    Our AI will parse unstructured Indian addresses and convert them to precise GPS coordinates
                  </p>

                  <div className="mt-8 grid grid-cols-2 gap-4 text-left max-w-lg">
                    <div className="p-4 rounded-xl bg-white/5">
                      <div className="text-[#00FF88] font-medium mb-1">Landmark Detection</div>
                      <div className="text-sm text-gray-500">Identifies temples, schools, shops</div>
                    </div>
                    <div className="p-4 rounded-xl bg-white/5">
                      <div className="text-[#00D6FF] font-medium mb-1">Hinglish Support</div>
                      <div className="text-sm text-gray-500">Understands "ke paas", "wali gali"</div>
                    </div>
                    <div className="p-4 rounded-xl bg-white/5">
                      <div className="text-[#FF9500] font-medium mb-1">Direction Parsing</div>
                      <div className="text-sm text-gray-500">Near, behind, opposite</div>
                    </div>
                    <div className="p-4 rounded-xl bg-white/5">
                      <div className="text-purple-400 font-medium mb-1">Confidence Score</div>
                      <div className="text-sm text-gray-500">Reliability assessment</div>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>
    </div>
  );
}
