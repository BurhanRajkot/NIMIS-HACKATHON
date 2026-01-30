import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { ArrowRight, Building2, Mail, User, Loader2, CheckCircle } from 'lucide-react';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export default function CTASection() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    company: '',
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);

    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1500));

    setIsSubmitting(false);
    setIsSubmitted(true);
  };

  return (
    <section id="demo" className="relative py-24 lg:py-32 overflow-hidden">
      {/* Background effects */}
      <div className="absolute inset-0 bg-gradient-to-b from-[#050505] via-[#0A0A0C] to-[#050505]" />
      <div
        className="absolute inset-0 opacity-30"
        style={{
          background: 'radial-gradient(ellipse at center, rgba(0, 80, 255, 0.15) 0%, transparent 70%)',
        }}
      />

      <div className="relative max-w-7xl mx-auto px-6 lg:px-8">
        <div className="grid lg:grid-cols-2 gap-12 lg:gap-20 items-center">
          {/* Left content */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
          >
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 mb-6">
              <span className="w-2 h-2 rounded-full bg-[#0050FF] animate-pulse" />
              <span className="text-sm text-gray-400">Enterprise Ready</span>
            </div>

            <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold tracking-tight leading-tight">
              Ready to solve your
              <span className="text-gradient"> last-mile challenge?</span>
            </h2>

            <p className="mt-6 text-lg text-gray-400 leading-relaxed">
              Join leading logistics companies using Smart Address Intelligence to improve delivery accuracy and reduce failed attempts.
            </p>

            {/* Trust indicators */}
            <div className="mt-10 flex flex-wrap gap-6">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-white/5 flex items-center justify-center">
                  <CheckCircle className="w-5 h-5 text-[#00FF88]" />
                </div>
                <div className="text-sm">
                  <div className="font-medium">99.9% Uptime</div>
                  <div className="text-gray-500">SLA guaranteed</div>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-white/5 flex items-center justify-center">
                  <CheckCircle className="w-5 h-5 text-[#00FF88]" />
                </div>
                <div className="text-sm">
                  <div className="font-medium">SOC 2 Type II</div>
                  <div className="text-gray-500">Compliant</div>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-white/5 flex items-center justify-center">
                  <CheckCircle className="w-5 h-5 text-[#00FF88]" />
                </div>
                <div className="text-sm">
                  <div className="font-medium">GDPR Ready</div>
                  <div className="text-gray-500">Data protection</div>
                </div>
              </div>
            </div>
          </motion.div>

          {/* Right form */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.2 }}
          >
            <div className="glass-panel rounded-2xl p-8 lg:p-10">
              {!isSubmitted ? (
                <>
                  <h3 className="text-xl font-semibold mb-2">Request Enterprise Demo</h3>
                  <p className="text-gray-400 text-sm mb-8">
                    Get a personalized walkthrough of our platform
                  </p>

                  <form onSubmit={handleSubmit} className="space-y-5">
                    <div className="relative">
                      <User className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                      <Input
                        type="text"
                        placeholder="Full name"
                        value={formData.name}
                        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                        className="pl-12 h-12 bg-white/5 border-white/10 focus:border-[#0050FF] rounded-xl"
                        required
                      />
                    </div>

                    <div className="relative">
                      <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                      <Input
                        type="email"
                        placeholder="Work email"
                        value={formData.email}
                        onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                        className="pl-12 h-12 bg-white/5 border-white/10 focus:border-[#0050FF] rounded-xl"
                        required
                      />
                    </div>

                    <div className="relative">
                      <Building2 className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                      <Input
                        type="text"
                        placeholder="Company name"
                        value={formData.company}
                        onChange={(e) => setFormData({ ...formData, company: e.target.value })}
                        className="pl-12 h-12 bg-white/5 border-white/10 focus:border-[#0050FF] rounded-xl"
                        required
                      />
                    </div>

                    <Button
                      type="submit"
                      disabled={isSubmitting}
                      className="w-full h-12 bg-white text-[#050505] hover:bg-gray-100 rounded-xl font-medium"
                    >
                      {isSubmitting ? (
                        <Loader2 className="w-5 h-5 animate-spin" />
                      ) : (
                        <>
                          Get Started
                          <ArrowRight className="w-5 h-5 ml-2" />
                        </>
                      )}
                    </Button>
                  </form>

                  <p className="mt-6 text-xs text-gray-500 text-center">
                    By submitting, you agree to our Terms of Service and Privacy Policy
                  </p>
                </>
              ) : (
                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="text-center py-8"
                >
                  <div className="w-16 h-16 rounded-full bg-[#00FF88]/20 flex items-center justify-center mx-auto mb-6">
                    <CheckCircle className="w-8 h-8 text-[#00FF88]" />
                  </div>
                  <h3 className="text-xl font-semibold mb-2">Thank you!</h3>
                  <p className="text-gray-400">
                    Our team will reach out within 24 hours to schedule your demo.
                  </p>
                </motion.div>
              )}
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
