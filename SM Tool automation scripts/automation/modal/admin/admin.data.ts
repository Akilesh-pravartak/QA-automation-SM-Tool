/** Administration sections (Doc §2, §7) — Super admin only. */
export const adminSections: Record<string, RegExp> = {
  Users: /users/i,
  Teams: /teams/i,
  'SLA policies': /sla/i,
  'Business hours': /business hours/i,
  Configuration: /configuration|workflows/i,
  'Inbound outbox': /outbox|inbound/i,
  'Audit log': /audit/i,
};
