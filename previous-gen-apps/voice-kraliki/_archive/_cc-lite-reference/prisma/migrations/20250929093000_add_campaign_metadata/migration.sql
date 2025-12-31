-- Add metadata column to campaigns table if missing
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'campaigns' AND column_name = 'metadata'
  ) THEN
    ALTER TABLE "campaigns" ADD COLUMN "metadata" JSONB;
  END IF;
END;
$$;
