import { defineParameterType } from '@cucumber/cucumber';
import { Role } from './config';

const ROLE_WORDS: Record<string, Role> = {
  customer: 'customer',
  employee: 'employee',
  manager: 'manager',
  'team lead': 'teamlead',
  'super admin': 'superadmin',
};

/** {role} — "customer", "employee", "manager", "team lead" or "super admin". */
defineParameterType({
  name: 'role',
  regexp: /customer|employee|manager|team lead|super admin/,
  transformer: (s: string) => ROLE_WORDS[s],
});

/** {ticketType} — "incident", "service request" or "change". */
defineParameterType({
  name: 'ticketType',
  regexp: /incident|service request|change/,
  transformer: (s: string) => (s === 'incident' ? 'Incident' : s === 'change' ? 'Change' : 'Service Request'),
});
