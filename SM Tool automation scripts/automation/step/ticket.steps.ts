import { DataTable, Given, Then, When } from '@cucumber/cucumber';
import { expect } from '@playwright/test';
import path from 'path';
import { OpsWorld } from '../support/world';
import { ROOT, Role, users } from '../support/config';
import { Actor } from '../modal/actor';
import {
  attachmentFile, buildTicket, changeFields, dialogFields, kbSearchTerm, resolution, routing, TicketType, uniqueSubject, xssPayload,
} from '../modal/ticket/ticket.data';

const statusRe = (s: string) => new RegExp(s.replace(/fulfilment/i, 'fulfil(l)?ment').replace(/fulfilled/i, 'fulfil(l)?ed'), 'i');

async function openCurrent(world: OpsWorld, role: Role): Promise<Actor> {
  const a = await world.actor(role);
  expect(world.ticket, 'no ticket created in this scenario').toBeTruthy();
  await a.openTicket(world.ticket!.number, world.ticket!.url);
  return a;
}

export async function assignToEmployee(world: OpsWorld) {
  const manager = await openCurrent(world, 'manager');
  await manager.ticket.assign(routing.employeeTeam || undefined, users.employee!.displayName);
  expect(await manager.ticket.selectedText(/^assignee$/i)).toBe(users.employee!.displayName);
}

// ---------- creation --------------------------------------------------------

When('the {role} raises a new {ticketType}', async function (this: OpsWorld, role: Role, type: TicketType) {
  if (!this.hasCredential(role)) return 'skipped';
  this.ticket = await (await this.actor(role)).newTicket.create(buildTicket(type));
});

Given('a new {ticketType} raised by the {role}', async function (this: OpsWorld, type: TicketType, role: Role) {
  if (!this.hasCredential(role)) return 'skipped';
  this.ticket = await (await this.actor(role)).newTicket.create(buildTicket(type));
  this.attach(`Created ${this.ticket.number} (${this.ticket.url})`, 'text/plain');
});

/** Raised with no team and no category so routing leaves it unassigned. */
Given('a new unassigned incident raised by the {role}', async function (this: OpsWorld, role: Role) {
  if (!this.hasCredential(role)) return 'skipped';
  this.ticket = await (await this.actor(role)).newTicket.create(buildTicket('Incident', 'UNASSIGNED'));
  this.attach(`Created ${this.ticket.number} (${this.ticket.url})`, 'text/plain');
});

Given('a new {ticketType} raised by the {role} and assigned to the employee', async function (this: OpsWorld, type: TicketType, role: Role) {
  if (!this.hasCredential(role) || !this.hasCredential('employee')) return 'skipped';
  this.ticket = await (await this.actor(role)).newTicket.create(buildTicket(type));
  await assignToEmployee(this);
  this.attach(`Created ${this.ticket.number} and assigned it to the employee`, 'text/plain');
});

When('the {role} raises a new incident whose subject contains a script payload', async function (this: OpsWorld, role: Role) {
  const a = await this.actor(role);
  this.scratch.dialogFired = false;
  a.page.on('dialog', async (d) => { this.scratch.dialogFired = true; await d.dismiss(); });
  const subject = `${xssPayload} ${uniqueSubject('XSS')}`;
  this.scratch.subject = subject;
  this.ticket = await a.newTicket.create({ ...buildTicket('Incident'), subject });
});

When('the {role} raises {int} incidents in a row', async function (this: OpsWorld, role: Role, count: number) {
  if (!this.hasCredential(role)) return 'skipped';
  const a = await this.actor(role);
  const numbers: number[] = [];
  for (let i = 0; i < count; i++) numbers.push(Number((await a.newTicket.create(buildTicket('Incident', `SEQ${i}`))).number.replace(/\D/g, '')));
  this.scratch.numbers = numbers;
  this.attach(`Ticket numbers: ${numbers.join(', ')}`, 'text/plain');
});

Then('the ticket numbers are strictly increasing', function (this: OpsWorld) {
  const n = this.scratch.numbers as number[];
  for (let i = 1; i < n.length; i++) expect(n[i]).toBeGreaterThan(n[i - 1]);
  if (n[n.length - 1] - n[0] !== n.length - 1) this.attach('Gap observed - re-run when no other users are creating incidents (gap-free check needs a quiet environment).', 'text/plain');
});

Then('the ticket number starts with {string}', function (this: OpsWorld, prefix: string) {
  expect(this.ticket!.number.startsWith(prefix), `${this.ticket!.number} should start with ${prefix}`).toBe(true);
});

// ---------- new ticket form -------------------------------------------------

When('the {role} opens the new ticket form', async function (this: OpsWorld, role: Role) {
  await (await this.actor(role)).newTicket.open();
});

