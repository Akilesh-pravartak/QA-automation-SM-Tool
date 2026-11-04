import { Then, When } from '@cucumber/cucumber';
import { expect } from '@playwright/test';
import { OpsWorld } from '../support/world';
import { Role } from '../support/config';
import { ReportsPage } from '../modal/reports/reports.page';
import { ExportFormat } from '../modal/reports/reports.data';

When('the {role} exports the {string} report as {string}', async function (this: OpsWorld, role: Role, report: string, format: ExportFormat) {
  const r = (await this.actor(role)).reports;
  await r.open();
  const download = await r.export(report, format);
  const info = await ReportsPage.verify(download, format);
  this.scratch.export = info;
  this.attach(`Downloaded ${info.name} (${info.size} bytes)`, 'text/plain');
});

Then('a valid non-empty {string} file is downloaded', function (this: OpsWorld, format: string) {
  const info = this.scratch.export as { name: string; size: number; valid: boolean };
  expect(info.size, 'export must not be empty').toBeGreaterThan(0);
  expect(info.valid, `${info.name} should be a valid ${format}`).toBe(true);
});

Then('the export does not contain the ticket', function (this: OpsWorld) {
  const info = this.scratch.export as { text: string };
  expect(info.text, `export must not include ${this.ticket!.number} (not visible to the viewer)`).not.toContain(this.ticket!.number);
});
