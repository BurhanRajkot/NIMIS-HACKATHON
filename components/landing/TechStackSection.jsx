import React from 'react';
import { motion } from 'framer-motion';

const techItems = [
  { name: 'TensorFlow', category: 'AI/ML' },
  { name: 'H3', category: 'Geospatial' },
  { name: 'FastAPI', category: 'Backend' },
  { name: 'Redis', category: 'Cache' },
  { name: 'PostgreSQL', category: 'Database' },
  { name: 'Kubernetes', category: 'Infrastructure' },
];

export default function TechStackSection() {
  return (
    <section id="technology" className="py-24 lg:py-32 bg-[#050505]">
      <div className="max-w-7xl mx-auto px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl sm:text-4xl font-bold tracking-tight">
            Built on <span className="text-gradient">proven technology</span>
          </h2>
          <p className="mt-4 text-gray-400 max-w-2xl mx-auto">
            Enterprise-grade infrastructure designed for scale and reliability
          </p>
        </motion.div>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
          {techItems.map((tech, index) => (
            <motion.div
              key={tech.name}
              initial={{ opacity: 0, scale: 0.9 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.05 }}
              className="group p-6 rounded-xl bg-white/[0.02] border border-white/5 hover:border-[#0050FF]/30 hover:bg-white/[0.04] transition-all duration-300 text-center"
            >
              <div className="text-lg font-medium group-hover:text-[#00D6FF] transition-colors">
                {tech.name}
              </div>
              <div className="text-xs text-gray-500 mt-1">{tech.category}</div>
            </motion.div>
          ))}
        </div>

        {/* API Preview */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.3 }}
          className="mt-16 lg:mt-24"
        >
          <div className="glass-panel rounded-2xl overflow-hidden">
            <div className="flex items-center gap-2 px-4 py-3 border-b border-white/5">
              <div className="w-3 h-3 rounded-full bg-red-500/80" />
              <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
              <div className="w-3 h-3 rounded-full bg-green-500/80" />
              <span className="ml-4 text-xs text-gray-500">api-request.py</span>
            </div>
            <pre className="p-6 text-sm overflow-x-auto">
              <code className="text-gray-300">
                <span className="text-[#FF79C6]">import</span> sai_client{'\n\n'}
                <span className="text-gray-500"># Initialize client</span>{'\n'}
                client = sai_client.<span className="text-[#50FA7B]">Client</span>(api_key=<span className="text-[#F1FA8C]">"your_api_key"</span>){'\n\n'}
                <span className="text-gray-500"># Resolve an unstructured address</span>{'\n'}
                result = client.<span className="text-[#8BE9FD]">resolve</span>({'\n'}
                {'    '}address=<span className="text-[#F1FA8C]">"Near old cinema, Sector 5, piche wali gali"</span>,{'\n'}
                {'    '}city=<span className="text-[#F1FA8C]">"Lucknow"</span>{'\n'}
                ){'\n\n'}
                <span className="text-[#FF79C6]">print</span>(result.coordinates)  <span className="text-gray-500"># (26.8467, 80.9462)</span>{'\n'}
                <span className="text-[#FF79C6]">print</span>(result.confidence)   <span className="text-gray-500"># 0.973</span>
              </code>
            </pre>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
