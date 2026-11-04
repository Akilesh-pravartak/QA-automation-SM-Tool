import { expect } from '@playwright/test';
import { Page } from 'playwright';
import { BasePage, escapeRe } from '../common/common.page';
import { routes } from '../common/common.data';
import { newTicketModal, ticketDetailModal, ticketListModal } from './ticket.modal';
import { actions, CreatedTicket, NewTicket, staffTicketAccount, ticketNumberRe, TicketType } from './ticket.data';

/** New-ticket form labels for impact / urgency (options after "Default" are levels 1..4). */
const IMPACT_LABEL = /how many people are affected/i;
const URGENCY_LABEL = /how urgent is it/i;

export class NewTicketPage extends BasePage {
  readonly el;
  constructor(page: Page) {
    super(page);
    this.el = newTicketModal(page);
  }

  async open() {
    await this.page.goto(routes.newTicket);
    await this.settle();
    await expect(this.el.subject).toBeVisible();
  }

  async typeOptions(): Promise<string[]> {
    const names: string[] = [];
    for (const r of await this.el.typeRadios.all()) names.push((await r.getAttribute('aria-label')) ?? (await r.evaluate((el) => (el as HTMLInputElement).labels?.[0]?.innerText ?? '')));
    return names;
  }

  async chooseType(type: TicketType) {
    const radio = this.el.typeRadio(new RegExp(`^${type}$`, 'i'));
    await radio.check({ force: true }); // native radio is visually hidden behind the segmented control
    await this.settle(400);
  }

  private async selectLevel(label: RegExp, level: number) {
    const field = this.page.getByLabel(label).first();
    const options = await field.locator('option').allInnerTexts();
    await field.selectOption({ label: options[level].trim() }); // index 0 is "Default"
  }

  async fill(t: NewTicket) {
    await this.chooseType(t.type);
    await this.el.subject.fill(t.subject);
    if (t.description !== undefined) await this.el.description.fill(t.description);
    const account = t.account ?? staffTicketAccount;
    if (account && (await this.el.account.isVisible().catch(() => false))) await this.fillByLabel(/^account$/i, account);
    if (t.category) await this.fillByLabel(/^category$/i, t.category);
    if (t.team) await this.fillByLabel(/^team$/i, t.team);
    if (t.impact) await this.selectLevel(IMPACT_LABEL, t.impact);
    if (t.urgency) await this.selectLevel(URGENCY_LABEL, t.urgency);
    for (const [label, value] of Object.entries(t.fields ?? {})) {
      await this.fillByLabel(new RegExp(`^${escapeRe(label)}`, 'i'), value);
    }
  }

  async create(t: NewTicket): Promise<CreatedTicket> {
    await this.open();
    await this.fill(t);
    await this.el.submit.click();
    await expect(this.el.createdNumber, 'ticket detail should open after creation').toBeVisible({ timeout: 30_000 });
    const number = (await this.el.createdNumber.innerText()).match(ticketNumberRe)![0];
    return { number, url: this.page.url().split('?')[0] };
  }
}

export class TicketListPage extends BasePage {
  readonly el;
  constructor(page: Page) {
    super(page);
    this.el = ticketListModal(page);
  }

  async open(view: 'open' | 'unassigned' | 'mine' = 'open') {
    await this.page.goto(`/tickets?view=${view}`);
    await this.settle(1800);
  }

  async search(text: string) {
    await this.el.search.fill(text);
    await this.settle(1500);
  }

  async numbers(): Promise<string[]> {
    const labels = await this.el.rows.evaluateAll((els) => els.map((e) => e.getAttribute('aria-label') || (e as HTMLElement).innerText));
    return labels.map((l) => (l.match(/[A-Z]{3}-\d+/) ?? [''])[0]).filter(Boolean);
  }

  async openTicket(number: string) {
    await this.open();
    await this.search(number);
    await this.el.row(number).click();
    await this.settle();
    await expect(this.page.getByRole('region', { name: /ticket detail/i }).getByText(number).first()).toBeVisible();
  }

