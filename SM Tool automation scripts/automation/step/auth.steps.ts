import { Given, Then, When } from '@cucumber/cucumber';
import { expect } from '@playwright/test';
import { OpsWorld } from '../support/world';
import { Role, users } from '../support/config';
import { LoginPage } from '../modal/login/login.page';
import { loginData } from '../modal/login/login.data';
import { routes } from '../modal/common/common.data';

async function loginPage(world: OpsWorld) {
  return new LoginPage(await world.anonymousPage());
}

Given('I am on the sign-in page', async function (this: OpsWorld) {
  await (await loginPage(this)).open();
});

When('I sign in as the {role}', async function (this: OpsWorld, role: Role) {
  const user = users[role];
  if (!user) return 'skipped';
  await (await loginPage(this)).submit(user.email, user.password);
});

When('I sign in as the {role} with the email in upper case', async function (this: OpsWorld, role: Role) {
  const user = users[role]!;
  await (await loginPage(this)).submit(user.email.toUpperCase(), user.password);
});

When('I sign in with the {role} email and a wrong password', async function (this: OpsWorld, role: Role) {
  const lp = await loginPage(this);
  await lp.submit(users[role]!.email, loginData.wrongPassword);
  this.scratch.wrongPasswordMessage = await lp.errorText();
});

When('I sign in with an unregistered email', async function (this: OpsWorld) {
  const lp = await loginPage(this);
  await lp.open();
  await lp.submit(loginData.unregisteredEmail(), loginData.wrongPassword);
});

When('I submit the sign-in form with email {string} and password {string}', async function (this: OpsWorld, email: string, password: string) {
  const lp = await loginPage(this);
  await lp.open();
  await lp.submit(email, password);
});

Then('I land on the customer portal', async function (this: OpsWorld) {
  const lp = await loginPage(this);
  await expect(lp.el.password).toBeHidden({ timeout: 30_000 });
  await expect(lp.el.portalLanding).toBeVisible();
});

Then('I land on the dashboard', async function (this: OpsWorld) {
  const lp = await loginPage(this);
  await expect(lp.el.password).toBeHidden({ timeout: 30_000 });
  await expect(lp.el.dashboardLanding).toBeVisible();
});

Then('a sign-in error is shown and I remain on the sign-in page', async function (this: OpsWorld) {
  const lp = await loginPage(this);
  await expect(lp.el.error).toBeVisible();
  await expect(lp.el.password).toBeVisible();
});

Then('the error message is the same as for a wrong password', async function (this: OpsWorld) {
  const msg = await (await loginPage(this)).errorText();
  expect(msg, 'messages must not reveal whether an account exists').toBe(this.scratch.wrongPasswordMessage);
});

Then('sign-in validation is shown', async function (this: OpsWorld) {
  const lp = await loginPage(this);
  expect(await lp.hasValidationError()).toBe(true);
  await expect(lp.el.password).toBeVisible();
});

Then('the password field is masked', async function (this: OpsWorld) {
  await expect((await loginPage(this)).el.password).toHaveAttribute('type', 'password');
});

When('the {role} signs out', async function (this: OpsWorld, role: Role) {
  const a = await this.actor(role);
  // Visit two protected pages so "Back" has a protected page to return to
  // (sign-out replaces the current history entry rather than adding one).
  await a.page.goto(routes.dashboard);
  await a.dashboard.settle();
  await a.page.goto(routes.tickets);
  await a.dashboard.settle();
  await a.login.logout();
});

Then('the {role} cannot return to a protected page using Back or reload', async function (this: OpsWorld, role: Role) {
  const a = await this.actor(role);
  await a.page.goBack();
  await a.login.settle();
  expect(a.page.url(), 'Back should return to the previous protected page').toContain(routes.dashboard);
  expect(await a.login.isOnSignIn(), 'Back must not restore the session').toBe(true);
  await a.page.reload();
  await a.login.settle();
  expect(await a.login.isOnSignIn(), 'reload must not restore the session').toBe(true);
  expect(await a.page.evaluate(() => localStorage.getItem('opsdesk.auth')), 'token removed on sign-out').toBeNull();
  await a.page.goto(routes.dashboard);
  expect(await a.login.isOnSignIn()).toBe(true);
});

Then('opening the {string} page without signing in shows the sign-in page', async function (this: OpsWorld, pageName: string) {
  const page = await this.anonymousPage();
  const route = pageName === 'Dashboard' ? routes.dashboard : routes.tickets;
  await page.goto(route);
  await expect(new LoginPage(page).el.password).toBeVisible();
});
