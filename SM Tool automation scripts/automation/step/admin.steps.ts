import { DataTable, Then, When } from '@cucumber/cucumber';
import { expect } from '@playwright/test';
import { OpsWorld } from '../support/world';
import { users } from '../support/config';

When('the super admin opens each Administration section:', async function (this: OpsWorld, table: DataTable) {
  const admin = (await this.actor('superadmin')).admin;
  await admin.open();
  for (const [section] of table.raw()) await admin.openSectionByName(section);
});

Then('the Users screen has no create or invite option', async function (this: OpsWorld) {
  const admin = (await this.actor('superadmin')).admin;
  await admin.openUsers();
  await expect(admin.el.createUser).toBeHidden();
});

Then('the super admin account row has no edit, deactivate or reset actions', async function (this: OpsWorld) {
  const admin = (await this.actor('superadmin')).admin;
  await admin.openUsers();
  const row = admin.el.userRow(users.superadmin!.email);
  await expect(row).toBeVisible();
  await expect(admin.el.rowActions(row)).toHaveCount(0);
});

When('the super admin searches the audit log for the ticket', async function (this: OpsWorld) {
  await (await this.actor('superadmin')).admin.searchAudit(this.ticket!.number);
});

Then('matching audit entries are listed', async function (this: OpsWorld) {
  const admin = (await this.actor('superadmin')).admin;
  await expect(admin.page.getByText(this.ticket!.number).first()).toBeVisible();
});

Then('the audit entries offer no edit or delete controls', async function (this: OpsWorld) {
  await expect((await this.actor('superadmin')).admin.el.auditEditControls).toHaveCount(0);
});
