-- Create medical_event_symptoms table
CREATE TABLE IF NOT EXISTS public.medical_event_symptoms (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    medical_event_id UUID REFERENCES public.medical_events(id) ON DELETE CASCADE,
    symptom_id UUID REFERENCES public.symptoms(id) ON DELETE CASCADE,
    severity INTEGER CHECK (severity >= 1 AND severity <= 10),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE DEFAULT auth.uid()
);

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_medical_event_symptoms_medical_event_id ON public.medical_event_symptoms(medical_event_id);
CREATE INDEX IF NOT EXISTS idx_medical_event_symptoms_symptom_id ON public.medical_event_symptoms(symptom_id);

-- Enable RLS
ALTER TABLE public.medical_event_symptoms ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Users can view their own medical event symptoms"
    ON public.medical_event_symptoms
    FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own medical event symptoms"
    ON public.medical_event_symptoms
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own medical event symptoms"
    ON public.medical_event_symptoms
    FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete their own medical event symptoms"
    ON public.medical_event_symptoms
    FOR DELETE
    USING (auth.uid() = user_id); 