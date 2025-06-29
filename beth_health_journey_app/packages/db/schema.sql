-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create tables
CREATE TABLE providers (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  specialty TEXT,
  facility TEXT,
  address TEXT,
  phone TEXT,
  email TEXT,
  website TEXT,
  notes TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE conditions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  description TEXT,
  date_diagnosed TIMESTAMP WITH TIME ZONE,
  status TEXT CHECK (status IN ('active', 'resolved', 'in_remission', 'suspected', 'misdignosed')),
  severity INTEGER CHECK (severity BETWEEN 1 AND 10),
  category TEXT,
  notes TEXT,
  provider_id UUID,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  FOREIGN KEY (provider_id) REFERENCES providers (id) ON DELETE SET NULL
);

CREATE TABLE treatments (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  condition_id UUID,
  name TEXT NOT NULL,
  type TEXT CHECK (type IN ('medication', 'procedure', 'therapy', 'lifestyle')),
  description TEXT,
  start_date TIMESTAMP WITH TIME ZONE,
  end_date TIMESTAMP WITH TIME ZONE,
  dosage TEXT,
  frequency TEXT,
  effectiveness INTEGER CHECK (effectiveness BETWEEN 1 AND 10),
  side_effects TEXT,
  prescribed_by UUID,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  FOREIGN KEY (condition_id) REFERENCES conditions (id) ON DELETE SET NULL,
  FOREIGN KEY (prescribed_by) REFERENCES providers (id) ON DELETE SET NULL
);

CREATE TABLE symptoms (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  description TEXT,
  severity INTEGER CHECK (severity BETWEEN 1 AND 10),
  frequency TEXT,
  duration TEXT,
  triggers JSONB,
  alleviating_factors JSONB,
  date_recorded TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Junction table for conditions to symptoms
CREATE TABLE condition_symptoms (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  condition_id UUID NOT NULL,
  symptom_id UUID NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  FOREIGN KEY (condition_id) REFERENCES conditions (id) ON DELETE CASCADE,
  FOREIGN KEY (symptom_id) REFERENCES symptoms (id) ON DELETE CASCADE,
  UNIQUE (condition_id, symptom_id)
);

CREATE TABLE medical_events (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  title TEXT NOT NULL,
  description TEXT,
  event_type TEXT CHECK (event_type IN ('appointment', 'hospitalization', 'procedure', 'test', 'lab_result', 'other')),
  date TIMESTAMP WITH TIME ZONE NOT NULL,
  location TEXT,
  provider_id UUID,
  condition_id UUID,
  treatment_id UUID,
  notes TEXT,
  documents JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  FOREIGN KEY (provider_id) REFERENCES providers (id) ON DELETE SET NULL,
  FOREIGN KEY (condition_id) REFERENCES conditions (id) ON DELETE SET NULL,
  FOREIGN KEY (treatment_id) REFERENCES treatments (id) ON DELETE SET NULL
);

CREATE TABLE lab_results (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  medical_event_id UUID,
  test_name TEXT NOT NULL,
  category TEXT,
  date TIMESTAMP WITH TIME ZONE NOT NULL,
  result TEXT NOT NULL,
  unit TEXT,
  reference_range TEXT,
  is_abnormal BOOLEAN DEFAULT FALSE,
  provider_id UUID,
  notes TEXT,
  file_url TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  FOREIGN KEY (medical_event_id) REFERENCES medical_events (id) ON DELETE SET NULL,
  FOREIGN KEY (provider_id) REFERENCES providers (id) ON DELETE SET NULL
);

CREATE TABLE documents (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  title TEXT NOT NULL,
  description TEXT,
  file_url TEXT NOT NULL,
  file_type TEXT,
  category TEXT,
  date TIMESTAMP WITH TIME ZONE,
  tags JSONB,
  related_entity_id UUID,
  related_entity_type TEXT CHECK (related_entity_type IN ('condition', 'treatment', 'event', 'provider')),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create Row-Level Security (RLS) policies
ALTER TABLE conditions ENABLE ROW LEVEL SECURITY;
ALTER TABLE treatments ENABLE ROW LEVEL SECURITY;
ALTER TABLE symptoms ENABLE ROW LEVEL SECURITY;
ALTER TABLE condition_symptoms ENABLE ROW LEVEL SECURITY;
ALTER TABLE providers ENABLE ROW LEVEL SECURITY;
ALTER TABLE medical_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE lab_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- Create indices for better performance
CREATE INDEX idx_conditions_provider ON conditions (provider_id);
CREATE INDEX idx_treatments_condition ON treatments (condition_id);
CREATE INDEX idx_treatments_provider ON treatments (prescribed_by);
CREATE INDEX idx_condition_symptoms_condition ON condition_symptoms (condition_id);
CREATE INDEX idx_condition_symptoms_symptom ON condition_symptoms (symptom_id);
CREATE INDEX idx_medical_events_provider ON medical_events (provider_id);
CREATE INDEX idx_medical_events_condition ON medical_events (condition_id);
CREATE INDEX idx_medical_events_treatment ON medical_events (treatment_id);
CREATE INDEX idx_lab_results_event ON lab_results (medical_event_id);
CREATE INDEX idx_lab_results_provider ON lab_results (provider_id); 