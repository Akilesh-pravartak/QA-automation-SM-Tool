/** Dashboard content from Doc §8. Names are matched as regexes. */
export const kpiCards: Record<string, RegExp> = {
  'Open now': /open now/i,
  'Open and breached': /open and breached|breached/i,
  'At risk': /at risk/i,
  'SLA met': /sla met/i,
  'Avg first response': /avg\.? first response|average first response/i,
  'Mean time to resolve': /mean time to resolve|mttr/i,
  CSAT: /csat/i,
  'AI suggestions accepted': /ai suggestions accepted/i,
};

export const charts: Record<string, RegExp> = {
  'Created vs resolved': /created vs\.? resolved/i,
  'Backlog age': /backlog age/i,
  'Intake by channel': /intake by channel/i,
  'Open by priority': /open by priority/i,
  'Accounts this period': /accounts this period/i,
  'Open by team': /open by team/i,
};

export const periods = [7, 30, 90] as const;