When('the {role} opens the new ticket form for a/an {ticketType}', async function (this: OpsWorld, role: Role, type: TicketType) {
  const a = await this.actor(role);
  await a.newTicket.open();
  await a.newTicket.chooseType(type);
});

Then('the ticket types offered to the {role} are:', async function (this: OpsWorld, role: Role, table: DataTable) {
  const offered = (await (await this.actor(role)).newTicket.typeOptions()).join(' | ');
  this.attach(`Offered types: ${offered}`, 'text/plain');
  for (const row of table.hashes()) {
    const re = new RegExp(row.type, 'i');
    if (row.offered === 'yes') expect(offered, `${row.type} should be offered`).toMatch(re);
    else expect(offered, `${row.type} must not be offered`).not.toMatch(re);
  }
});

Then('the {role} sees the form fields:', async function (this: OpsWorld, role: Role, table: DataTable) {
  const a = await this.actor(role);
  for (const [label] of table.raw()) {
    await expect(a.page.getByLabel(new RegExp(label, 'i')).first(), `field "${label}"`).toBeVisible();
  }
});

When('the {role} submits the form with an empty subject and description', async function (this: OpsWorld, role: Role) {
  const a = await this.actor(role);
  await a.newTicket.el.submit.click();
});

Then('the {role} sees a validation message and the form is not submitted', async function (this: OpsWorld, role: Role) {
  const a = await this.actor(role);
  expect(await a.newTicket.hasValidationError()).toBe(true);
  // still on the form: the Summary field's accessible name gains the error text, so check the page instead
  await expect(a.newTicket.el.heading).toBeVisible();
  expect(new URL(a.page.url()).pathname).toBe('/new');
});

When('the {role} types the knowledge search term into the subject', async function (this: OpsWorld, role: Role) {
  await (await this.actor(role)).newTicket.el.subject.pressSequentially(kbSearchTerm, { delay: 50 });
});

Then('the {role} sees knowledge-base suggestions', async function (this: OpsWorld, role: Role) {
  const el = (await this.actor(role)).newTicket.el;
  await expect(el.kbSuggestionsPanel).toBeVisible();
  await expect(el.kbSuggestionLinks.first(), 'matching articles / past fixes should be listed').toBeVisible({ timeout: 15_000 });
});

Then('the payload is displayed as text and no script runs for the {role}', async function (this: OpsWorld, role: Role) {
  const a = await openCurrent(this, role);
  a.page.on('dialog', async (d) => { this.scratch.dialogFired = true; await d.dismiss(); });
  await expect(a.page.getByText(this.scratch.subject as string).first()).toBeVisible();
  await a.page.waitForTimeout(1000);
  expect(this.scratch.dialogFired, 'injected script must not execute').toBe(false);
});

// ---------- visibility ------------------------------------------------------

When('the {role} opens the ticket', async function (this: OpsWorld, role: Role) {
  await openCurrent(this, role);
});

Then('the {role} can see the ticket', async function (this: OpsWorld, role: Role) {
  expect(await (await this.actor(role)).list.contains(this.ticket!.number), `${role} should see ${this.ticket!.number}`).toBe(true);
});

Then('the {role} cannot see the ticket in the list', async function (this: OpsWorld, role: Role) {
  expect(await (await this.actor(role)).list.contains(this.ticket!.number), `${role} must not see ${this.ticket!.number}`).toBe(false);
});

Then('the {role} cannot open the ticket by its URL', async function (this: OpsWorld, role: Role) {
  const a = await this.actor(role);
  await a.page.goto(this.ticket!.url);
  await a.ticket.settle();
  await expect(a.page.getByText(this.ticket!.number), `${role} must not be able to open ${this.ticket!.number}`).toBeHidden();
});

// ---------- status & workflow -----------------------------------------------

Then('the ticket status is {string}', async function (this: OpsWorld, status: string) {
  const role = (this.scratch.lastRole as Role) ?? 'customer';
  const a = await this.actor(role);
  await a.page.reload();
  await a.ticket.expectStatus(statusRe(status));
});

Then('the {role} sees the ticket status {string}', async function (this: OpsWorld, role: Role, status: string) {
  const a = await openCurrent(this, role);
  await a.ticket.expectStatus(statusRe(status));
});

Then('the {role} sees the ticket came via {string}', async function (this: OpsWorld, role: Role, channel: string) {
  const a = await openCurrent(this, role);
  await expect(a.ticket.el.detail.getByText(new RegExp(`^${channel}$`, 'i')).first()).toBeVisible();
});

When('the {role} performs {string}', async function (this: OpsWorld, role: Role, action: string) {
  const a = await openCurrent(this, role);
  this.scratch.lastRole = role;
  // Comment boxes are filled only when the action's dialog shows one.
  this.scratch.lastActionCompleted = await a.ticket.perform(action, {}, { [dialogFields.comment]: 'QA automation comment' });
});

