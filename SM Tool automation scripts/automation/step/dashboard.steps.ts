import { DataTable, Then, When } from '@cucumber/cucumber';
import { expect } from '@playwright/test';
import { OpsWorld } from '../support/world';
import { Role } from '../support/config';
import { periods } from '../modal/dashboard/dashboard.data';

When('the {role} opens the dashboard', async function (this: OpsWorld, role: Role) {
  await (await this.actor(role)).dashboard.open();
});

Then('the {role} sees the dashboard widgets:', async function (this: OpsWorld, role: Role, table: DataTable) {
  const d = (await this.actor(role)).dashboard;
  for (const [name] of table.raw()) await expect(d.widgetLocator(name), `widget "${name}"`).toBeVisible();
});

Then('the {role} does not see the dashboard widgets:', async function (this: OpsWorld, role: Role, table: DataTable) {
  const d = (await this.actor(role)).dashboard;
  for (const [name] of table.raw()) await expect(d.widgetLocator(name), `widget "${name}" must be hidden`).toBeHidden();
});

When('the {role} selects each dashboard period', async function (this: OpsWorld, role: Role) {
  const d = (await this.actor(role)).dashboard;
  for (const p of periods) await d.selectPeriod(p);
});

When('the {role} filters the dashboard by an account', async function (this: OpsWorld, role: Role) {
  await (await this.actor(role)).dashboard.selectFirstAccount();
});

Then('the dashboard shows no errors', async function (this: OpsWorld) {
  const d = (await this.actor((this.scratch.lastRole as Role) ?? 'manager')).dashboard;
  await expect(d.el.errorBanner).toBeHidden();
  await expect(d.widgetLocator('Open now')).toBeVisible();
});
