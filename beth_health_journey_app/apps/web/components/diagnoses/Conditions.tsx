import { useState, useEffect } from 'react';
import { createClient } from '@supabase/supabase-js';
import { Database } from '../../lib/supabase/database.types';

// Initialize Supabase client
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || '';
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || '';
const supabase = createClient<Database>(supabaseUrl, supabaseKey);

// Type for the condition with related provider
type Condition = Database['public']['Tables']['conditions']['Row'] & {
  providers?: Database['public']['Tables']['providers']['Row'] | null;
};

type ConditionStatus = 'active' | 'resolved' | 'chronic' | 'inactive';
type ConditionSeverity = 'mild' | 'moderate' | 'severe';

export default function Conditions() {
  const [conditions, setConditions] = useState<Condition[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<ConditionStatus | 'all'>('all');
  const [severityFilter, setSeverityFilter] = useState<ConditionSeverity | 'all'>('all');

  useEffect(() => {
    fetchConditions();
  }, [statusFilter, severityFilter]);

  async function fetchConditions() {
    setLoading(true);
    
    try {
      let query = supabase
        .from('conditions')
        .select(`
          *,
          providers:provider_id (*)
        `)
        .order('date_diagnosed', { ascending: false });
      
      // Apply filters if they're not set to 'all'
      if (statusFilter !== 'all') {
        query = query.eq('status', statusFilter);
      }
      
      if (severityFilter !== 'all') {
        query = query.eq('severity', severityFilter);
      }
      
      const { data, error } = await query;
      
      if (error) {
        throw error;
      }
      
      setConditions(data || []);
    } catch (error) {
      console.error('Error fetching conditions:', error);
    } finally {
      setLoading(false);
    }
  }

  function getStatusColor(status: string | null) {
    switch (status) {
      case 'active': return 'text-red-600';
      case 'chronic': return 'text-amber-600';
      case 'resolved': return 'text-green-600';
      case 'inactive': return 'text-gray-600';
      default: return 'text-gray-800';
    }
  }

  function getSeverityBadge(severity: string | null) {
    let bgColor;
    
    switch (severity) {
      case 'mild': 
        bgColor = 'bg-green-100 text-green-800';
        break;
      case 'moderate': 
        bgColor = 'bg-amber-100 text-amber-800';
        break;
      case 'severe': 
        bgColor = 'bg-red-100 text-red-800';
        break;
      default: 
        bgColor = 'bg-gray-100 text-gray-800';
    }
    
    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${bgColor}`}>
        {severity || 'Unknown'}
      </span>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Health Conditions</h2>
        
        <div className="flex gap-4">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value as ConditionStatus | 'all')}
            className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
          >
            <option value="all">All Statuses</option>
            <option value="active">Active</option>
            <option value="chronic">Chronic</option>
            <option value="resolved">Resolved</option>
            <option value="inactive">Inactive</option>
          </select>
          
          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value as ConditionSeverity | 'all')}
            className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
          >
            <option value="all">All Severities</option>
            <option value="mild">Mild</option>
            <option value="moderate">Moderate</option>
            <option value="severe">Severe</option>
          </select>
        </div>
      </div>
      
      {loading ? (
        <div className="space-y-4">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="animate-pulse">
              <div className="h-24 bg-gray-200 rounded-lg"></div>
            </div>
          ))}
        </div>
      ) : conditions.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500">No conditions found with the selected filters</p>
        </div>
      ) : (
        <div className="space-y-4">
          {conditions.map((condition) => (
            <div key={condition.id} className="border border-gray-200 rounded-lg p-5 hover:shadow-md transition-shadow">
              <div className="flex justify-between items-start">
                <div className="space-y-1">
                  <h3 className="text-lg font-medium text-gray-900">{condition.name}</h3>
                  
                  <div className="flex items-center gap-2">
                    <span className={`font-medium ${getStatusColor(condition.status)}`}>
                      {condition.status || 'Unknown status'}
                    </span>
                    {condition.severity && getSeverityBadge(condition.severity)}
                  </div>
                  
                  {condition.date_diagnosed && (
                    <p className="text-sm text-gray-500">
                      Diagnosed: {new Date(condition.date_diagnosed).toLocaleDateString()}
                    </p>
                  )}
                  
                  {condition.providers && (
                    <p className="text-sm text-gray-500">
                      Provider: {condition.providers.name || 'Unknown'}
                      {condition.providers.specialty && ` (${condition.providers.specialty})`}
                    </p>
                  )}
                </div>
                
                <div className="text-right">
                  <span className="px-3 py-1 text-sm rounded-full bg-gray-100">
                    {condition.category || 'Uncategorized'}
                  </span>
                </div>
              </div>
              
              {condition.description && (
                <p className="mt-3 text-gray-700">{condition.description}</p>
              )}
              
              {condition.notes && (
                <div className="mt-4 bg-gray-50 p-3 rounded text-sm text-gray-700">
                  <p className="font-medium text-gray-900 mb-1">Notes:</p>
                  <p>{condition.notes}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
} 