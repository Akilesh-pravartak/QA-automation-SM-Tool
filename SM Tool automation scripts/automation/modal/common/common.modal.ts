import { Page } from 'playwright';
import { deniedText, validationText } from './common.data';

/** Locators shared by every screen. The sidebar has no navigation landmark, so links are matched page-wide. */
export const commonModal = (page: Page) => ({
  navItem: (name: RegExp) => page.getByRole('link', { name }).first(),
  pageHeading: (name: RegExp) => page.getByRole('heading', { name }).first(),
  roleBadge: page.getByRole('link', { name: /\b(customer|employee|team_lead|manager|super_?admin)$/i }).first(),
  deniedMessage: page.getByText(deniedText).first(),
  validationMessage: page.getByText(validationText).first(),
  toast: page.getByRole('alert').or(page.getByRole('status')).first(),
  dialog: page.getByRole('dialog'),
  option: (name: RegExp) => page.getByRole('option', { name }).first(),
});
