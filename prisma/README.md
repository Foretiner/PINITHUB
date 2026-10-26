# Database

`schema.prisma` describes PostgreSQL records. The initial SQL migration enables pgvector, creates a 512-dimensional vector column and HNSW cosine index, and enables row-level security on biometric tables. Prisma accesses vectors through raw SQL. Apply only to a disposable local database until the schema and access model have been reviewed.

RLS is enabled with no browser-facing policies, so ordinary roles are denied by default. Production must use a restricted server role and explicitly review its privileges; do not expose service credentials to the web app.
