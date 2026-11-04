import { Given, Then, When } from '@cucumber/cucumber';
import { expect } from '@playwright/test';
import { OpsWorld } from '../support/world';
import { Role, users } from '../support/config';
import { buildTicket, routing } from '../modal/ticket/ticket.data';
import { assignToEmployee } from './ticket.steps';

When('the manager assigns the ticket to the employee', async function (this: OpsWorld) {
  this.scratch.lastRole = 'manager';
  await assignToEmployee(this);
});

Given('a category that routes to a team is configured', function (this: OpsWorld) {
  if (!routing.routedCategory || !routing.routedTeam) {
    this.attach('Set routing.routedCategory / routedTeam in fixture/testdata.json to run this scenario.', 'text/plain');
    return 'skipped';
  }
});

When('the {role} raises a new incident in the routed category', async function (this: OpsWorld, role: Role) {
  const a = await this.actor(role);
  this.ticket = await a.newTicket.create({ ...buildTicket('Incident'), category: routing.routedCategory });
});

Then('the {role} sees the ticket routed to that team', async function (this: OpsWorld, role: Role) {
  const a = await this.actor(role);
  await a.openTicket(this.ticket!.number, this.ticket!.url);
  await expect(a.page.getByText(new RegExp(routing.routedTeam, 'i')).first()).toBeVisible();
});

Then('the ticket is listed in the {role}\'s unassigned queue', async function (this: OpsWorld, role: Role) {
  const a = await this.actor(role);
  expect(await a.list.contains(this.ticket!.number, 'unassigned'), `${this.ticket!.number} should be in the ${role}'s Unassigned queue`).toBe(true);
});

Then('the employee\'s unassigned queue lists no tickets', async function (this: OpsWorld) {
  const a = await this.actor('employee');
  await a.list.open('unassigned');
  const nums = await a.list.numbers();
  this.attach(`Employee Unassigned queue: ${nums.join(', ') || '(empty)'}`, 'text/plain');
  expect(nums, 'employees must not see unassigned tickets').toEqual([]);
});

Then('every ticket in the employee\'s open list is assigned to the employee', async function (this: OpsWorld) {
  const a = await this.actor('employee');
  await a.list.open('open');
  const open = await a.list.numbers();
  await a.list.open('mine');
  const mine = new Set(await a.list.numbers());
  this.attach(`All open: ${open.join(', ') || '(none)'}\nAssigned to me: ${[...mine].join(', ') || '(none)'}`, 'text/plain');
  // Tickets the employee raised would also be visible; none are raised by the employee in this suite.
  expect(open.filter((n) => !mine.has(n)), 'open tickets not assigned to the employee').toEqual([]);
});

Then('the {role} sees the same open tickets as the manager', async function (this: OpsWorld, role: Role) {
  const other = await this.actor(role);
  const manager = await this.actor('manager');
  await Promise.all([other.list.open('open'), manager.list.open('open')]);
  const [a, b] = await Promise.all([other.list.numbers(), manager.list.numbers()]);
  this.attach(`${role}: ${a.join(', ')}\nmanager: ${b.join(', ')}`, 'text/plain');
  expect(a.sort()).toEqual(b.sort());
});

Then('the assignee list offers the employee once the employee\'s team is selected', async function (this: OpsWorld) {
  const a = await this.actor('manager');
  await a.openTicket(this.ticket!.number, this.ticket!.url);
  if (!routing.employeeTeam) {
    this.attach('routing.employeeTeam not set in fixture/testdata.json - team filter not exercised.', 'text/plain');
    return 'skipped';
  }
  await a.ticket.fillByLabel(/^team$/i, routing.employeeTeam);
  const options = await a.ticket.assigneeOptions();
  this.attach(`Assignees for team ${routing.employeeTeam}: ${options.join(', ')}`, 'text/plain');
  expect(options.join('|').toLowerCase()).toContain(users.employee!.displayName.toLowerCase());
  expect(options.length, 'list should be filtered to the team').toBeGreaterThan(0);
});

Then('the ticket history shows the assignment', async function (this: OpsWorld) {
  const a = await this.actor('manager');
  await a.page.reload();
  await a.ticket.settle();
  await a.ticket.openHistory();
  await expect(a.ticket.el.activityEntry(/changed (team, )?assignee/i).first()).toBeVisible();
});
