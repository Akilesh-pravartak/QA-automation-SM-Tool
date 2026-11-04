import { expect } from '@playwright/test';
import { Page } from 'playwright';
import { BasePage } from '../common/common.page';
import { loginModal } from './login.modal';
import { Credential } from '../../support/config';

export class LoginPage extends BasePage {
  readonly el;
  constructor(page: Page) {
    super(page);
    this.el = loginModal(page);
  }

  async open() {
    await this.page.goto('/');
    await expect(this.el.password).toBeVisible();
  }

  async submit(email: string, password: string) {
    if (email) await this.el.email.fill(email);
    if (password) await this.el.password.fill(password);
    await this.el.submit.click();
    await this.settle();
  }

  async loginAs(user: Pick<Credential, 'email' | 'password'>) {
    await this.open();
    await this.submit(user.email, user.password);
    await expect(this.el.password, `sign-in failed for ${user.email}`).toBeHidden({ timeout: 30_000 });
  }

  async logout() {
    if (!(await this.el.signOut.isVisible().catch(() => false)) && (await this.el.userMenu.isVisible().catch(() => false))) {
      await this.el.userMenu.click();
    }
    await this.el.signOut.click();
    await expect(this.el.password).toBeVisible();
  }

  async errorText() {
    await expect(this.el.error).toBeVisible();
    return (await this.el.error.innerText()).trim();
  }

  async isOnSignIn() {
    return this.el.password.isVisible().catch(() => false);
  }
}
