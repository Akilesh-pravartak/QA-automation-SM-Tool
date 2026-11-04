import routesJson from '../../fixture/routes.json';

export type RouteKey = Exclude<keyof typeof routesJson, '_comment'>;
export const routes = routesJson as Record<RouteKey, string>;

/** Sidebar link names (regex). Queue links carry a live count, e.g. "All open 13". */
export const navNames = {
  dashboard: /^dashboard$/i,
  tickets: /^all open\b/i,
  unassigned: /^unassigned\b/i,
  mine: /^assigned to me\b/i,
  newTicket: /^new ticket$/i,
  reports: /^dashboard$/i, // exports live on the dashboard
  knowledgeBase: /^knowledge base$/i,
  admin: /^administration$|^admin$/i,
} as const;
export type NavKey = keyof typeof navNames;

/**
 * Content that proves a protected page actually rendered. Non-admins opening /admin are shown
 * a ticket queue at the same URL, so a redirect check alone is not enough.
 */
export const routeMarkers: Partial<Record<RouteKey, RegExp>> = {
  dashboard: /^dashboard$/i,
  admin: /^(administration|users|configuration|settings)$/i,
  adminUsers: /^users$/i,
  auditLog: /^audit( log)?$/i,
};

export const deniedText = /access denied|forbidden|not authori[sz]ed|permission|not found|404|403|don't have access/i;
export const validationText = /required|cannot be (empty|blank)|please (enter|fill|provide)|is invalid|must |^add a short summary/i;
