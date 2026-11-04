import { Given, Then } from '@cucumber/cucumber';
import { expect } from '@playwright/test';
import { OpsWorld } from '../support/world';
import { Role } from '../support/config';
import { NavKey, RouteKey } from '../modal/common/common.data';

/** Page names used in feature files -> direct routes (fixture/routes.json). */
const PAGE_ROUTES: Record<string, RouteKey> = {
  Dashboard: 'dashboard',
  Tickets: 'tickets',
  Reports: 'reports',
  Administration: 'admin',
  'Users administration': 'adminUsers',
  'Audit log': 'auditLog',
  'New change form': 'newChange',
};

const MENUS: Record<string, NavKey> = {
  Dashboard: 'dashboard',
  Tickets: 'tickets',
  Reports: 'reports',
  'Knowledge base': 'knowledgeBase',
  Administration: 'admin',
};

Given('the {role} is signed in', async function (this: OpsWorld, role: Role) {
  if (!this.hasCredential(role)) return 'skipped';
  await this.actor(role);
});

Then('the signed-in user is shown with the role {string}', async function (this: OpsWorld, roleLabel: string) {
  const page = this.anonymous ?? (await this.anonymousPage());
  await expect(page.getByRole('link', { name: new RegExp(`\\b${roleLabel}$`, 'i') }).first()).toBeVisible();
});

Then('the {role} does not see the {string} menu', async function (this: OpsWorld, role: Role, menu: string) {
  const a = await this.actor(role);
  await a.page.goto('/dashboard');
  await a.dashboard.settle();
  expect(await a.dashboard.isMenuVisible(MENUS[menu]), `${menu} menu should be hidden for ${role}`).toBe(false);
});

Then('the {role} sees the {string} menu', async function (this: OpsWorld, role: Role, menu: string) {
  const a = await this.actor(role);
  expect(await a.dashboard.isMenuVisible(MENUS[menu]), `${menu} menu should be visible for ${role}`).toBe(true);
});

Then('the {role} is denied access to the {string} page', async function (this: OpsWorld, role: Role, pageName: string) {
  const a = await this.actor(role);
  const key = PAGE_ROUTES[pageName];
  expect(key, `unknown page "${pageName}"`).toBeTruthy();
  expect(await a.dashboard.isDeniedAt(key), `${role} should be denied ${pageName}; page rendered at ${a.page.url()}`).toBe(true);
});

Then('the {role} can open the {string} page', async function (this: OpsWorld, role: Role, pageName: string) {
  const a = await this.actor(role);
  expect(await a.dashboard.isDeniedAt(PAGE_ROUTES[pageName]), `${role} should be able to open ${pageName}`).toBe(false);
});
