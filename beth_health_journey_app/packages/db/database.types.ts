export type Database = {
  public: {
    Tables: {
      conditions: {
        Row: {
          id: string;
          name: string;
          description: string | null;
          date_diagnosed: string | null;
          status: string | null;
          severity: number | null;
          category: string | null;
          notes: string | null;
          provider_id: string | null;
          created_at: string;
          updated_at: string;
        };
        Insert: {
          id?: string;
          name: string;
          description?: string | null;
          date_diagnosed?: string | null;
          status?: string | null;
          severity?: number | null;
          category?: string | null;
          notes?: string | null;
          provider_id?: string | null;
          created_at?: string;
          updated_at?: string;
        };
        Update: {
          id?: string;
          name?: string;
          description?: string | null;
          date_diagnosed?: string | null;
          status?: string | null;
          severity?: number | null;
          category?: string | null;
          notes?: string | null;
          provider_id?: string | null;
          created_at?: string;
          updated_at?: string;
        };
      };
      symptoms: {
        Row: {
          id: string;
          condition_id: string | null;
          name: string;
          description: string | null;
          severity: number | null;
          frequency: string | null;
          duration: string | null;
          triggers: string[] | null;
          alleviating_factors: string[] | null;
          date_recorded: string;
          created_at: string;
          updated_at: string;
        };
        Insert: {
          id?: string;
          condition_id?: string | null;
          name: string;
          description?: string | null;
          severity?: number | null;
          frequency?: string | null;
          duration?: string | null;
          triggers?: string[] | null;
          alleviating_factors?: string[] | null;
          date_recorded?: string;
          created_at?: string;
          updated_at?: string;
        };
        Update: {
          id?: string;
          condition_id?: string | null;
          name?: string;
          description?: string | null;
          severity?: number | null;
          frequency?: string | null;
          duration?: string | null;
          triggers?: string[] | null;
          alleviating_factors?: string[] | null;
          date_recorded?: string;
          created_at?: string;
          updated_at?: string;
        };
      };
      providers: {
        Row: {
          id: string;
          name: string;
          specialty: string | null;
          facility: string | null;
          address: string | null;
          phone: string | null;
          email: string | null;
          website: string | null;
          notes: string | null;
          created_at: string;
          updated_at: string;
        };
        Insert: {
          id?: string;
          name: string;
          specialty?: string | null;
          facility?: string | null;
          address?: string | null;
          phone?: string | null;
          email?: string | null;
          website?: string | null;
          notes?: string | null;
          created_at?: string;
          updated_at?: string;
        };
        Update: {
          id?: string;
          name?: string;
          specialty?: string | null;
          facility?: string | null;
          address?: string | null;
          phone?: string | null;
          email?: string | null;
          website?: string | null;
          notes?: string | null;
          created_at?: string;
          updated_at?: string;
        };
      };
      medical_events: {
        Row: {
          id: string;
          title: string;
          description: string | null;
          event_type: string | null;
          date: string;
          location: string | null;
          provider_id: string | null;
          condition_id: string | null;
          treatment_id: string | null;
          notes: string | null;
          documents: string[] | null;
          created_at: string;
          updated_at: string;
        };
        Insert: {
          id?: string;
          title: string;
          description?: string | null;
          event_type?: string | null;
          date: string;
          location?: string | null;
          provider_id?: string | null;
          condition_id?: string | null;
          treatment_id?: string | null;
          notes?: string | null;
          documents?: string[] | null;
          created_at?: string;
          updated_at?: string;
        };
        Update: {
          id?: string;
          title?: string;
          description?: string | null;
          event_type?: string | null;
          date?: string;
          location?: string | null;
          provider_id?: string | null;
          condition_id?: string | null;
          treatment_id?: string | null;
          notes?: string | null;
          documents?: string[] | null;
          created_at?: string;
          updated_at?: string;
        };
      };
      lab_results: {
        Row: {
          id: string;
          test_name: string;
          category: string | null;
          date: string;
          result: string;
          unit: string | null;
          reference_range: string | null;
          is_abnormal: boolean | null;
          provider_id: string | null;
          notes: string | null;
          file_url: string | null;
          created_at: string;
          updated_at: string;
        };
        Insert: {
          id?: string;
          test_name: string;
          category?: string | null;
          date: string;
          result: string;
          unit?: string | null;
          reference_range?: string | null;
          is_abnormal?: boolean | null;
          provider_id?: string | null;
          notes?: string | null;
          file_url?: string | null;
          created_at?: string;
          updated_at?: string;
        };
        Update: {
          id?: string;
          test_name?: string;
          category?: string | null;
          date?: string;
          result?: string;
          unit?: string | null;
          reference_range?: string | null;
          is_abnormal?: boolean | null;
          provider_id?: string | null;
          notes?: string | null;
          file_url?: string | null;
          created_at?: string;
          updated_at?: string;
        };
      };
    };
  };
}; 