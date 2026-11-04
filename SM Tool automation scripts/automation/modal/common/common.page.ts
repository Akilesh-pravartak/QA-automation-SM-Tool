import { expect } from '@playwright/test';
import { Page } from 'playwright';
import { commonModal } from './common.modal';
import { navNames, NavKey, RouteKey, routeMarkers, routes } from './common.data';

export const escapeRe = (s: string) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

export class BasePage {
  readonly common;
  constructor(readonly page: Page) {
    this.common = commonModal(page);
  }

  /**
   * OpsDesk keeps a live event stream open, so 'networkidle' never fires (each wait would burn
   * its full timeout). Wait for the DOM, then give the SPA a moment to render.
   */
  async settle(ms = 1200) {
    await this.page.waitForLoadState('domcontentloaded').catch(() => {});
    await this.page.waitForTimeout(ms);
  }

  /** Navigate by sidebar link where available, falling back to the direct route. */
  async openSection(key: NavKey & RouteKey) {
    const item = this.common.navItem(navNames[key]);
    if (await item.isVisible().catch(() => false)) await item.click();
    else await this.page.goto(routes[key]);
    await this.settle();
  }

  async isMenuVisible(key: NavKey) {
    return this.common.navItem(navNames[key]).isVisible().catch(() => false);
  }

  /**
   * Opens a route directly and reports whether it was refused: redirected away, a denial
   * message, or the page's own content (routeMarkers) did not render.
   */
  async isDeniedAt(key: RouteKey): Promise<boolean> {
    const target = routes[key].split('?')[0];
    await this.page.goto(routes[key]);
    await this.settle(2000);
    if (!new URL(this.page.url()).pathname.startsWith(target)) return true;
    if (await this.common.deniedMessage.isVisible().catch(() => false)) return true;
    const marker = routeMarkers[key];
    if (marker) return !(await this.common.pageHeading(marker).isVisible().catch(() => false));
    return false;
  }

  /** A visible validation message, a field flagged aria-invalid (OpsDesk's pattern), or native constraint failure. */
  async hasValidationError(): Promise<boolean> {
    if (await this.common.validationMessage.isVisible().catch(() => false)) return true;
    if (await this.page.locator('[aria-invalid="true"]').count()) return true;
    return this.page.evaluate(() =>
      Array.from(document.querySelectorAll('input, textarea, select')).some((el) => !(el as HTMLInputElement).checkValidity()),
    );
  }

  /**
   * Fill an input, textarea or select located by its label. Selects accept the exact option
   * label, an option starting with the value (e.g. "2" -> "2 - Department / many users"),
   * or an option containing it.
   */
  async fillByLabel(label: RegExp, value: string) {
    const field = this.page.getByLabel(label).first();
    await expect(field, `field ${label} not found`).toBeVisible();
    const tag = await field.evaluate((el) => el.tagName.toLowerCase());
    if (tag === 'select') {
      const options = (await field.locator('option').allInnerTexts()).map((o) => o.trim());
      const lc = value.toLowerCase();
      const pick = options.find((o) => o.toLowerCase() === lc)
        ?? options.find((o) => new RegExp(`^${escapeRe(lc)}\\b`).test(o.toLowerCase()))
        ?? options.find((o) => o.toLowerCase().includes(lc));
      expect(pick, `no option matching "${value}" in ${label} (options: ${options.join(' | ')})`).toBeTruthy();
      await field.selectOption({ label: pick! });
    } else if ((await field.getAttribute('role')) === 'combobox') {
      await field.click();
      await field.fill(value).catch(() => {});
      await this.common.option(new RegExp(escapeRe(value), 'i')).click();
    } else {
      await field.fill(value);
    }
  }

  /** Selected option text of a labelled select. */
  async selectedText(label: RegExp) {
    const field = this.page.getByLabel(label).first();
    return (await field.evaluate((el) => (el as HTMLSelectElement).selectedOptions?.[0]?.text ?? (el as HTMLInputElement).value)).trim();
  }
}
