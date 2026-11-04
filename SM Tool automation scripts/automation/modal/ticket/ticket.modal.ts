import { Page } from 'playwright';
import { ticketNumberRe } from './ticket.data';

/** Status chip values shown in the ticket header. */
export const STATUS_WORDS = /^(new|in progress|waiting on customer|waiting on third party|resolved|closed|cancelled|rejected|awaiting approval|in fulfil(l)?ment|fulfil(l)?ed|draft|assessment|cab review|scheduled|implementing|post-implementation review|root cause analysis|known error)$/i;

/** New ticket form (/new). Type choices are radios rendered as a segmented control. */
export const newTicketModal = (page: Page) => ({
  heading: page.getByRole('heading', { name: /^new ticket$/i }),
  typeRadio: (name: RegExp) => page.getByRole('radio', { name }).first(),
  typeRadios: page.getByRole('radio'),
  subject: page.getByLabel(/^summary$/i).first(),
  description: page.getByLabel(/^details$/i).first(),
  account: page.getByLabel(/^account$/i).first(),
  submit: page.getByRole('button', { name: /^create ticket$/i }),
  createdNumber: page.getByRole('region', { name: /ticket detail/i }).getByText(ticketNumberRe).first(),
  kbSuggestionsPanel: page.getByRole('heading', { name: /similar past tickets/i }),
  kbSuggestionLinks: page.getByRole('heading', { name: /similar past tickets/i }).locator('xpath=ancestor::*[2]').getByRole('link'),
});

/** Ticket queues (/tickets?view=...). Each ticket is a button labelled "Select ticket <number> ...". */
export const ticketListModal = (page: Page) => ({
  heading: page.getByRole('heading').first(),
  search: page.getByRole('searchbox', { name: /search tickets/i }),
  rows: page.getByRole('button', { name: /^Select ticket / }),
  row: (num: string) => page.getByRole('button', { name: new RegExp(`^Select ticket ${num}\\b`) }).first(),
  emptyState: page.getByText(/^nothing here$/i),
});

/** Ticket detail (/tickets/<id>). */
export const ticketDetailModal = (page: Page) => {
  const detail = page.getByRole('region', { name: /ticket detail/i });
  return {
    detail,
    number: detail.getByText(ticketNumberRe).first(),
    action: (name: RegExp) => detail.getByRole('button', { name }).first(),
    dialogConfirm: page.getByRole('dialog').getByRole('button', {
      name: /confirm|save|submit|resolve|fulfil|cancel ticket|reopen|ok|apply|send|yes|reject|close|declare/i,
    }).last(),
    status: detail.getByText(STATUS_WORDS).first(),
    pausedChip: detail.getByText(/^paused$/i).first(),
    responseSla: detail.getByRole('progressbar', { name: /first response/i }),
    resolutionSla: detail.getByRole('progressbar', { name: /resolution/i }),
    slaBars: detail.getByRole('progressbar'),
    majorIncidentFlag: detail.getByText(/^major incident$/i).locator('xpath=following::*[1]'),
    publicReplyToggle: detail.getByRole('button', { name: /^public reply$/i }),
    internalNoteToggle: detail.getByRole('button', { name: /^internal note$/i }),
    composer: detail.getByRole('textbox', { name: /^message$/i }),
    sendReply: detail.getByRole('button', { name: /^send reply$/i }),
    attachButton: detail.getByRole('button', { name: /^attach$/i }),
    fileInput: page.locator('input[type="file"]').first(),
    activityHeading: detail.getByRole('heading', { name: /activity log/i }),
    activityEntry: (text: RegExp) => detail.getByText(text),
    text: (t: string) => detail.getByText(t).first(),
    field: (label: RegExp) => detail.getByLabel(label).first(),
  };
};
