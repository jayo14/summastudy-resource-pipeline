-- Supabase SQL Schema for SummaStudy resources
CREATE TABLE IF NOT EXISTS public.resources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_code TEXT NOT NULL,
    filename TEXT NOT NULL,
    storage_path TEXT UNIQUE NOT NULL,
    mime_type TEXT NOT NULL,
    status TEXT DEFAULT 'uploaded',
    created_at TIMESTAMPTZ DEFAULT now()
);
