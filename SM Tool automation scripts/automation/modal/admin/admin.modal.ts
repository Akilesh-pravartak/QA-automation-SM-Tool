import { Page } from 'playwright';

export const adminModal = (page: Page) => ({
  sectionLink: (name: RegExp) => page.getByRole('link', { name }).or(page.getByRole('tab', { name })).first(),
  sectionHeading: (name: RegExp) => page.getByRole('heading', { name }).first(),
  createUser: page.getByRole('button', { name: /create user|new user|add user|invite/i })
    .or(page.getByRole('link', { name: /create user|new user|add user|invite/i })).first(),
  userRow: (email: string) => page.getByRole('row', { name: new RegExp(email, 'i') }).first(),
  rowActions: (row: ReturnType<Page['locator']>) => row.getByRole('button', { name: /edit|deactivate|reset/i }),
  auditSearch: page.getByRole('searchbox').or(page.getByPlaceholder(/search/i)).first(),
  auditRows: page.getByRole('row').filter({ hasText: /\d/ }),
  auditEditControls: page.getByRole('main').getByRole('button', { name: /^(edit|delete|remove)$/i }),
});
