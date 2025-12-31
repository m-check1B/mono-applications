-- CreateEnum
CREATE TYPE "UserRole" AS ENUM ('AGENT', 'SUPERVISOR', 'ADMIN');

-- CreateEnum
CREATE TYPE "UserStatus" AS ENUM ('ACTIVE', 'INACTIVE', 'SUSPENDED');

-- CreateEnum
CREATE TYPE "TeamRole" AS ENUM ('MEMBER', 'LEAD', 'SUPERVISOR');

-- CreateEnum
CREATE TYPE "CampaignType" AS ENUM ('INBOUND', 'OUTBOUND', 'TRANSFER', 'ESCALATION');

-- CreateEnum
CREATE TYPE "CallStatus" AS ENUM ('QUEUED', 'RINGING', 'IN_PROGRESS', 'ON_HOLD', 'COMPLETED', 'NO_ANSWER', 'BUSY', 'FAILED', 'CANCELED');

-- CreateEnum
CREATE TYPE "CallDirection" AS ENUM ('INBOUND', 'OUTBOUND');

-- CreateEnum
CREATE TYPE "SessionStatus" AS ENUM ('ACTIVE', 'PAUSED', 'COMPLETED', 'ERROR');

-- CreateEnum
CREATE TYPE "TranscriptRole" AS ENUM ('USER', 'ASSISTANT', 'SYSTEM');

