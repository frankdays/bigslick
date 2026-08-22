---
name: crm-conventions
description: Establish and enforce the client's CRM and marketing-ops conventions — lifecycle stages, lead scoring, campaign naming, required fields, and data hygiene. Use when the user mentions "lifecycle stages", "lead scoring", "campaign naming", "CRM hygiene", "HubSpot setup/cleanup", "data quality", "UTM conventions", "required fields", or when reports are untrustworthy because the underlying data is messy. Works with the upstream hubspot skill (tool how-to) — this skill owns the client's RULES.
---
# CRM & Marketing-Ops Conventions
Read the active client pack. This skill writes and maintains `crm-conventions.md` in the client pack — the single place the client's ops rules live. Definitions of funnel stages defer to `metrics-baseline.md`; this file covers everything operational around them.

## What the conventions file must contain
1. **Lifecycle model:** the stages, entry/exit criteria per stage, who/what moves records (automation vs. human), and the reverse paths (recycle, disqualify) — most CRMs rot because nothing ever moves backward.
2. **Scoring:** what adds points (fit + behavior separately), thresholds that trigger routing, decay rules, and the quarterly re-validation: score bands vs. actual conversion (a score that doesn't predict conversion is theater — fix or delete).
3. **Naming conventions:** campaigns `YYYY-Qx_channel_program_asset`, UTMs (source/medium dictionary — pick ONE spelling per source), lists, and workflows. Publish the dictionary; reject nonconforming names in review, not after launch.
4. **Required fields by object:** the minimum on contact/company/deal for reporting to work (source, segment, loss reason from `win-loss-program` taxonomy) — and no more; every optional-but-required field breeds fake data.
5. **Hygiene cadence:** monthly dedupe pass, quarterly decay review (bounced/unengaged), ownership of each job by name.

## Rollout reality
Sales ops co-signs everything touching their objects — conventions imposed unilaterally get ignored. Migrate incrementally: fix naming going forward + patch the top reporting-breaking fields historically; a full historical cleanup is rarely worth it. Enforce at creation time (templates, required fields, workflow validation) rather than by audit — audits catch what prevention would have stopped.

## Audit mode
When asked to assess an existing instance: pull structure via the CRM MCP (via resource-hub), score against the checklist above, and deliver: top 5 reporting-breaking issues (ranked by which reports they corrupt), quick wins vs. structural fixes, and the conventions file draft.

For external LLM or API capabilities, load the `resource-hub` skill and follow its routing.
