import { NextApiRequest, NextApiResponse } from 'next';
import { supabase } from '../../lib/supabase/client';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  try {
    // Fetch some data from Supabase to test the connection
    const { data: conditions, error: conditionsError } = await supabase
      .from('conditions')
      .select('id, name, description, status')
      .limit(5);
    
    if (conditionsError) {
      throw new Error(`Error fetching conditions: ${conditionsError.message}`);
    }

    const { data: symptoms, error: symptomsError } = await supabase
      .from('symptoms')
      .select('id, name, description, severity')
      .limit(5);
      
    if (symptomsError) {
      throw new Error(`Error fetching symptoms: ${symptomsError.message}`);
    }

    const { data: providers, error: providersError } = await supabase
      .from('providers')
      .select('id, name, specialty, facility')
      .limit(5);
      
    if (providersError) {
      throw new Error(`Error fetching providers: ${providersError.message}`);
    }

    // Return success with data
    res.status(200).json({
      success: true,
      message: 'Database connection successful',
      data: {
        conditions,
        symptoms,
        providers
      }
    });
  } catch (error) {
    console.error('API error:', error);
    res.status(500).json({
      success: false,
      message: error instanceof Error ? error.message : 'Unknown error occurred',
    });
  }
} 