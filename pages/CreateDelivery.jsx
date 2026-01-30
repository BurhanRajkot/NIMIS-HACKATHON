import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { createPageUrl } from '../utils';
import { motion } from 'framer-motion';
import { base44 } from '@/api/base44Client';
import {
  Package,
  MapPin,
  User,
  Phone,
  FileText,
  ArrowRight,
  ArrowLeft,
  Loader2,
  CheckCircle,
  Sparkles,
  Truck,
  Clock,
  Zap
} from 'lucide-react';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import AddressInput from '../components/delivery/AddressInput';
import DeliveryMap from '../components/map/DeliveryMap';

const steps = [
  { id: 'sender', label: 'Pickup Details', icon: User },
  { id: 'receiver', label: 'Delivery Details', icon: MapPin },
  { id: 'package', label: 'Package Info', icon: Package },
  { id: 'confirm', label: 'Confirm', icon: CheckCircle },
];

export default function CreateDelivery() {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(0);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [estimatedPrice, setEstimatedPrice] = useState(null);
  const [estimatedDistance, setEstimatedDistance] = useState(null);

  const [formData, setFormData] = useState({
    // Sender
    sender_name: '',
    sender_phone: '',
    sender_address: '',
    sender_lat: null,
    sender_lng: null,
    // Receiver
    receiver_name: '',
    receiver_phone: '',
    receiver_address: '',
    receiver_lat: null,
    receiver_lng: null,
    // Package
    package_type: 'small_parcel',
    package_weight: '',
    priority: 'standard',
    notes: '',
  });

  // Calculate distance and price when coordinates change
  useEffect(() => {
    if (formData.sender_lat && formData.sender_lng && formData.receiver_lat && formData.receiver_lng) {
      const R = 6371; // Earth's radius in km
      const dLat = (formData.receiver_lat - formData.sender_lat) * Math.PI / 180;
      const dLon = (formData.receiver_lng - formData.sender_lng) * Math.PI / 180;
      const a =
        Math.sin(dLat/2) * Math.sin(dLat/2) +
        Math.cos(formData.sender_lat * Math.PI / 180) * Math.cos(formData.receiver_lat * Math.PI / 180) *
        Math.sin(dLon/2) * Math.sin(dLon/2);
      const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
      const distance = R * c;

      setEstimatedDistance(distance);

      // Calculate price
      const basePrice = 50;
      const pricePerKm = 8;
      const priorityMultiplier = formData.priority === 'express' ? 1.5 : formData.priority === 'same_day' ? 2 : 1;
      const price = (basePrice + distance * pricePerKm) * priorityMultiplier;

      setEstimatedPrice(Math.round(price));
    }
  }, [formData.sender_lat, formData.sender_lng, formData.receiver_lat, formData.receiver_lng, formData.priority]);

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSenderCoordinates = (coords) => {
    setFormData(prev => ({
      ...prev,
      sender_lat: coords.lat,
      sender_lng: coords.lng
    }));
  };

  const handleReceiverCoordinates = (coords) => {
    setFormData(prev => ({
      ...prev,
      receiver_lat: coords.lat,
      receiver_lng: coords.lng
    }));
  };

  const generateTrackingId = () => {
    const prefix = 'SAI';
    const timestamp = Date.now().toString(36).toUpperCase();
    const random = Math.random().toString(36).substring(2, 6).toUpperCase();
    return `${prefix}${timestamp}${random}`;
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);

    try {
      const deliveryData = {
        ...formData,
        tracking_id: generateTrackingId(),
        status: 'pending',
        price: estimatedPrice,
        distance_km: estimatedDistance,
        package_weight: parseFloat(formData.package_weight) || 0,
        estimated_delivery: new Date(Date.now() + (formData.priority === 'same_day' ? 8 : formData.priority === 'express' ? 24 : 48) * 60 * 60 * 1000).toISOString(),
      };

      const created = await base44.entities.Delivery.create(deliveryData);
      navigate(createPageUrl(`DeliveryDetails?id=${created.id}`));
    } catch (error) {
      console.error('Error creating delivery:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const canProceed = () => {
    switch (currentStep) {
      case 0:
        return formData.sender_name && formData.sender_phone && formData.sender_address;
      case 1:
        return formData.receiver_name && formData.receiver_phone && formData.receiver_address;
      case 2:
        return formData.package_type;
      case 3:
        return true;
      default:
        return false;
    }
  };

  return (
    <div className="min-h-screen bg-[#050505] pt-20">
      <div className="max-w-6xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="mb-8">
          <Button
            variant="ghost"
            onClick={() => navigate(-1)}
            className="mb-4 text-gray-400 hover:text-white"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
          </Button>
          <h1 className="text-3xl font-bold">Create Delivery</h1>
          <p className="text-gray-400 mt-1">Enter shipment details to get started</p>
        </div>

        {/* Progress Steps */}
        <div className="flex items-center justify-between mb-12 max-w-2xl">
          {steps.map((step, index) => {
            const StepIcon = step.icon;
            const isActive = index === currentStep;
            const isCompleted = index < currentStep;

            return (
              <React.Fragment key={step.id}>
                <div className="flex flex-col items-center">
                  <motion.div
                    animate={{
                      scale: isActive ? 1.1 : 1,
                      backgroundColor: isCompleted ? '#00FF88' : isActive ? '#0050FF' : 'rgba(255,255,255,0.1)'
                    }}
                    className={`w-12 h-12 rounded-full flex items-center justify-center ${
                      isActive ? 'ring-4 ring-[#0050FF]/30' : ''
                    }`}
                  >
                    {isCompleted ? (
                      <CheckCircle className="w-6 h-6 text-[#050505]" />
                    ) : (
                      <StepIcon className={`w-5 h-5 ${isActive ? 'text-white' : 'text-gray-500'}`} />
                    )}
                  </motion.div>
                  <span className={`text-xs mt-2 ${isActive ? 'text-white' : 'text-gray-500'}`}>
                    {step.label}
                  </span>
                </div>
                {index < steps.length - 1 && (
                  <div className={`flex-1 h-0.5 mx-4 ${
                    index < currentStep ? 'bg-[#00FF88]' : 'bg-white/10'
                  }`} />
                )}
              </React.Fragment>
            );
          })}
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Form Section */}
          <div className="p-6 rounded-2xl bg-gradient-to-br from-white/[0.03] to-transparent border border-white/5">
            <motion.div
              key={currentStep}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
            >
              {/* Step 0: Sender Details */}
              {currentStep === 0 && (
                <div className="space-y-6">
                  <div className="flex items-center gap-3 mb-6">
                    <div className="p-3 rounded-xl bg-[#0050FF]/20 border border-[#0050FF]/30">
                      <User className="w-5 h-5 text-[#0050FF]" />
                    </div>
                    <div>
                      <h2 className="font-semibold text-lg">Pickup Details</h2>
                      <p className="text-sm text-gray-500">Where should we pick up the package?</p>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <div>
                      <Label>Sender Name</Label>
                      <Input
                        value={formData.sender_name}
                        onChange={(e) => handleInputChange('sender_name', e.target.value)}
                        placeholder="Full name"
                        className="mt-1.5 h-12 bg-white/5 border-white/10"
                      />
                    </div>

                    <div>
                      <Label>Phone Number</Label>
                      <Input
                        value={formData.sender_phone}
                        onChange={(e) => handleInputChange('sender_phone', e.target.value)}
                        placeholder="+91 XXXXX XXXXX"
                        className="mt-1.5 h-12 bg-white/5 border-white/10"
                      />
                    </div>

                    <AddressInput
                      label="Pickup Address"
                      placeholder="Enter pickup location or landmark..."
                      value={formData.sender_address}
                      onChange={(value) => handleInputChange('sender_address', value)}
                      onCoordinatesResolved={handleSenderCoordinates}
                    />
                  </div>
                </div>
              )}

              {/* Step 1: Receiver Details */}
              {currentStep === 1 && (
                <div className="space-y-6">
                  <div className="flex items-center gap-3 mb-6">
                    <div className="p-3 rounded-xl bg-[#00FF88]/20 border border-[#00FF88]/30">
                      <MapPin className="w-5 h-5 text-[#00FF88]" />
                    </div>
                    <div>
                      <h2 className="font-semibold text-lg">Delivery Details</h2>
                      <p className="text-sm text-gray-500">Where should we deliver the package?</p>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <div>
                      <Label>Receiver Name</Label>
                      <Input
                        value={formData.receiver_name}
                        onChange={(e) => handleInputChange('receiver_name', e.target.value)}
                        placeholder="Full name"
                        className="mt-1.5 h-12 bg-white/5 border-white/10"
                      />
                    </div>

                    <div>
                      <Label>Phone Number</Label>
                      <Input
                        value={formData.receiver_phone}
                        onChange={(e) => handleInputChange('receiver_phone', e.target.value)}
                        placeholder="+91 XXXXX XXXXX"
                        className="mt-1.5 h-12 bg-white/5 border-white/10"
                      />
                    </div>

                    <AddressInput
                      label="Delivery Address"
                      placeholder="Enter delivery location or landmark..."
                      value={formData.receiver_address}
                      onChange={(value) => handleInputChange('receiver_address', value)}
                      onCoordinatesResolved={handleReceiverCoordinates}
                      icon={MapPin}
                      accentColor="#00FF88"
                    />
                  </div>
                </div>
              )}

              {/* Step 2: Package Details */}
              {currentStep === 2 && (
                <div className="space-y-6">
                  <div className="flex items-center gap-3 mb-6">
                    <div className="p-3 rounded-xl bg-[#00D6FF]/20 border border-[#00D6FF]/30">
                      <Package className="w-5 h-5 text-[#00D6FF]" />
                    </div>
                    <div>
                      <h2 className="font-semibold text-lg">Package Information</h2>
                      <p className="text-sm text-gray-500">Tell us about your shipment</p>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <div>
                      <Label>Package Type</Label>
                      <Select
                        value={formData.package_type}
                        onValueChange={(value) => handleInputChange('package_type', value)}
                      >
                        <SelectTrigger className="mt-1.5 h-12 bg-white/5 border-white/10">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="document">Document</SelectItem>
                          <SelectItem value="small_parcel">Small Parcel (up to 2kg)</SelectItem>
                          <SelectItem value="medium_parcel">Medium Parcel (2-10kg)</SelectItem>
                          <SelectItem value="large_parcel">Large Parcel (10-25kg)</SelectItem>
                          <SelectItem value="fragile">Fragile Item</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div>
                      <Label>Weight (kg)</Label>
                      <Input
                        type="number"
                        value={formData.package_weight}
                        onChange={(e) => handleInputChange('package_weight', e.target.value)}
                        placeholder="0.0"
                        className="mt-1.5 h-12 bg-white/5 border-white/10"
                      />
                    </div>

                    <div>
                      <Label className="mb-3 block">Delivery Priority</Label>
                      <RadioGroup
                        value={formData.priority}
                        onValueChange={(value) => handleInputChange('priority', value)}
                        className="grid grid-cols-3 gap-3"
                      >
                        <Label
                          htmlFor="standard"
                          className={`flex flex-col items-center p-4 rounded-xl border cursor-pointer transition-all ${
                            formData.priority === 'standard'
                              ? 'border-[#0050FF] bg-[#0050FF]/10'
                              : 'border-white/10 hover:border-white/20'
                          }`}
                        >
                          <RadioGroupItem value="standard" id="standard" className="sr-only" />
                          <Clock className="w-5 h-5 mb-2 text-gray-400" />
                          <span className="text-sm font-medium">Standard</span>
                          <span className="text-xs text-gray-500">2-3 days</span>
                        </Label>
                        <Label
                          htmlFor="express"
                          className={`flex flex-col items-center p-4 rounded-xl border cursor-pointer transition-all ${
                            formData.priority === 'express'
                              ? 'border-[#FF9500] bg-[#FF9500]/10'
                              : 'border-white/10 hover:border-white/20'
                          }`}
                        >
                          <RadioGroupItem value="express" id="express" className="sr-only" />
                          <Truck className="w-5 h-5 mb-2 text-[#FF9500]" />
                          <span className="text-sm font-medium">Express</span>
                          <span className="text-xs text-gray-500">24 hours</span>
                        </Label>
                        <Label
                          htmlFor="same_day"
                          className={`flex flex-col items-center p-4 rounded-xl border cursor-pointer transition-all ${
                            formData.priority === 'same_day'
                              ? 'border-[#FF2D55] bg-[#FF2D55]/10'
                              : 'border-white/10 hover:border-white/20'
                          }`}
                        >
                          <RadioGroupItem value="same_day" id="same_day" className="sr-only" />
                          <Zap className="w-5 h-5 mb-2 text-[#FF2D55]" />
                          <span className="text-sm font-medium">Same Day</span>
                          <span className="text-xs text-gray-500">8 hours</span>
                        </Label>
                      </RadioGroup>
                    </div>

                    <div>
                      <Label>Special Instructions (Optional)</Label>
                      <Textarea
                        value={formData.notes}
                        onChange={(e) => handleInputChange('notes', e.target.value)}
                        placeholder="Any special handling instructions..."
                        className="mt-1.5 bg-white/5 border-white/10 min-h-24"
                      />
                    </div>
                  </div>
                </div>
              )}

              {/* Step 3: Confirmation */}
              {currentStep === 3 && (
                <div className="space-y-6">
                  <div className="flex items-center gap-3 mb-6">
                    <div className="p-3 rounded-xl bg-[#00FF88]/20 border border-[#00FF88]/30">
                      <CheckCircle className="w-5 h-5 text-[#00FF88]" />
                    </div>
                    <div>
                      <h2 className="font-semibold text-lg">Confirm Delivery</h2>
                      <p className="text-sm text-gray-500">Review your shipment details</p>
                    </div>
                  </div>

                  {/* Summary */}
                  <div className="space-y-4">
                    <div className="p-4 rounded-xl bg-white/5 border border-white/10">
                      <div className="text-xs text-gray-500 mb-2">PICKUP</div>
                      <div className="font-medium">{formData.sender_name}</div>
                      <div className="text-sm text-gray-400">{formData.sender_address}</div>
                      <div className="text-sm text-gray-500">{formData.sender_phone}</div>
                    </div>

                    <div className="flex justify-center">
                      <ArrowRight className="w-5 h-5 text-gray-500" />
                    </div>

                    <div className="p-4 rounded-xl bg-white/5 border border-white/10">
                      <div className="text-xs text-gray-500 mb-2">DELIVERY</div>
                      <div className="font-medium">{formData.receiver_name}</div>
                      <div className="text-sm text-gray-400">{formData.receiver_address}</div>
                      <div className="text-sm text-gray-500">{formData.receiver_phone}</div>
                    </div>

                    <div className="p-4 rounded-xl bg-white/5 border border-white/10">
                      <div className="text-xs text-gray-500 mb-2">PACKAGE</div>
                      <div className="flex items-center justify-between">
                        <span className="text-gray-400">Type</span>
                        <span className="font-medium capitalize">{formData.package_type.replace('_', ' ')}</span>
                      </div>
                      <div className="flex items-center justify-between mt-2">
                        <span className="text-gray-400">Priority</span>
                        <span className="font-medium capitalize">{formData.priority.replace('_', ' ')}</span>
                      </div>
                      {formData.package_weight && (
                        <div className="flex items-center justify-between mt-2">
                          <span className="text-gray-400">Weight</span>
                          <span className="font-medium">{formData.package_weight} kg</span>
                        </div>
                      )}
                    </div>

                    {/* Price Summary */}
                    <div className="p-4 rounded-xl bg-gradient-to-br from-[#0050FF]/20 to-[#00D6FF]/10 border border-[#0050FF]/30">
                      <div className="flex items-center justify-between mb-3">
                        <span className="text-gray-400">Estimated Distance</span>
                        <span className="font-medium">{estimatedDistance?.toFixed(1) || '--'} km</span>
                      </div>
                      <div className="flex items-center justify-between text-lg">
                        <span className="font-medium">Total Price</span>
                        <span className="text-2xl font-bold text-[#00D6FF]">₹{estimatedPrice || '--'}</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </motion.div>

            {/* Navigation Buttons */}
            <div className="flex items-center justify-between mt-8 pt-6 border-t border-white/5">
              <Button
                variant="ghost"
                onClick={() => setCurrentStep(prev => prev - 1)}
                disabled={currentStep === 0}
                className="text-gray-400 hover:text-white"
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back
              </Button>

              {currentStep < steps.length - 1 ? (
                <Button
                  onClick={() => setCurrentStep(prev => prev + 1)}
                  disabled={!canProceed()}
                  className="bg-[#0050FF] hover:bg-[#0040DD]"
                >
                  Continue
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              ) : (
                <Button
                  onClick={handleSubmit}
                  disabled={isSubmitting}
                  className="bg-[#00FF88] hover:bg-[#00DD77] text-[#050505]"
                >
                  {isSubmitting ? (
                    <Loader2 className="w-4 h-4 animate-spin mr-2" />
                  ) : (
                    <CheckCircle className="w-4 h-4 mr-2" />
                  )}
                  Confirm Delivery
                </Button>
              )}
            </div>
          </div>

          {/* Map Section */}
          <div className="space-y-6">
            <div className="p-6 rounded-2xl bg-gradient-to-br from-white/[0.03] to-transparent border border-white/5">
              <h3 className="font-semibold mb-4">Route Preview</h3>
              <DeliveryMap
                origin={formData.sender_lat && formData.sender_lng ? {
                  lat: formData.sender_lat,
                  lng: formData.sender_lng,
                  address: formData.sender_address
                } : null}
                destination={formData.receiver_lat && formData.receiver_lng ? {
                  lat: formData.receiver_lat,
                  lng: formData.receiver_lng,
                  address: formData.receiver_address
                } : null}
                height="400px"
              />
            </div>

            {/* AI Insights */}
            {(formData.sender_lat || formData.receiver_lat) && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="p-6 rounded-2xl bg-gradient-to-br from-[#0050FF]/10 to-transparent border border-[#0050FF]/20"
              >
                <div className="flex items-center gap-2 mb-4">
                  <Sparkles className="w-5 h-5 text-[#00D6FF]" />
                  <h3 className="font-semibold">AI Address Intelligence</h3>
                </div>
                <div className="space-y-3 text-sm">
                  <div className="flex items-center justify-between">
                    <span className="text-gray-400">Address Resolution</span>
                    <span className="text-[#00FF88]">Active</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-400">Landmark Detection</span>
                    <span className="text-[#00FF88]">Enabled</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-400">Route Optimization</span>
                    <span className="text-[#00D6FF]">Ready</span>
                  </div>
                </div>
              </motion.div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