When('the {role} performs {string} with:', async function (this: OpsWorld, role: Role, action: string, table: DataTable) {
  const a = await openCurrent(this, role);
  this.scratch.lastRole = role;
  this.scratch.lastActionCompleted = await a.ticket.perform(action, table.rowsHash());
});

When('the {role} tries to perform {string} without the required details', async function (this: OpsWorld, role: Role, action: string) {
  const a = await openCurrent(this, role);
  this.scratch.lastRole = role;
  this.scratch.statusBefore = await a.ticket.status();
  this.scratch.lastActionCompleted = await a.ticket.perform(action, {});
});

Then('the action is blocked and the status is unchanged', async function (this: OpsWorld) {
  const a = await this.actor(this.scratch.lastRole as Role);
  const blocked = this.scratch.lastActionCompleted === false || (await a.ticket.hasValidationError());
  await a.page.reload();
  await a.ticket.settle();
  expect(await a.ticket.status(), 'status must not change').toBe(this.scratch.statusBefore);
  expect(blocked, 'the app should refuse the action').toBe(true);
});

When('the {role} resolves the ticket with a resolution code and notes', async function (this: OpsWorld, role: Role) {
  const a = await openCurrent(this, role);
  this.scratch.lastRole = role;
  this.scratch.lastActionCompleted = await a.ticket.perform('Resolve', {
    [dialogFields.resolutionCode]: resolution.code,
    [dialogFields.resolutionNotes]: resolution.notes,
  });
});

When('the {role} fulfils the request with resolution notes', async function (this: OpsWorld, role: Role) {
  const a = await openCurrent(this, role);
  this.scratch.lastRole = role;
  this.scratch.lastActionCompleted = await a.ticket.perform('Fulfil', { [dialogFields.resolutionNotes]: resolution.notes });
});

Then('the {role} does not have the {string} action', async function (this: OpsWorld, role: Role, action: string) {
  const a = await openCurrent(this, role);
  expect(await a.ticket.hasAction(action), `${role} must not have "${action}"`).toBe(false);
});

Then('the {role} has the {string} action', async function (this: OpsWorld, role: Role, action: string) {
  const a = await openCurrent(this, role);
  expect(await a.ticket.hasAction(action), `${role} should have "${action}"`).toBe(true);
});

Then('the ticket is flagged as a major incident', async function (this: OpsWorld) {
  const a = await this.actor('manager');
  await a.page.reload();
  await expect(a.page.getByText(/major incident/i).first()).toBeVisible();
  expect(await a.ticket.hasAction('Declare major incident'), 'declare action should no longer be offered').toBe(false);
});

// ---------- communication ---------------------------------------------------

When('the {role} sends a public reply', async function (this: OpsWorld, role: Role) {
  const a = await openCurrent(this, role);
  this.scratch.publicReply = uniqueSubject('public reply');
  await a.ticket.reply(this.scratch.publicReply as string, false);
});

When('the {role} adds an internal note', async function (this: OpsWorld, role: Role) {
  const a = await openCurrent(this, role);
  this.scratch.internalNote = uniqueSubject('INTERNAL note');
  await a.ticket.reply(this.scratch.internalNote as string, true);
});

Then('the {role} sees the public reply', async function (this: OpsWorld, role: Role) {
  const a = await openCurrent(this, role);
  await expect(a.page.getByText(this.scratch.publicReply as string).first()).toBeVisible();
});

Then('the {role} does not see the internal note', async function (this: OpsWorld, role: Role) {
  const a = await openCurrent(this, role);
  await a.ticket.openHistory().catch(() => {});
  await expect(a.page.getByText(this.scratch.internalNote as string)).toHaveCount(0);
});

Then('the {role} cannot write an internal note', async function (this: OpsWorld, role: Role) {
  const a = await openCurrent(this, role);
  expect(await a.ticket.canWriteInternalNote()).toBe(false);
});

When('the {role} attaches the sample file', async function (this: OpsWorld, role: Role) {
  const a = await openCurrent(this, role);
  await a.ticket.attach(path.join(ROOT, attachmentFile));
});

Then('the attachment is listed on the ticket', async function (this: OpsWorld) {
  const a = await openCurrent(this, 'employee');
  await a.page.reload();
  await a.ticket.settle();
  await expect(a.page.getByText(path.basename(attachmentFile)).first()).toBeVisible();
});

// ---------- fields ----------------------------------------------------------

When('the {role} changes the {string} field to {string}', async function (this: OpsWorld, role: Role, label: string, value: string) {
  const a = await openCurrent(this, role);
  await a.ticket.setField(new RegExp(label, 'i'), value);
  this.scratch.changedField = label;
});

When('the {role} edits the subject', async function (this: OpsWorld, role: Role) {
  const a = await openCurrent(this, role);
  const subject = uniqueSubject('EDITED');
  await a.ticket.setField(/subject|title/i, subject);
  this.scratch.subject = subject;
});

