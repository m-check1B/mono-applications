-- Secure refresh tokens implementation
-- This migration adds security columns while preserving backwards compatibility

-- Add new security tracking columns
ALTER TABLE "user_sessions" ADD COLUMN "refresh_token_hash" TEXT;
ALTER TABLE "user_sessions" ADD COLUMN "refresh_count" INTEGER NOT NULL DEFAULT 0;
ALTER TABLE "user_sessions" ADD COLUMN "last_refresh_at" TIMESTAMP(3);
ALTER TABLE "user_sessions" ADD COLUMN "revoked_at" TIMESTAMP(3);

-- For existing sessions, generate secure hashes from current refresh tokens
-- This is a one-time migration to secure existing sessions
UPDATE "user_sessions" 
SET "refresh_token_hash" = encode(sha256((refresh_token)::bytea), 'hex') 
WHERE "refresh_token_hash" IS NULL;

-- Make refresh_token_hash required and unique
ALTER TABLE "user_sessions" ALTER COLUMN "refresh_token_hash" SET NOT NULL;
CREATE UNIQUE INDEX "user_sessions_refresh_token_hash_key" ON "user_sessions"("refresh_token_hash");

-- Drop the old refresh_token column and its unique constraint
DROP INDEX IF EXISTS "user_sessions_refresh_token_key";
ALTER TABLE "user_sessions" DROP COLUMN "refresh_token";