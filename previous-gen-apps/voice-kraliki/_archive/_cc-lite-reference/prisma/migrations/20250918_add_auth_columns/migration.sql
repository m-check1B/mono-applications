-- Add missing auth-related columns to users table to match current Prisma schema
DO $$ BEGIN
  CREATE TYPE "AuthProvider" AS ENUM ('LOCAL', 'GOOGLE');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

ALTER TABLE "users" ADD COLUMN IF NOT EXISTS "auth_provider" "AuthProvider" NOT NULL DEFAULT 'LOCAL';
ALTER TABLE "users" ADD COLUMN IF NOT EXISTS "google_id" TEXT;
ALTER TABLE "users" ADD COLUMN IF NOT EXISTS "google_profile" JSONB;
ALTER TABLE "users" ADD COLUMN IF NOT EXISTS "email_verified" BOOLEAN NOT NULL DEFAULT false;
ALTER TABLE "users" ADD COLUMN IF NOT EXISTS "polar_customer_id" TEXT;
ALTER TABLE "users" ADD COLUMN IF NOT EXISTS "subscription_id" TEXT;
ALTER TABLE "users" ADD COLUMN IF NOT EXISTS "subscription_status" TEXT;
ALTER TABLE "users" ADD COLUMN IF NOT EXISTS "subscribed_at" TIMESTAMP(3);
ALTER TABLE "users" ADD COLUMN IF NOT EXISTS "subscription_end_date" TIMESTAMP(3);
ALTER TABLE "users" ADD COLUMN IF NOT EXISTS "api_keys" JSONB;
ALTER TABLE "users" ADD COLUMN IF NOT EXISTS "last_activity_at" TIMESTAMP(3);

DO $$ BEGIN
  ALTER TABLE "users" ADD CONSTRAINT "users_google_id_key" UNIQUE ("google_id");
EXCEPTION WHEN duplicate_table THEN NULL; WHEN duplicate_object THEN NULL; END $$;

