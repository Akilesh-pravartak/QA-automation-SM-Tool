import { expect } from '@playwright/test';
import { Page } from 'playwright';
import { BasePage } from '../common/common.page';
import { dashboardModal } from './dashboard.modal';
import { charts, kpiCards } from './dashboard.data';

export class DashboardPage extends BasePage {
  readonly el;
  constructor(page: Page) {
    super(page);
    this.el = dashboardModal(page);
  }

  async open() {
    await this.openSection('dashboard');
    await expect(this.el.heading).toBeVisible();
  }

  widgetLocator(name: string) {
    const re = kpiCards[name] ?? charts[name];
    if (!re) throw new Error(`Unknown dashboard widget "${name}" (modal/dashboard/dashboard.data.ts)`);
    return this.el.widget(re);
  }

  async selectPeriod(days: number) {
    const btn = this.el.periodButton(days);
    if (await btn.isVisible().catch(() => false)) await btn.click();
    else if ((await this.el.periodControl.evaluate((el) => el.tagName.toLowerCase())) === 'select') {
      const label = (await this.el.periodControl.locator('option', { hasText: String(days) }).first().innerText()).trim();
      await this.el.periodControl.selectOption({ label });
    } else {
      await this.el.periodControl.click();
      await this.common.option(new RegExp(String(days))).click();
    }
    await this.settle();
    await expect(this.el.errorBanner).toBeHidden();
  }

  async selectFirstAccount() {
    const f = this.el.accountFilter;
    await expect(f).toBeVisible();
    if ((await f.evaluate((el) => el.tagName.toLowerCase())) === 'select') {
      const opts = await f.locator('option').allInnerTexts();
      const pick = opts.find((o) => o.trim() && !/all/i.test(o));
      expect(pick, 'at least one account to filter by').toBeTruthy();
      await f.selectOption({ label: pick!.trim() });
    } else {
      await f.click();
      await this.page.getByRole('option').filter({ hasNotText: /all/i }).first().click();
    }
    await this.settle();
    await expect(this.el.errorBanner).toBeHidden();
  }
}
