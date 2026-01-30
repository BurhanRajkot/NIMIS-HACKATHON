import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { createPageUrl } from '../utils';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { base44 } from '@/api/base44Client';
import { motion } from 'framer-motion';
import {
  Package,
  Search,
  Filter,
  Plus,
  ArrowUpDown,
  MoreHorizontal,
  Eye,
  Truck,
  CheckCircle,
  XCircle,
  Download,
  Trash2
} from 'lucide-react';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { format } from 'date-fns';

const statusConfig = {
  pending: { label: 'Pending', color: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30' },
  picked_up: { label: 'Picked Up', color: 'bg-blue-500/20 text-blue-400 border-blue-500/30' },
  in_transit: { label: 'In Transit', color: 'bg-purple-500/20 text-purple-400 border-purple-500/30' },
  out_for_delivery: { label: 'Out for Delivery', color: 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30' },
  delivered: { label: 'Delivered', color: 'bg-green-500/20 text-green-400 border-green-500/30' },
  failed: { label: 'Failed', color: 'bg-red-500/20 text-red-400 border-red-500/30' },
};

export default function Deliveries() {
  const queryClient = useQueryClient();
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [priorityFilter, setPriorityFilter] = useState('all');
  const [sortBy, setSortBy] = useState('-created_date');

  const { data: deliveries = [], isLoading } = useQuery({
    queryKey: ['deliveries', sortBy],
    queryFn: () => base44.entities.Delivery.list(sortBy, 100),
  });

  const updateStatusMutation = useMutation({
    mutationFn: ({ id, status }) => base44.entities.Delivery.update(id, { status }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['deliveries'] })
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => base44.entities.Delivery.delete(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['deliveries'] })
  });

  const filteredDeliveries = deliveries.filter(d => {
    const matchesSearch = !searchQuery ||
      d.tracking_id?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      d.receiver_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      d.sender_name?.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesStatus = statusFilter === 'all' || d.status === statusFilter;
    const matchesPriority = priorityFilter === 'all' || d.priority === priorityFilter;

    return matchesSearch && matchesStatus && matchesPriority;
  });

  const exportCSV = () => {
    const headers = ['Tracking ID', 'Sender', 'Receiver', 'Status', 'Priority', 'Price', 'Date'];
    const rows = filteredDeliveries.map(d => [
      d.tracking_id,
      d.sender_name,
      d.receiver_name,
      d.status,
      d.priority,
      d.price,
      d.created_date
    ]);

    const csv = [headers, ...rows].map(row => row.join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'deliveries.csv';
    a.click();
  };

  return (
    <div className="min-h-screen bg-[#050505] pt-20">
      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 mb-8">
          <div>
            <h1 className="text-3xl font-bold">Deliveries</h1>
            <p className="text-gray-400 mt-1">Manage and track all shipments</p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="outline" onClick={exportCSV} className="border-white/10">
              <Download className="w-4 h-4 mr-2" />
              Export
            </Button>
            <Link to={createPageUrl('CreateDelivery')}>
              <Button className="bg-[#0050FF] hover:bg-[#0040DD]">
                <Plus className="w-4 h-4 mr-2" />
                New Delivery
              </Button>
            </Link>
          </div>
        </div>

        {/* Filters */}
        <div className="flex flex-col lg:flex-row gap-4 mb-6">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
            <Input
              placeholder="Search by tracking ID, sender, or receiver..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9 bg-white/5 border-white/10"
            />
          </div>

          <div className="flex items-center gap-3">
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-40 bg-white/5 border-white/10">
                <Filter className="w-4 h-4 mr-2" />
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="pending">Pending</SelectItem>
                <SelectItem value="picked_up">Picked Up</SelectItem>
                <SelectItem value="in_transit">In Transit</SelectItem>
                <SelectItem value="out_for_delivery">Out for Delivery</SelectItem>
                <SelectItem value="delivered">Delivered</SelectItem>
                <SelectItem value="failed">Failed</SelectItem>
              </SelectContent>
            </Select>

            <Select value={priorityFilter} onValueChange={setPriorityFilter}>
              <SelectTrigger className="w-40 bg-white/5 border-white/10">
                <SelectValue placeholder="Priority" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Priority</SelectItem>
                <SelectItem value="standard">Standard</SelectItem>
                <SelectItem value="express">Express</SelectItem>
                <SelectItem value="same_day">Same Day</SelectItem>
              </SelectContent>
            </Select>

            <Select value={sortBy} onValueChange={setSortBy}>
              <SelectTrigger className="w-40 bg-white/5 border-white/10">
                <ArrowUpDown className="w-4 h-4 mr-2" />
                <SelectValue placeholder="Sort" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="-created_date">Newest First</SelectItem>
                <SelectItem value="created_date">Oldest First</SelectItem>
                <SelectItem value="-price">Highest Price</SelectItem>
                <SelectItem value="price">Lowest Price</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Results count */}
        <div className="text-sm text-gray-500 mb-4">
          Showing {filteredDeliveries.length} of {deliveries.length} deliveries
        </div>

        {/* Table */}
        <div className="rounded-2xl bg-gradient-to-br from-white/[0.03] to-transparent border border-white/5 overflow-hidden">
          <Table>
            <TableHeader>
              <TableRow className="border-white/5 hover:bg-transparent">
                <TableHead className="text-gray-400">Tracking ID</TableHead>
                <TableHead className="text-gray-400">Sender</TableHead>
                <TableHead className="text-gray-400">Receiver</TableHead>
                <TableHead className="text-gray-400">Status</TableHead>
                <TableHead className="text-gray-400">Priority</TableHead>
                <TableHead className="text-gray-400">Price</TableHead>
                <TableHead className="text-gray-400">Date</TableHead>
                <TableHead className="text-gray-400 text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                Array(5).fill(0).map((_, i) => (
                  <TableRow key={i} className="border-white/5">
                    <TableCell colSpan={8}>
                      <div className="h-12 bg-white/5 animate-pulse rounded" />
                    </TableCell>
                  </TableRow>
                ))
              ) : filteredDeliveries.length > 0 ? (
                filteredDeliveries.map((delivery) => {
                  const status = statusConfig[delivery.status] || statusConfig.pending;
                  return (
                    <TableRow
                      key={delivery.id}
                      className="border-white/5 hover:bg-white/[0.02] cursor-pointer"
                      onClick={() => window.location.href = createPageUrl(`DeliveryDetails?id=${delivery.id}`)}
                    >
                      <TableCell className="font-medium">
                        {delivery.tracking_id}
                      </TableCell>
                      <TableCell>
                        <div>
                          <div className="font-medium text-sm">{delivery.sender_name}</div>
                          <div className="text-xs text-gray-500 truncate max-w-32">{delivery.sender_address}</div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div>
                          <div className="font-medium text-sm">{delivery.receiver_name}</div>
                          <div className="text-xs text-gray-500 truncate max-w-32">{delivery.receiver_address}</div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline" className={status.color}>
                          {status.label}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <span className={`text-sm capitalize ${
                          delivery.priority === 'same_day' ? 'text-red-400' :
                          delivery.priority === 'express' ? 'text-orange-400' :
                          'text-gray-400'
                        }`}>
                          {delivery.priority?.replace('_', ' ') || 'Standard'}
                        </span>
                      </TableCell>
                      <TableCell className="font-medium">
                        ₹{delivery.price || '--'}
                      </TableCell>
                      <TableCell className="text-gray-400 text-sm">
                        {delivery.created_date && format(new Date(delivery.created_date), 'MMM d, h:mm a')}
                      </TableCell>
                      <TableCell className="text-right">
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild onClick={(e) => e.stopPropagation()}>
                            <Button variant="ghost" size="icon" className="h-8 w-8">
                              <MoreHorizontal className="w-4 h-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuItem onClick={() => window.location.href = createPageUrl(`DeliveryDetails?id=${delivery.id}`)}>
                              <Eye className="w-4 h-4 mr-2" />
                              View Details
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => window.location.href = createPageUrl(`Tracking?tracking_id=${delivery.tracking_id}`)}>
                              <Truck className="w-4 h-4 mr-2" />
                              Track
                            </DropdownMenuItem>
                            <DropdownMenuSeparator />
                            {delivery.status !== 'delivered' && delivery.status !== 'failed' && (
                              <>
                                <DropdownMenuItem
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    updateStatusMutation.mutate({ id: delivery.id, status: 'delivered' });
                                  }}
                                >
                                  <CheckCircle className="w-4 h-4 mr-2 text-green-400" />
                                  Mark Delivered
                                </DropdownMenuItem>
                                <DropdownMenuItem
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    updateStatusMutation.mutate({ id: delivery.id, status: 'failed' });
                                  }}
                                >
                                  <XCircle className="w-4 h-4 mr-2 text-red-400" />
                                  Mark Failed
                                </DropdownMenuItem>
                              </>
                            )}
                            <DropdownMenuSeparator />
                            <DropdownMenuItem
                              className="text-red-400"
                              onClick={(e) => {
                                e.stopPropagation();
                                if (confirm('Delete this delivery?')) {
                                  deleteMutation.mutate(delivery.id);
                                }
                              }}
                            >
                              <Trash2 className="w-4 h-4 mr-2" />
                              Delete
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </TableCell>
                    </TableRow>
                  );
                })
              ) : (
                <TableRow className="border-white/5">
                  <TableCell colSpan={8} className="text-center py-12">
                    <Package className="w-12 h-12 text-gray-600 mx-auto mb-4" />
                    <p className="text-gray-400">No deliveries found</p>
                    <Link to={createPageUrl('CreateDelivery')}>
                      <Button className="mt-4 bg-[#0050FF] hover:bg-[#0040DD]">
                        Create First Delivery
                      </Button>
                    </Link>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </div>
      </div>
    </div>
  );
}
