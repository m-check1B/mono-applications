# Lab by Kraliki Billing Integration Plan (Stripe)

**Target:** Automated Stripe billing for VM rentals (EUR 299-499/mo)  
**Updated:** 2025-12-28

## 1. Pricing model decision

- Use Stripe subscriptions (monthly) as the default to maximize MRR.
- Offer annual billing as a discounted price on the same subscription (no new flow).
- Add a metered overage price for usage beyond plan budgets (compute + CLIProxy).

## 2. Products and prices (Stripe)

Product: Lab by Kraliki VM Rental

| Tier | Price | Included |
|------|-------|----------|
| **Starter** | EUR 299/mo | 1x Hetzner CPX31 VM, standard orchestration |
| **Pro** | EUR 499/mo | 1x Hetzner CPX31/41 VM, advanced patterns, priority support |

Product: Lab by Kraliki Usage Overage

- Metered unit: compute-unit-hour (CUH)
- Charge only when usage exceeds plan budget

## 3. Usage metering (CPX31 costs)

- Metric formula: (vCPU * hours) + (RAM_GB * hours * weight) + (disk_GB * hours * weight).
- Aggregation: daily job from provisioning logs + CLIProxy usage.
- Stripe writes: submit usage records daily; reconcile monthly invoices.
- Cost baseline: confirm CPX31 pricing and target margin >= 85%.

## 4. Integration architecture

Components:

1. Billing service (FastAPI or Node) to receive Stripe webhooks and persist billing state.
2. Provisioning worker that calls `scripts/provision.sh` or `scripts/create-vm.sh`.
3. Billing datastore (Postgres) for Stripe IDs + VM mappings.

Flow:

1. User selects plan on landing page (Stripe Payment Links or Checkout).
2. `checkout.session.completed` triggers provisioning and customer record creation.
3. Subscription status updates access (cancel/failed payment -> suspend).
4. Usage sync job pushes metered overage to Stripe.

## 5. Webhooks to handle

- `checkout.session.completed` -> provision VM and bind Stripe IDs.
- `customer.subscription.updated/deleted` -> suspend or de-provision access.
- `invoice.paid` / `invoice.payment_failed` -> update billing_status and notify.

## 6. Data to store

- account_id
- stripe_customer_id
- stripe_subscription_id
- plan_tier
- billing_status
- usage_budget_cuh
- last_usage_sync_at
- vm_id / provider_vm_id

## 7. Implementation steps

Phase 1: Stripe setup

- Create products/prices (flat + metered).
- Set up Payment Links and Customer Portal.

Phase 2: Billing service

- Implement webhook endpoint with signature verification.
- Persist Stripe IDs to billing datastore.
- Trigger provisioning queue on successful checkout.

Phase 3: Usage sync

- Build daily usage aggregation job.
- Push usage records to Stripe metered price.
- Add alerts for failed invoices and usage sync lag.

## 8. Open questions

- Budget per tier (included CUH and CLIProxy token limits).
- Billing cadence for usage (daily vs hourly).
- Final CPX31 cost inputs (compute, storage, traffic).
