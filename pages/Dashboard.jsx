import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { createPageUrl } from '../utils';
import { motion } from 'framer-motion';
import { useQuery } from '@tanstack/react-query';
import { base44 } from '@/api/base44Client';
import {
  Package,
  Truck,
  MapPin,
  TrendingUp,
  Clock,
  CheckCircle,
  AlertCircle,
  Plus,
  Search,
  Filter,
  ArrowRight,
  BarChart3,
  Users,
  Navigation
} from 'lucide-react';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import StatsCard from '../components/dashboard/StatsCard';
import { DeliveryAreaChart, DeliveryBarChart, StatusPieChart } from '../components/dashboard/DeliveryChart';
import DeliveryCard from '../components/delivery/DeliveryCard';
import DeliveryMap from '../components/map/DeliveryMap';

export default function Dashboard() {
  const [selectedTab, setSelectedTab] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');

  const { data: deliveries = [], isLoading } = useQuery({
    queryKey: ['deliveries'],
    queryFn: () => base44.entities.Delivery.list('-created_date', 50),
  });

  const { data: drivers = [] } = useQuery({
    queryKey: ['drivers'],
    queryFn: () => base44.entities.Driver.list(),
  });

  // Calculate stats
  const stats = {
    total: deliveries.length,
    pending: deliveries.filter(d => d.status === 'pending').length,
    inTransit: deliveries.filter(d => ['in_transit', 'out_for_delivery', 'picked_up'].includes(d.status)).length,
    delivered: deliveries.filter(d => d.status === 'delivered').length,
    failed: deliveries.filter(d => d.status === 'failed').length,
  };

  // Sample chart data
  const weeklyData = [
    { name: 'Mon', deliveries: 45 },
    { name: 'Tue', deliveries: 52 },
    { name: 'Wed', deliveries: 49 },
    { name: 'Thu', deliveries: 63 },
    { name: 'Fri', deliveries: 71 },
    { name: 'Sat', deliveries: 58 },
    { name: 'Sun', deliveries: 42 },
  ];

  const statusData = [
    { name: 'Delivered', value: stats.delivered || 12 },
    { name: 'In Transit', value: stats.inTransit || 8 },
    { name: 'Pending', value: stats.pending || 5 },
    { name: 'Failed', value: stats.failed || 2 },
  ];

  const filteredDeliveries = deliveries.filter(d => {
    const matchesSearch = !searchQuery ||
      d.tracking_id?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      d.receiver_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      d.sender_name?.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesTab = selectedTab === 'all' || d.status === selectedTab;

    return matchesSearch && matchesTab;
  });

  // Get active deliveries for map
  const activeDeliveries = deliveries.filter(d =>
    d.sender_lat && d.sender_lng && d.receiver_lat && d.receiver_lng &&
    ['in_transit', 'out_for_delivery'].includes(d.status)
  );

  return (
    <div className="min-h-screen bg-[#050505] pt-20">
      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 mb-8">
          <div>
            <h1 className="text-3xl font-bold">Dashboard</h1>
            <p className="text-gray-400 mt-1">Monitor your delivery operations</p>
          </div>
          <div className="flex items-center gap-3">
            <Link to={createPageUrl('CreateDelivery')}>
              <Button className="bg-[#0050FF] hover:bg-[#0040DD]">
                <Plus className="w-4 h-4 mr-2" />
                New Delivery
              </Button>
            </Link>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <StatsCard
            title="Total Deliveries"
            value={stats.total || 127}
            change="+12%"
            changeType="positive"
            icon={Package}
            color="#0050FF"
          />
          <StatsCard
            title="In Transit"
            value={stats.inTransit || 23}
            change="+5%"
            changeType="positive"
            icon={Truck}
            color="#00D6FF"
          />
          <StatsCard
            title="Delivered"
            value={stats.delivered || 89}
            change="+18%"
            changeType="positive"
            icon={CheckCircle}
            color="#00FF88"
          />
          <StatsCard
            title="Active Drivers"
            value={drivers.filter(d => d.status === 'on_delivery').length || 8}
            icon={Users}
            color="#FF9500"
          />
        </div>

        {/* Main Content Grid */}
        <div className="grid lg:grid-cols-3 gap-6 mb-8">
          {/* Chart Section */}
          <div className="lg:col-span-2 space-y-6">
            {/* Weekly Performance */}
            <div className="p-6 rounded-2xl bg-gradient-to-br from-white/[0.03] to-transparent border border-white/5">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h3 className="font-semibold text-lg">Weekly Performance</h3>
                  <p className="text-sm text-gray-500">Deliveries over the past week</p>
                </div>
                <div className="flex items-center gap-2 text-sm text-[#00FF88]">
                  <TrendingUp className="w-4 h-4" />
                  +15% vs last week
                </div>
              </div>
              <div className="h-64">
                <DeliveryAreaChart data={weeklyData} />
              </div>
            </div>

            {/* Live Map */}
            <div className="p-6 rounded-2xl bg-gradient-to-br from-white/[0.03] to-transparent border border-white/5">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="font-semibold text-lg">Live Tracking</h3>
                  <p className="text-sm text-gray-500">{activeDeliveries.length} active deliveries</p>
                </div>
                <Link to={createPageUrl('Tracking')}>
                  <Button variant="ghost" size="sm" className="text-[#00D6FF]">
                    View All <ArrowRight className="w-4 h-4 ml-1" />
                  </Button>
                </Link>
              </div>
              <DeliveryMap
                origin={activeDeliveries[0] && { lat: activeDeliveries[0].sender_lat, lng: activeDeliveries[0].sender_lng }}
                destination={activeDeliveries[0] && { lat: activeDeliveries[0].receiver_lat, lng: activeDeliveries[0].receiver_lng }}
                height="300px"
              />
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Status Distribution */}
            <div className="p-6 rounded-2xl bg-gradient-to-br from-white/[0.03] to-transparent border border-white/5">
              <h3 className="font-semibold text-lg mb-4">Status Distribution</h3>
              <div className="h-48">
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

            {/* Quick Actions */}
            <div className="p-6 rounded-2xl bg-gradient-to-br from-white/[0.03] to-transparent border border-white/5">
              <h3 className="font-semibold text-lg mb-4">Quick Actions</h3>
              <div className="space-y-2">
                <Link to={createPageUrl('CreateDelivery')} className="block">
                  <Button variant="outline" className="w-full justify-start border-white/10 hover:bg-white/5">
                    <Plus className="w-4 h-4 mr-2" />
                    Create Delivery
                  </Button>
                </Link>
                <Link to={createPageUrl('Tracking')} className="block">
                  <Button variant="outline" className="w-full justify-start border-white/10 hover:bg-white/5">
                    <Navigation className="w-4 h-4 mr-2" />
                    Track Shipment
                  </Button>
                </Link>
                <Link to={createPageUrl('AddressResolver')} className="block">
                  <Button variant="outline" className="w-full justify-start border-white/10 hover:bg-white/5">
                    <MapPin className="w-4 h-4 mr-2" />
                    Resolve Address
                  </Button>
                </Link>
                <Link to={createPageUrl('Analytics')} className="block">
                  <Button variant="outline" className="w-full justify-start border-white/10 hover:bg-white/5">
                    <BarChart3 className="w-4 h-4 mr-2" />
                    View Analytics
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </div>

        {/* Recent Deliveries */}
        <div className="p-6 rounded-2xl bg-gradient-to-br from-white/[0.03] to-transparent border border-white/5">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 mb-6">
            <h3 className="font-semibold text-lg">Recent Deliveries</h3>

            <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                <Input
                  placeholder="Search deliveries..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-9 bg-white/5 border-white/10 w-full sm:w-64"
                />
              </div>

              <Tabs value={selectedTab} onValueChange={setSelectedTab}>
                <TabsList className="bg-white/5">
                  <TabsTrigger value="all">All</TabsTrigger>
                  <TabsTrigger value="pending">Pending</TabsTrigger>
                  <TabsTrigger value="in_transit">Transit</TabsTrigger>
                  <TabsTrigger value="delivered">Delivered</TabsTrigger>
                </TabsList>
              </Tabs>
            </div>
          </div>

          {isLoading ? (
            <div className="grid gap-4">
              {[1, 2, 3].map(i => (
                <div key={i} className="h-32 rounded-xl bg-white/5 animate-pulse" />
              ))}
            </div>
          ) : filteredDeliveries.length > 0 ? (
            <div className="grid gap-4">
              {filteredDeliveries.slice(0, 5).map(delivery => (
                <Link key={delivery.id} to={createPageUrl(`DeliveryDetails?id=${delivery.id}`)}>
                  <DeliveryCard delivery={delivery} showActions={false} />
                </Link>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <Package className="w-12 h-12 text-gray-600 mx-auto mb-4" />
              <p className="text-gray-400">No deliveries found</p>
              <Link to={createPageUrl('CreateDelivery')}>
                <Button className="mt-4 bg-[#0050FF] hover:bg-[#0040DD]">
                  Create First Delivery
                </Button>
              </Link>
            </div>
          )}

          {filteredDeliveries.length > 5 && (
            <div className="mt-6 text-center">
              <Link to={createPageUrl('Deliveries')}>
                <Button variant="ghost" className="text-[#00D6FF]">
                  View All Deliveries <ArrowRight className="w-4 h-4 ml-1" />
                </Button>
              </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
