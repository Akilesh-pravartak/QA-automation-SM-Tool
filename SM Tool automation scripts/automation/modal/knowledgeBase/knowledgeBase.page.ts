import { expect } from '@playwright/test';
import { Page } from 'playwright';
import { BasePage } from '../common/common.page';
import { routes } from '../common/common.data';
import { knowledgeBaseModal } from './knowledgeBase.modal';

export class KnowledgeBasePage extends BasePage {
  readonly el;
  constructor(page: Page) {
    super(page);
    this.el = knowledgeBaseModal(page);
  }

  async open() {
    await this.openSection('knowledgeBase');
    if (!(await this.el.heading.isVisible().catch(() => false))) await this.page.goto(routes.knowledgeBase);
    await expect(this.el.heading).toBeVisible();
  }

  async openFirstArticle() {
    await expect(this.el.articleLinks.first(), 'at least one published article').toBeVisible();
    await this.el.articleLinks.first().click();
    await this.settle();
  }

  async create(title: string, body: string) {
    await this.el.newArticle.click();
    await this.el.title.fill(title);
    await this.el.body.fill(body);
    await this.el.save.click();
    await this.settle();
    await expect(this.page.getByText(title).first()).toBeVisible();
  }

  async editBody(body: string) {
    await this.el.edit.click();
    await this.el.body.fill(body);
    await this.el.save.click();
    await this.settle();
    await expect(this.page.getByText(body).first()).toBeVisible();
  }

  async remove() {
    await this.el.remove.click();
    if (await this.el.confirm.isVisible({ timeout: 3_000 }).catch(() => false)) await this.el.confirm.click();
    await this.settle();
  }
}
