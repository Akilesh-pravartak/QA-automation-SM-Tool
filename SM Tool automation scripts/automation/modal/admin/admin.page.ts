import { expect } from '@playwright/test';
import { Page } from 'playwright';
import { BasePage } from '../common/common.page';
import { routes } from '../common/common.data';
import { adminModal } from './admin.modal';
import { adminSections } from './admin.data';

export class AdminPage extends BasePage {
  readonly el;
  constructor(page: Page) {
    super(page);
    this.el = adminModal(page);
  }

  async open() {
    await this.openSection('admin');
  }

  async openSectionByName(name: string) {
    const re = adminSections[name];
    await this.el.sectionLink(re).click();
    await this.settle();
    await expect(this.el.sectionHeading(re)).toBeVisible();
  }

  async openUsers() {
    await this.page.goto(routes.adminUsers);
    await this.settle();
  }

  async searchAudit(text: string) {
    await this.page.goto(routes.auditLog);
    await this.settle();
    await this.el.auditSearch.fill(text);
    await this.el.auditSearch.press('Enter');
    await this.settle();
  }
}