  async contains(number: string, view: 'open' | 'unassigned' | 'mine' = 'open') {
    await this.open(view);
    await this.search(number);
    return this.el.row(number).isVisible().catch(() => false);
  }
}

export class TicketDetailPage extends BasePage {
  readonly el;
  constructor(page: Page) {
    super(page);
    this.el = ticketDetailModal(page);
  }

  private actionRe(name: string) {
    return actions[name] ?? new RegExp(`^${escapeRe(name)}$`, 'i');
  }

  async hasAction(name: string): Promise<boolean> {
    return this.el.action(this.actionRe(name)).isVisible().catch(() => false);
  }

  /**
   * Click a workflow action, fill any dialog fields and confirm.
   * Returns true when the action completed, false when the app refused it (dialog kept open or confirm disabled).
   */
  async perform(name: string, fields: Record<string, string> = {}, softFields: Record<string, string> = {}): Promise<boolean> {
    expect(await this.hasAction(name), `action "${name}" not available`).toBe(true);
    await this.el.action(this.actionRe(name)).click();
    if (!(await this.common.dialog.isVisible({ timeout: 3_000 }).catch(() => false))) {
      await this.settle();
      return true;
    }
    for (const [label, value] of Object.entries(fields)) await this.fillByLabel(new RegExp(label, 'i'), value);
    for (const [label, value] of Object.entries(softFields)) {
      if (await this.page.getByRole('dialog').getByLabel(new RegExp(label, 'i')).first().isVisible().catch(() => false)) {
        await this.fillByLabel(new RegExp(label, 'i'), value);
      }
    }
    // A confirm button disabled until required fields are filled counts as "blocked".
    if (!(await this.el.dialogConfirm.isEnabled().catch(() => false))) {
      await this.page.keyboard.press('Escape');
      return false;
    }
    await this.el.dialogConfirm.click();
    const closed = await this.common.dialog.isHidden({ timeout: 5_000 }).catch(() => false);
    if (!closed) await this.page.keyboard.press('Escape');
    await this.settle();
    return closed;
  }

  async status() {
    await expect(this.el.status).toBeVisible();
    return (await this.el.status.innerText()).trim();
  }

  async expectStatus(re: RegExp) {
    await expect(this.el.status).toHaveText(re, { timeout: 20_000 });
  }

  async reply(text: string, internal = false) {
    await (internal ? this.el.internalNoteToggle : this.el.publicReplyToggle).click();
    await this.el.composer.fill(text);
    await this.el.sendReply.click();
    await expect(this.el.text(text)).toBeVisible({ timeout: 20_000 });
  }

  async canWriteInternalNote() {
    return this.el.internalNoteToggle.isVisible().catch(() => false);
  }

  async attach(filePath: string) {
    await this.el.fileInput.setInputFiles(filePath);
    await this.settle(1500);
  }

  /** Property selects autosave on change. */
  async setField(label: RegExp, value: string) {
    await this.fillByLabel(label, value);
    await this.settle(1500);
  }

  async isFieldEditable(label: RegExp) {
    const f = this.el.field(label);
    if (!(await f.isVisible().catch(() => false))) return false;
    return f.isEditable().catch(() => false);
  }

  async assign(team: string | undefined, assignee: string) {
    if (team) await this.setField(/^team$/i, team);
    await this.setField(/^assignee$/i, assignee);
  }

  async assigneeOptions(): Promise<string[]> {
    return (await this.el.field(/^assignee$/i).locator('option').allInnerTexts()).map((o) => o.trim()).filter((o) => o && o !== 'None');
  }

  async priority() {
    return this.selectedText(/^priority$/i);
  }

  async openHistory() {
    await this.el.activityHeading.scrollIntoViewIfNeeded();
  }

  async slaText() {
    return (await this.el.slaBars.evaluateAll((els) => els.map((e) => e.getAttribute('aria-label') || (e as HTMLElement).innerText))).join(' | ');
  }
}
