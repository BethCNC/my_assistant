'use client';

import { useState, useEffect } from 'react';
import { createClientComponentClient } from '@supabase/auth-helpers-nextjs';
import { Database } from '@/types/supabase';
import { format } from 'date-fns';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Skeleton } from '@/components/ui/skeleton';

type MedicalEvent = Database['public']['Tables']['medical_events']['Row'];

export default function MedicalEvents() {
  const [events, setEvents] = useState<MedicalEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [eventType, setEventType] = useState<string>('all');
  const [sortOrder, setSortOrder] = useState<'desc' | 'asc'>('desc');
  
  const supabase = createClientComponentClient<Database>();

  useEffect(() => {
    fetchEvents();
  }, [eventType, sortOrder]);

  async function fetchEvents() {
    try {
      setLoading(true);
      let query = supabase
        .from('medical_events')
        .select(`
          *,
          provider:providers(name, specialty),
          condition:conditions(name),
          treatment:treatments(name)
        `)
        .order('date', { ascending: sortOrder === 'asc' });

      if (eventType !== 'all') {
        query = query.eq('event_type', eventType);
      }

      const { data, error } = await query;

      if (error) throw error;
      setEvents(data || []);
    } catch (error) {
      console.error('Error fetching medical events:', error);
    } finally {
      setLoading(false);
    }
  }

  const eventTypeColors: Record<string, string> = {
    appointment: 'bg-blue-100 text-blue-800',
    hospitalization: 'bg-red-100 text-red-800',
    procedure: 'bg-purple-100 text-purple-800',
    test: 'bg-green-100 text-green-800',
    other: 'bg-gray-100 text-gray-800',
  };

  if (loading) {
    return (
      <div className="space-y-4">
        {[...Array(3)].map((_, i) => (
          <Skeleton key={i} className="h-32 w-full" />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex gap-4">
        <Select
          value={eventType}
          onValueChange={(value) => setEventType(value)}
        >
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="Filter by type" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Events</SelectItem>
            <SelectItem value="appointment">Appointments</SelectItem>
            <SelectItem value="hospitalization">Hospitalizations</SelectItem>
            <SelectItem value="procedure">Procedures</SelectItem>
            <SelectItem value="test">Tests</SelectItem>
            <SelectItem value="other">Other</SelectItem>
          </SelectContent>
        </Select>

        <Select
          value={sortOrder}
          onValueChange={(value: 'asc' | 'desc') => setSortOrder(value)}
        >
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="Sort by date" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="desc">Newest First</SelectItem>
            <SelectItem value="asc">Oldest First</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-4">
        {events.map((event) => (
          <Card key={event.id}>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-xl font-semibold">
                  {event.title}
                </CardTitle>
                <Badge 
                  variant="secondary"
                  className={eventTypeColors[event.event_type || 'other']}
                >
                  {event.event_type}
                </Badge>
              </div>
              <CardDescription>
                {format(new Date(event.date), 'PPP')}
                {event.location && ` • ${event.location}`}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {event.description && (
                  <p className="text-sm text-gray-600">{event.description}</p>
                )}
                {event.provider && (
                  <p className="text-sm">
                    <span className="font-medium">Provider:</span>{' '}
                    {event.provider.name}
                    {event.provider.specialty && ` (${event.provider.specialty})`}
                  </p>
                )}
                {event.condition && (
                  <p className="text-sm">
                    <span className="font-medium">Related Condition:</span>{' '}
                    {event.condition.name}
                  </p>
                )}
                {event.treatment && (
                  <p className="text-sm">
                    <span className="font-medium">Related Treatment:</span>{' '}
                    {event.treatment.name}
                  </p>
                )}
                {event.notes && (
                  <p className="text-sm mt-2 italic">{event.notes}</p>
                )}
              </div>
            </CardContent>
          </Card>
        ))}

        {events.length === 0 && (
          <p className="text-center text-gray-500">No medical events found</p>
        )}
      </div>
    </div>
  );
} 