Then('the new subject is saved', async function (this: OpsWorld) {
  const a = await this.actor((this.scratch.lastRole as Role) ?? 'customer');
  await a.page.reload();
  await expect(a.page.getByText(this.scratch.subject as string).first()).toBeVisible();
});

Then('the {role} cannot edit the fields:', async function (this: OpsWorld, role: Role, table: DataTable) {
  const a = await openCurrent(this, role);
  for (const [label] of table.raw()) {
    expect(await a.ticket.isFieldEditable(new RegExp(`^${label}$`, 'i')), `${role} must not edit ${label}`).toBe(false);
  }
});

Then('the ticket history records the {string} change', async function (this: OpsWorld, field: string) {
  const a = await this.actor((this.scratch.lastRole as Role) ?? 'manager');
  await a.page.reload();
  await a.ticket.settle();
  await a.ticket.openHistory();
  await expect(a.ticket.el.activityEntry(new RegExp(`changed .*${field}`, 'i')).first()).toBeVisible();
});

Then('the {role} sees a history entry with user and time', async function (this: OpsWorld, role: Role) {
  const a = await openCurrent(this, role);
  await a.ticket.openHistory();
  // Activity log rows read "<d Mon yyyy, hh:mm> <user> <what changed>"
  await expect(a.ticket.el.activityEntry(/^\d{1,2} \w{3} \d{4}, \d{2}:\d{2}$/).first()).toBeVisible();
  await expect(a.ticket.el.activityEntry(/changed .*assignee/i).first()).toBeVisible();
});

// ---------- change stage fields --------------------------------------------

When('the {role} fills the change fields:', async function (this: OpsWorld, role: Role, table: DataTable) {
  const a = await openCurrent(this, role);
  for (const [label] of table.raw()) await a.ticket.setField(new RegExp(label, 'i'), changeFields[label]);
});

// ---------- SLA -------------------------------------------------------------

Then('the SLA is shown as paused', async function (this: OpsWorld) {
  const a = await this.actor(this.scratch.lastRole as Role);
  await a.page.reload();
  await a.ticket.settle();
  this.attach(`SLA bars: ${await a.ticket.slaText()}`, 'text/plain');
  await expect(a.ticket.el.resolutionSla).toHaveAccessibleName(/paused/i);
});

Then('the SLA is not shown as paused', async function (this: OpsWorld) {
  const a = await this.actor(this.scratch.lastRole as Role);
  await a.page.reload();
  await a.ticket.settle();
  this.attach(`SLA bars: ${await a.ticket.slaText()}`, 'text/plain');
  await expect(a.ticket.el.resolutionSla).toBeVisible();
  await expect(a.ticket.el.resolutionSla).not.toHaveAccessibleName(/paused/i);
});

Then('the ticket has no SLA timer', async function (this: OpsWorld) {
  const a = await openCurrent(this, 'manager');
  this.attach(`SLA bars: ${(await a.ticket.slaText()) || '(none)'}`, 'text/plain');
  await expect(a.ticket.el.slaBars).toHaveCount(0);
});

Then('the response SLA is {string}', async function (this: OpsWorld, state: string) {
  const a = await openCurrent(this, 'employee');
  this.attach(`SLA bars: ${await a.ticket.slaText()}`, 'text/plain');
  if (state === 'met') await expect(a.ticket.el.responseSla).toHaveAccessibleName(/first response met/i);
  else await expect(a.ticket.el.responseSla).not.toHaveAccessibleName(/first response met/i);
});

When('the {role} records the SLA due dates', async function (this: OpsWorld, role: Role) {
  const a = await openCurrent(this, role);
  this.scratch.dueBefore = await a.ticket.slaText();
});

Then('the SLA due dates are recalculated', async function (this: OpsWorld) {
  const a = await this.actor('manager');
  await a.page.reload();
  await a.ticket.settle();
  const after = await a.ticket.slaText();
  this.attach(`before: ${this.scratch.dueBefore}\nafter: ${after}`, 'text/plain');
  expect(after, 'SLA targets should change after priority override').not.toBe(this.scratch.dueBefore);
});

// ---------- priority --------------------------------------------------------

When('the manager sets impact {int} and urgency {int}', async function (this: OpsWorld, impact: number, urgency: number) {
  const a = await openCurrent(this, 'manager');
  this.scratch.lastRole = 'manager';
  await a.ticket.setField(/impact/i, String(impact));
  await a.ticket.setField(/urgency/i, String(urgency));
});

Then('the ticket priority is {string}', async function (this: OpsWorld, priority: string) {
  const a = await this.actor('manager');
  await a.page.reload();
  await a.ticket.settle();
  expect(await a.ticket.priority()).toMatch(new RegExp(`^${priority}\\b`));
});
