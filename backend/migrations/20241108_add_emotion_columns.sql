-- Supabase migration: add multi-emotion support columns
alter table public.entries
    add column if not exists emotions jsonb default null;

alter table public.entries
    add column if not exists dominant_emotion text default null;

-- Backfill dominant_emotion with legacy sentiment values
update public.entries
set dominant_emotion = sentiment
where dominant_emotion is null and sentiment is not null;

