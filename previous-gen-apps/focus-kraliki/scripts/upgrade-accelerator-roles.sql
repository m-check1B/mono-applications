-- Upgrade Accelerator Dev Accounts to SUPERVISOR role
-- Run this on Focus production database
-- Created: 2025-12-28 for Monday accelerator onboarding

-- Upgrade all accelerator devs to SUPERVISOR (Dev tier)
UPDATE users
SET role = 'SUPERVISOR'
WHERE email IN (
    'dev1@accelerator.kraliki.dev',
    'dev2@accelerator.kraliki.dev',
    'dev3@accelerator.kraliki.dev'
);

-- Verify the changes
SELECT id, email, username, role, status, "createdAt"
FROM users
WHERE email LIKE '%@accelerator.kraliki.dev'
ORDER BY email;

-- Expected output:
-- 3 rows with role = 'SUPERVISOR'
