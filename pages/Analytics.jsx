import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { base44 } from '@/api/base44Client';
import { motion } from 'framer-motion';
import {
  BarChart3,
  TrendingUp,
  TrendingDown,
  Package,
  Truck,
  MapPin,
  Clock,
  CheckCircle,
  AlertCircle,
  Users,
  Calendar,
  DollarSign,
  Target
} from 'lucide-react';
import { Button } from "@/components/ui/button";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import StatsCard from '../components/dashboard/StatsCard';
import { DeliveryAreaChart, DeliveryBarChart, StatusPieChart } from '../components/dashboard/DeliveryChart';
import DeliveryMap from '../components/map/DeliveryMap';

export default function Analytics() {
  const [timeRange, setTimeRange] = useState('7d');
  const [selectedMetric, setSelectedMetric] = useState('deliveries');

  const { data: deliveries = [] } = useQuery({
    queryKey: ['deliveries'],
    queryFn: () => base44.entities.Delivery.list('-created_date', 200),
  });

  const { data: drivers = [] } = useQuery({
    queryKey: ['drivers'],
    queryFn: () => base44.entities.Driver.list(),
  });

  const { data: zones = [] } = useQuery({
    queryKey: ['zones'],
    queryFn: () => base44.entities.DeliveryZone.list(),
  });

  // Calculate comprehensive stats
  const stats = {
    total: deliveries.length || 127,
    delivered: deliveries.filter(d => d.status === 'delivered').length || 89,
    pending: deliveries.filter(d => d.status === 'pending').length || 15,
    inTransit: deliveries.filter(d => ['in_transit', 'out_for_delivery', 'picked_up'].includes(d.status)).length || 18,
    failed: deliveries.filter(d => d.status === 'failed').length || 5,
    totalRevenue: deliveries.reduce((sum, d) => sum + (d.price || 0), 0) || 45670,
    avgDeliveryTime: 4.2, // hours
    successRate: deliveries.length > 0
      ? Math.round((deliveries.filter(d => d.status === 'delivered').length / deliveries.length) * 100)
      : 92,
  };

  // Weekly performance data
  const weeklyData = [
    { name: 'Mon', deliveries: 45, revenue: 5400 },
    { name: 'Tue', deliveries: 52, revenue: 6240 },
    { name: 'Wed', deliveries: 49, revenue: 5880 },
    { name: 'Thu', deliveries: 63, revenue: 7560 },
    { name: 'Fri', deliveries: 71, revenue: 8520 },
    { name: 'Sat', deliveries: 58, revenue: 6960 },
    { name: 'Sun', deliveries: 42, revenue: 5040 },
  ];

  // Hourly distribution
  const hourlyData = [
    { name: '6am', deliveries: 5 },
    { name: '8am', deliveries: 12 },
    { name: '10am', deliveries: 25 },
    { name: '12pm', deliveries: 18 },
    { name: '2pm', deliveries: 22 },
    { name: '4pm', deliveries: 28 },
    { name: '6pm', deliveries: 15 },
    { name: '8pm', deliveries: 8 },
  ];

  // Status distribution
  const statusData = [
    { name: 'Delivered', value: stats.delivered },
    { name: 'In Transit', value: stats.inTransit },
    { name: 'Pending', value: stats.pending },
    { name: 'Failed', value: stats.failed },
  ];

  // Zone performance
  const zonePerformance = [
    { name: 'North Delhi', completed: 45, pending: 8, failed: 2 },
    { name: 'South Delhi', completed: 38, pending: 12, failed: 3 },
    { name: 'East Delhi', completed: 32, pending: 6, failed: 1 },
    { name: 'West Delhi', completed: 28, pending: 9, failed: 2 },
    { name: 'Gurgaon', completed: 41, pending: 5, failed: 1 },
  ];

  // Priority breakdown
  const priorityData = [
    { name: 'Standard', value: 65 },
    { name: 'Express', value: 25 },
    { name: 'Same Day', value: 10 },
  ];

  return (
    <div className="min-h-screen bg-[#050505] pt-20">
      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 mb-8">
          <div>
            <h1 className="text-3xl font-bold">Analytics</h1>
            <p className="text-gray-400 mt-1">Comprehensive delivery performance insights</p>
          </div>
          <div className="flex items-center gap-3">
            <Select value={timeRange} onValueChange={setTimeRange}>
              <SelectTrigger className="w-36 bg-white/5 border-white/10">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="24h">Last 24 hours</SelectItem>
                <SelectItem value="7d">Last 7 days</SelectItem>
                <SelectItem value="30d">Last 30 days</SelectItem>
                <SelectItem value="90d">Last 90 days</SelectItem>
              </SelectContent>
            </Select>
            <Button variant="outline" className="border-white/10">
              <Calendar className="w-4 h-4 mr-2" />
              Custom Range
            </Button>
          </div>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <StatsCard
            title="Total Deliveries"
            value={stats.total}
            change="+12%"
            changeType="positive"
            icon={Package}
            color="#0050FF"
          />
          <StatsCard
            title="Success Rate"
            value={stats.successRate}
            suffix="%"
            change="+3%"
            changeType="positive"
            icon={Target}
            color="#00FF88"
          />
          <StatsCard
            title="Total Revenue"
            value={stats.totalRevenue}
            prefix="₹"
            change="+18%"
            changeType="positive"
            icon={DollarSign}
            color="#00D6FF"
          />
          <StatsCard
            title="Avg Delivery Time"
            value={stats.avgDeliveryTime}
            suffix=" hrs"
            change="-8%"
            changeType="positive"
            icon={Clock}
            color="#FF9500"
          />
        </div>

        {/* Charts Grid */}
        <div className="grid lg:grid-cols-3 gap-6 mb-8">
          {/* Main Chart */}
          <div className="lg:col-span-2 p-6 rounded-2xl bg-gradient-to-br from-white/[0.03] to-transparent border border-white/5">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="font-semibold text-lg">Performance Trend</h3>
                <p className="text-sm text-gray-500">Weekly delivery volume</p>
              </div>
              <Tabs value={selectedMetric} onValueChange={setSelectedMetric}>
                <TabsList className="bg-white/5">
                  <TabsTrigger value="deliveries">Deliveries</TabsTrigger>
                  <TabsTrigger value="revenue">Revenue</TabsTrigger>
                </TabsList>
              </Tabs>
            </div>
            <div className="h-80">
              <DeliveryAreaChart
                data={weeklyData}
                dataKey={selectedMetric}
                color={selectedMetric === 'revenue' ? '#00FF88' : '#0050FF'}
              />
            </div>
          </div>

          {/* Status Distribution */}
          <div className="p-6 rounded-2xl bg-gradient-to-br from-white/[0.03] to-transparent border border-white/5">
            <h3 className="font-semibold text-lg mb-4">Status Distribution</h3>
            <div className="h-52">
              <StatusPieChart data={statusData} />
            </div>
            <div className="mt-4 space-y-2">
              {statusData.map((item, idx) => (
                <div key={item.name} className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-2">
                    <div className={`w-3 h-3 rounded-full ${
                      idx === 0 ? 'bg-[#00FF88]' :
                      idx === 1 ? 'bg-[#0050FF]' :
                      idx === 2 ? 'bg-[#00D6FF]' :
                      'bg-[#FF4444]'
                    }`} />
                    <span className="text-gray-400">{item.name}</span>
                  </div>
                  <span className="font-medium">{item.value}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Second Row */}
        <div className="grid lg:grid-cols-2 gap-6 mb-8">
          {/* Zone Performance */}
          <div className="p-6 rounded-2xl bg-gradient-to-br from-white/[0.03] to-transparent border border-white/5">
            <h3 className="font-semibold text-lg mb-6">Zone Performance</h3>
            <div className="h-64">
              <DeliveryBarChart data={zonePerformance} />
            </div>
          </div>

          {/* Hourly Distribution */}
          <div className="p-6 rounded-2xl bg-gradient-to-br from-white/[0.03] to-transparent border border-white/5">
            <h3 className="font-semibold text-lg mb-6">Hourly Distribution</h3>
            <div className="h-64">
              <DeliveryAreaChart data={hourlyData} color="#00D6FF" />
            </div>
          </div>
        </div>

        {/* Third Row */}
        <div className="grid lg:grid-cols-3 gap-6">
          {/* Driver Performance */}
          <div className="p-6 rounded-2xl bg-gradient-to-br from-white/[0.03] to-transparent border border-white/5">
            <h3 className="font-semibold text-lg mb-4">Top Drivers</h3>
            <div className="space-y-4">
              {[
                { name: 'Rajesh Kumar', deliveries: 45, rating: 4.9 },
                { name: 'Amit Singh', deliveries: 42, rating: 4.8 },
                { name: 'Suresh Sharma', deliveries: 38, rating: 4.7 },
                { name: 'Vikram Patel', deliveries: 35, rating: 4.6 },
                { name: 'Deepak Gupta', deliveries: 32, rating: 4.5 },
              ].map((driver, idx) => (
                <div key={driver.name} className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                      idx === 0 ? 'bg-yellow-500/20 text-yellow-400' :
                      idx === 1 ? 'bg-gray-400/20 text-gray-300' :
                      idx === 2 ? 'bg-orange-500/20 text-orange-400' :
                      'bg-white/5 text-gray-400'
                    }`}>
                      {idx + 1}
                    </div>
                    <div>
                      <div className="font-medium text-sm">{driver.name}</div>
                      <div className="text-xs text-gray-500">{driver.deliveries} deliveries</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-1">
                    <span className="text-yellow-400">★</span>
                    <span className="text-sm">{driver.rating}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Priority Breakdown */}
          <div className="p-6 rounded-2xl bg-gradient-to-br from-white/[0.03] to-transparent border border-white/5">
            <h3 className="font-semibold text-lg mb-4">Priority Breakdown</h3>
            <div className="space-y-4">
              {priorityData.map((item, idx) => (
                <div key={item.name}>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-gray-400">{item.name}</span>
                    <span className="text-sm font-medium">{item.value}%</span>
                  </div>
                  <div className="h-2 rounded-full bg-white/10 overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${item.value}%` }}
                      transition={{ duration: 1, delay: idx * 0.2 }}
                      className={`h-full ${
                        idx === 0 ? 'bg-[#0050FF]' :
                        idx === 1 ? 'bg-[#FF9500]' :
                        'bg-[#FF2D55]'
                      }`}
                    />
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-6 pt-6 border-t border-white/5">
              <h4 className="text-sm text-gray-500 mb-3">Revenue by Priority</h4>
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-400">Standard</span>
                  <span className="font-medium">₹23,450</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-400">Express</span>
                  <span className="font-medium">₹15,820</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-400">Same Day</span>
                  <span className="font-medium">₹6,400</span>
                </div>
              </div>
            </div>
          </div>

          {/* Performance Metrics */}
          <div className="p-6 rounded-2xl bg-gradient-to-br from-white/[0.03] to-transparent border border-white/5">
            <h3 className="font-semibold text-lg mb-4">Performance Metrics</h3>
            <div className="space-y-6">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-400">On-Time Delivery</span>
                  <span className="text-sm font-medium text-[#00FF88]">94%</span>
                </div>
                <div className="h-2 rounded-full bg-white/10 overflow-hidden">
                  <div className="h-full w-[94%] bg-[#00FF88]" />
                </div>
              </div>
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-400">First Attempt Success</span>
                  <span className="text-sm font-medium text-[#00D6FF]">88%</span>
                </div>
                <div className="h-2 rounded-full bg-white/10 overflow-hidden">
                  <div className="h-full w-[88%] bg-[#00D6FF]" />
                </div>
              </div>
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-400">Customer Satisfaction</span>
                  <span className="text-sm font-medium text-[#0050FF]">4.7/5</span>
                </div>
                <div className="h-2 rounded-full bg-white/10 overflow-hidden">
                  <div className="h-full w-[94%] bg-[#0050FF]" />
                </div>
              </div>
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-400">Address Resolution</span>
                  <span className="text-sm font-medium text-[#FF9500]">97%</span>
                </div>
                <div className="h-2 rounded-full bg-white/10 overflow-hidden">
                  <div className="h-full w-[97%] bg-[#FF9500]" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
