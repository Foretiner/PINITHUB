CREATE EXTENSION IF NOT EXISTS vector;

CREATE TYPE "BioSubjectStatus" AS ENUM ('ACTIVE', 'DELETION_PENDING', 'DELETED');
CREATE TYPE "EnrollmentStatus" AS ENUM ('OPEN', 'PROCESSING', 'COMPLETED', 'EXPIRED', 'FAILED');
CREATE TYPE "EnrollmentDecision" AS ENUM ('CREATED', 'DUPLICATE', 'REVIEW', 'RETRY');
CREATE TYPE "ReviewStatus" AS ENUM ('PENDING', 'APPROVED', 'REJECTED');

CREATE TABLE bio_subjects (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id text NOT NULL UNIQUE,
  status "BioSubjectStatus" NOT NULL DEFAULT 'ACTIVE',
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE face_templates (
  subject_id uuid PRIMARY KEY REFERENCES bio_subjects(id) ON DELETE CASCADE,
  model_version text NOT NULL,
  ciphertext bytea NOT NULL,
  iv bytea NOT NULL,
  auth_tag bytea NOT NULL,
  wrapped_key bytea NOT NULL,
  quality real,
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE face_search_vectors (
  subject_id uuid PRIMARY KEY REFERENCES bio_subjects(id) ON DELETE CASCADE,
  model_version text NOT NULL,
  embedding vector(512) NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX face_search_hnsw ON face_search_vectors USING hnsw (embedding vector_cosine_ops) WITH (m=16, ef_construction=100);
CREATE INDEX face_search_model_version ON face_search_vectors(model_version);
CREATE TABLE enrollment_sessions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(), nonce_hash text NOT NULL, consent_notice_version text NOT NULL, consented_at timestamptz NOT NULL DEFAULT now(), challenge text NOT NULL,
  status "EnrollmentStatus" NOT NULL DEFAULT 'OPEN', decision "EnrollmentDecision",
  device_hash text, ip_hash text, expires_at timestamptz NOT NULL, created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX enrollment_sessions_status_expiry ON enrollment_sessions(status, expires_at);
CREATE TABLE duplicate_reviews (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(), session_id uuid NOT NULL REFERENCES enrollment_sessions(id) ON DELETE CASCADE,
  candidate_subject_id uuid NOT NULL REFERENCES bio_subjects(id) ON DELETE CASCADE,
  status "ReviewStatus" NOT NULL DEFAULT 'PENDING', reviewer_ids text[] NOT NULL DEFAULT '{}',
  created_at timestamptz NOT NULL DEFAULT now(), decided_at timestamptz,
  CHECK (cardinality(reviewer_ids) <= 2)
);
CREATE INDEX duplicate_reviews_status_created ON duplicate_reviews(status, created_at);
CREATE TABLE passkey_credentials (
  credential_id text PRIMARY KEY, subject_id uuid NOT NULL REFERENCES bio_subjects(id) ON DELETE CASCADE,
  public_key bytea NOT NULL, counter bigint NOT NULL DEFAULT 0, transports text[] NOT NULL DEFAULT '{}',
  created_at timestamptz NOT NULL DEFAULT now(), revoked_at timestamptz
);
CREATE INDEX passkeys_subject_revoked ON passkey_credentials(subject_id, revoked_at);
CREATE TABLE webauthn_challenges (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(), subject_id uuid, challenge text NOT NULL, purpose text NOT NULL,
  expires_at timestamptz NOT NULL, created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX webauthn_challenges_expiry ON webauthn_challenges(expires_at);
CREATE TABLE biometric_consents (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(), subject_id uuid NOT NULL REFERENCES bio_subjects(id) ON DELETE CASCADE,
  purpose text NOT NULL, notice_version text NOT NULL, granted_at timestamptz NOT NULL DEFAULT now(), withdrawn_at timestamptz
);
CREATE INDEX biometric_consents_subject_purpose ON biometric_consents(subject_id, purpose);
CREATE TABLE bio_events (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(), subject_id uuid REFERENCES bio_subjects(id) ON DELETE SET NULL,
  event text NOT NULL, outcome text NOT NULL, reason text, created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX bio_events_created ON bio_events(created_at);

-- RLS is enabled. Browser-facing roles receive no access to biometric tables.
DO $$ DECLARE t text; BEGIN
  FOREACH t IN ARRAY ARRAY['bio_subjects','face_templates','face_search_vectors','enrollment_sessions','duplicate_reviews','passkey_credentials','webauthn_challenges','biometric_consents','bio_events'] LOOP
    EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY', t);
  END LOOP;
END $$;