-- CreateTable
CREATE TABLE "organizations" (
    "id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "domain" TEXT,
    "settings" JSONB,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "organizations_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "users" (
    "id" TEXT NOT NULL,
    "email" TEXT NOT NULL,
    "username" TEXT NOT NULL,
    "first_name" TEXT NOT NULL,
    "last_name" TEXT NOT NULL,
    "password_hash" TEXT NOT NULL,
    "role" "UserRole" NOT NULL,
    "status" "UserStatus" NOT NULL DEFAULT 'ACTIVE',
    "skills" TEXT[],
    "department" TEXT,
    "phone_extension" TEXT,
    "avatar" TEXT,
    "preferences" JSONB,
    "organization_id" TEXT NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,
    "last_login_at" TIMESTAMP(3),

    CONSTRAINT "users_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "teams" (
    "id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "description" TEXT,
    "organization_id" TEXT NOT NULL,
    "settings" JSONB,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "teams_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "team_members" (
    "id" TEXT NOT NULL,
    "user_id" TEXT NOT NULL,
    "team_id" TEXT NOT NULL,
    "role" "TeamRole" NOT NULL DEFAULT 'MEMBER',
    "joined_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "team_members_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "user_sessions" (
    "id" TEXT NOT NULL,
    "user_id" TEXT NOT NULL,
    "session_token" TEXT NOT NULL,
    "refresh_token" TEXT NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "expires_at" TIMESTAMP(3) NOT NULL,
    "last_activity" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "ip_address" TEXT,
    "user_agent" TEXT,

    CONSTRAINT "user_sessions_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "campaigns" (
    "id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "description" TEXT,
    "type" "CampaignType" NOT NULL,
    "language" TEXT NOT NULL DEFAULT 'en',
    "version" TEXT NOT NULL DEFAULT '1.0.0',
    "active" BOOLEAN NOT NULL DEFAULT false,
    "organization_id" TEXT NOT NULL,
    "instructions" JSONB NOT NULL,
    "tools" JSONB,
    "voice" JSONB,
    "analytics" JSONB,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "campaigns_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "campaign_metrics" (
    "id" TEXT NOT NULL,
    "campaign_id" TEXT NOT NULL,
    "calls_handled" INTEGER NOT NULL DEFAULT 0,
    "successful_completions" INTEGER NOT NULL DEFAULT 0,
    "average_handle_time" DOUBLE PRECISION NOT NULL DEFAULT 0,
    "customer_satisfaction" DOUBLE PRECISION,
    "tools_used" JSONB NOT NULL DEFAULT '{}',
    "error_rate" DOUBLE PRECISION NOT NULL DEFAULT 0,
    "last_used" TIMESTAMP(3) NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "campaign_metrics_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "calls" (
    "id" TEXT NOT NULL,
    "twilio_call_sid" TEXT,
    "from_number" TEXT NOT NULL,
    "to_number" TEXT NOT NULL,
    "status" "CallStatus" NOT NULL DEFAULT 'QUEUED',
    "direction" "CallDirection" NOT NULL,
    "organization_id" TEXT NOT NULL,
    "agent_id" TEXT,
    "supervisor_id" TEXT,
    "campaign_id" TEXT,
    "start_time" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "end_time" TIMESTAMP(3),
    "duration" INTEGER,
    "recording_url" TEXT,
    "disposition" TEXT,
    "notes" TEXT,
    "metadata" JSONB,

    CONSTRAINT "calls_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "contact_sessions" (
    "id" TEXT NOT NULL,
    "call_id" TEXT,
    "agent_id" TEXT NOT NULL,
    "campaign_id" TEXT,
    "status" "SessionStatus" NOT NULL DEFAULT 'ACTIVE',
    "start_time" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "end_time" TIMESTAMP(3),
    "conversation_history" JSONB NOT NULL DEFAULT '[]',
    "context" JSONB NOT NULL DEFAULT '{}',
    "metrics" JSONB NOT NULL DEFAULT '{}',
    "recovery_attempts" INTEGER NOT NULL DEFAULT 0,
    "last_recovery_time" TIMESTAMP(3),

    CONSTRAINT "contact_sessions_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "call_transcripts" (
    "id" TEXT NOT NULL,
    "call_id" TEXT NOT NULL,
    "role" "TranscriptRole" NOT NULL,
    "content" TEXT NOT NULL,
    "timestamp" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "confidence" DOUBLE PRECISION,
    "speaker_id" TEXT,
    "metadata" JSONB,

    CONSTRAINT "call_transcripts_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "organizations_domain_key" ON "organizations"("domain");

-- CreateIndex
CREATE UNIQUE INDEX "users_email_key" ON "users"("email");

-- CreateIndex
CREATE UNIQUE INDEX "users_username_key" ON "users"("username");

-- CreateIndex
CREATE UNIQUE INDEX "team_members_user_id_team_id_key" ON "team_members"("user_id", "team_id");

-- CreateIndex
CREATE UNIQUE INDEX "user_sessions_session_token_key" ON "user_sessions"("session_token");

-- CreateIndex
CREATE UNIQUE INDEX "user_sessions_refresh_token_key" ON "user_sessions"("refresh_token");

-- CreateIndex
CREATE UNIQUE INDEX "calls_twilio_call_sid_key" ON "calls"("twilio_call_sid");

-- AddForeignKey
ALTER TABLE "users" ADD CONSTRAINT "users_organization_id_fkey" FOREIGN KEY ("organization_id") REFERENCES "organizations"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "teams" ADD CONSTRAINT "teams_organization_id_fkey" FOREIGN KEY ("organization_id") REFERENCES "organizations"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "team_members" ADD CONSTRAINT "team_members_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "team_members" ADD CONSTRAINT "team_members_team_id_fkey" FOREIGN KEY ("team_id") REFERENCES "teams"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "user_sessions" ADD CONSTRAINT "user_sessions_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "campaigns" ADD CONSTRAINT "campaigns_organization_id_fkey" FOREIGN KEY ("organization_id") REFERENCES "organizations"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "campaign_metrics" ADD CONSTRAINT "campaign_metrics_campaign_id_fkey" FOREIGN KEY ("campaign_id") REFERENCES "campaigns"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "calls" ADD CONSTRAINT "calls_organization_id_fkey" FOREIGN KEY ("organization_id") REFERENCES "organizations"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "calls" ADD CONSTRAINT "calls_agent_id_fkey" FOREIGN KEY ("agent_id") REFERENCES "users"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "calls" ADD CONSTRAINT "calls_supervisor_id_fkey" FOREIGN KEY ("supervisor_id") REFERENCES "users"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "contact_sessions" ADD CONSTRAINT "contact_sessions_call_id_fkey" FOREIGN KEY ("call_id") REFERENCES "calls"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "contact_sessions" ADD CONSTRAINT "contact_sessions_agent_id_fkey" FOREIGN KEY ("agent_id") REFERENCES "users"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "contact_sessions" ADD CONSTRAINT "contact_sessions_campaign_id_fkey" FOREIGN KEY ("campaign_id") REFERENCES "campaigns"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "call_transcripts" ADD CONSTRAINT "call_transcripts_call_id_fkey" FOREIGN KEY ("call_id") REFERENCES "calls"("id") ON DELETE CASCADE ON UPDATE CASCADE;
