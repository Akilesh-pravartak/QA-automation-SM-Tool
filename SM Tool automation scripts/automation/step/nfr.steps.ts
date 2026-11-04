import { Then, When } from '@cucumber/cucumber';
import { expect } from '@playwright/test';
import { OpsWorld } from '../support/world';
import { env, Role } from '../support/config';
import testdata from '../fixture/testdata.json';

Then('the plain HTTP address redirects to HTTPS', async function (this: OpsWorld) {
  const page = await this.anonymousPage();
  const httpUrl = env.baseUrl.replace(/^https:/, 'http:') + '/';
  const res = await page.request.get(httpUrl, { maxRedirects: 0, failOnStatusCode: false });
  const location = res.headers()['location'] ?? '';
  this.attach(`GET ${httpUrl} -> ${res.status()} ${location}`, 'text/plain');
  expect([301, 302, 307, 308]).toContain(res.status());
  expect(location).toMatch(/^https:/);
});

Then('the {role} session cookie is Secure and HttpOnly', async function (this: OpsWorld, role: Role) {
  const a = await this.actor(role);
  const cookies = await a.page.context().cookies();
  this.attach(`Cookies: ${cookies.map((c) => `${c.name} secure=${c.secure} httpOnly=${c.httpOnly} sameSite=${c.sameSite}`).join('; ')}`, 'text/plain');
  const storageKeys = await a.page.evaluate(() =>
    Object.keys(localStorage).filter((k) => /auth|token|session|jwt/i.test(k) && /eyJ/.test(localStorage.getItem(k) ?? '')));
  this.attach(`localStorage keys holding a JWT: ${storageKeys.join(', ') || '(none)'}`, 'text/plain');
  const session = cookies.filter((c) => /sess|sid|auth|token|jwt/i.test(c.name));
  expect(storageKeys, 'auth tokens must not be readable by page scripts (localStorage is exposed to XSS)').toEqual([]);
  expect(session.length, 'session should be carried by a cookie').toBeGreaterThan(0);
  for (const c of session) {
    expect(c.secure, `${c.name} Secure`).toBe(true);
    expect(c.httpOnly, `${c.name} HttpOnly`).toBe(true);
  }
});

Then('the home page response includes security headers', async function (this: OpsWorld) {
  const page = await this.anonymousPage();
  const res = await page.request.get(env.baseUrl + '/', { headers: { 'ngrok-skip-browser-warning': '1' } });
  const h = res.headers();
  this.attach(JSON.stringify(h, null, 2), 'application/json');
  expect(!!h['content-security-policy'] || !!h['x-frame-options'], 'CSP or X-Frame-Options').toBe(true);
  expect(h['x-content-type-options']).toBe('nosniff');
});

When('the {role} loads the {string} page', async function (this: OpsWorld, role: Role, pageName: string) {
  const a = await this.actor(role);
  const start = Date.now();
  if (pageName === 'Dashboard') await a.dashboard.open();
  else await a.list.open();
  await a.page.waitForLoadState('load');
  this.scratch.loadMs = Date.now() - start;
  this.attach(`${pageName} load: ${this.scratch.loadMs} ms`, 'text/plain');
});

Then('the page loads within the performance budget', function (this: OpsWorld) {
  expect(this.scratch.loadMs as number, `budget ${testdata.loadBudgetMs} ms`).toBeLessThanOrEqual(testdata.loadBudgetMs);
});

// ---------- customer portal -------------------------------------------------

Then('the portal exposes a valid web app manifest', async function (this: OpsWorld) {
  const page = (await this.actor('customer')).page;
  const href = await page.locator('link[rel="manifest"]').first().getAttribute('href');
  expect(href, 'manifest link').toBeTruthy();
  const res = await page.request.get(new URL(href!, page.url()).toString());
  expect(res.ok()).toBe(true);
  const manifest = await res.json();
  expect(manifest.name || manifest.short_name).toBeTruthy();
  expect(Array.isArray(manifest.icons) && manifest.icons.length).toBeTruthy();
});

When('the customer uses a mobile viewport', async function (this: OpsWorld) {
  await (await this.actor('customer')).page.setViewportSize({ width: 375, height: 812 });
});

Then('the new request form fits the screen without horizontal scrolling', async function (this: OpsWorld) {
  const a = await this.actor('customer');
  await a.newTicket.open();
  const overflow = await a.page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
  expect(overflow, 'horizontal overflow in px').toBeLessThanOrEqual(1);
  await expect(a.newTicket.el.subject).toBeInViewport();
});
