import { After, AfterAll, AfterStep, Before, BeforeAll, setDefaultTimeout, Status } from '@cucumber/cucumber';
import { chromium, firefox, webkit } from 'playwright';
import { env } from './config';
import { OpsWorld } from './world';

setDefaultTimeout(env.stepTimeoutMs);

BeforeAll(async function () {
  const launcher = env.browser === 'firefox' ? firefox : env.browser === 'webkit' ? webkit : chromium;
  OpsWorld.browser = await launcher.launch({
    headless: env.headless,
    channel: env.browser === 'msedge' ? 'msedge' : undefined,
  });
});

AfterAll(async function () {
  await OpsWorld.browser?.close();
});

/** Scenarios needing a credential that was not supplied are skipped, not failed. */
Before({ tags: '@customer' }, function (this: OpsWorld) {
  if (!this.hasCredential('customer')) return 'skipped';
});
Before({ tags: '@teamlead' }, function (this: OpsWorld) {
  if (!this.hasCredential('teamlead')) return 'skipped';
});
Before({ tags: '@superadmin' }, function (this: OpsWorld) {
  if (!this.hasCredential('superadmin')) return 'skipped';
});

/**
 * Evidence for every Gherkin step: a screenshot of the page the step acted on, shown in the
 * HTML report as a collapsible "screenshot" link under the step. JPEG viewport captures keep
 * the self-contained report small. Steps that use no browser page (e.g. HTTP header checks) get none.
 */
AfterStep(async function (this: OpsWorld) {
  const page = this.activePage;
  if (!page || page.isClosed() || page.url() === 'about:blank') return;
  const shot = await page.screenshot({ type: 'jpeg', quality: 60, timeout: 5_000 }).catch(() => undefined);
  if (shot) this.attach(shot, { mediaType: 'image/jpeg', fileName: 'screenshot' });
});

After(async function (this: OpsWorld, { result }) {
  if (result?.status === Status.FAILED) {
    for (const page of this.allPages()) {
      const png = await page.screenshot({ fullPage: true, timeout: 10_000 }).catch(() => undefined);
      if (png) this.attach(png, { mediaType: 'image/png', fileName: 'failure screenshot (full page)' });
      this.attach(`URL at failure: ${page.url()}`, 'text/plain');
    }
  }
  await this.dispose();
});
