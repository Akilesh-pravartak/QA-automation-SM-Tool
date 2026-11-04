import testdata from '../../fixture/testdata.json';

export type TicketType = 'Incident' | 'Service Request' | 'Change';

export interface NewTicket {
  type: TicketType;
  subject: string;
  description?: string;
  category?: string;
  /** Staff must pick an account on the new-ticket form; defaults to testdata.staffTicketAccount. */
  account?: string;
  /** "Route automatically" unless set. */
  team?: string;
  impact?: number;
  urgency?: number;
  /** Type-specific fields keyed by label text. */
  fields?: Record<string, string>;
}

export interface CreatedTicket {
  number: string;
  url: string;
}

export const ticketNumberRe = /\b(INC|REQ|CHG|PRB)-?\d+\b/;

/** Unique, searchable subject; the prefix makes clean-up of automation data easy. */
export const uniqueSubject = (label: string) =>
  `${testdata.subjectPrefix} ${label} ${new Date().toISOString().replace(/[-:TZ.]/g, '').slice(0, 14)}-${Math.floor(Math.random() * 1000)}`;

export function buildTicket(type: TicketType, label?: string): NewTicket {
  const src = type === 'Incident' ? testdata.incident : type === 'Change' ? testdata.change : testdata.serviceRequest;
  return {
    type,
    subject: uniqueSubject(label ?? type.replace(' ', '')),
    description: src.description,
    // Change fields are filled at the stage that needs them, not on creation.
    fields: type === 'Change' ? {} : { ...src.fields },
  };
}

export const staffTicketAccount = testdata.staffTicketAccount;
export const changeFields = testdata.change.fields as Record<string, string>;
export const resolution = testdata.resolution;
export const routing = testdata.routing;
export const xssPayload = testdata.xssPayload;
export const kbSearchTerm = testdata.kbSearchTerm;
export const attachmentFile = testdata.attachmentFile;

/** Default priority matrix (Doc §6): P1 sum ≤ 3, P2 = 4, P3 5–6, P4 7–8. */
export const expectedPriority = (impact: number, urgency: number) => {
  const s = impact + urgency;
  return s <= 3 ? 'P1' : s === 4 ? 'P2' : s <= 6 ? 'P3' : 'P4';
};

/** Workflow action buttons in the ticket header (live build: Resume, Resolve, Cancel, Approved - fulfil, Reject, ...). */
export const actions: Record<string, RegExp> = {
  'Start work': /^start work$|^start progress$/i,
  'Ask customer': /^ask customer$/i,
  'Wait on third party': /third party/i,
  Resume: /^resume$/i,
  Resolve: /^resolve$/i,
  Cancel: /^cancel$/i,
  'Confirm close': /^confirm( close)?$|^close ticket$/i,
  Reopen: /^reopen$/i,
  'Send for approval': /^send for approval$/i,
  'Approve and fulfil': /^approved? - fulfil$/i,
  'Start fulfilment': /^start fulfil(l)?ment$|^approved? - fulfil$/i,
  Fulfil: /^fulfil(l)?$|^mark fulfil/i,
  'Submit for assessment': /submit for assessment/i,
  'Send to CAB': /cab|change.?board/i,
  Reject: /^reject$/i,
  Close: /^close$/i,
  'Declare major incident': /^declare major incident$/i,
  'Create KB draft': /^create kb draft$/i,
};

/** Dialog field labels used by the workflow actions. */
export const dialogFields = {
  resolutionCode: 'resolution code',
  resolutionNotes: 'resolution notes|notes',
  comment: 'comment|reason',
};
