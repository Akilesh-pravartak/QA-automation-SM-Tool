import { Page } from 'playwright';

export const loginModal = (page: Page) => ({
  email: page.getByLabel(/e-?mail|username/i).or(page.locator('input[type="email"], input[name*="email" i]')).first(),
  password: page.getByLabel(/password/i).or(page.locator('input[type="password"]')).first(),
  submit: page.getByRole('button', { name: /sign in|log ?in|continue/i }).first(),
  error: page.getByText(/invalid|incorrect|wrong|failed|not recogni[sz]ed|try again|too many/i).first(),
  userMenu: page.getByRole('button', { name: /account|profile|user menu|avatar/i }).first(),
  signOut: page.getByRole('menuitem', { name: /sign out|log ?out/i })
    .or(page.getByRole('button', { name: /sign out|log ?out/i }))
    .or(page.getByRole('link', { name: /sign out|log ?out/i }))
    .first(),
  portalLanding: page.getByText(/new request|new ticket|my tickets|my requests|raise/i).first(),
  dashboardLanding: page.getByText(/dashboard/i).first(),
});
