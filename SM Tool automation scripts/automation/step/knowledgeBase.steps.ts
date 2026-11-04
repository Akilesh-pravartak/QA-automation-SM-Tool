import { Then, When } from '@cucumber/cucumber';
import { expect } from '@playwright/test';
import { OpsWorld } from '../support/world';
import { Role } from '../support/config';
import { newArticle } from '../modal/knowledgeBase/knowledgeBase.data';

When('the {role} opens the first published article', async function (this: OpsWorld, role: Role) {
  const kb = (await this.actor(role)).kb;
  await kb.open();
  await kb.openFirstArticle();
});

Then('the article content is readable', async function (this: OpsWorld) {
  await expect((await this.actor('customer')).kb.el.articleBody).not.toBeEmpty();
});

When('the {role} votes the article helpful', async function (this: OpsWorld, role: Role) {
  await (await this.actor(role)).kb.el.helpfulVote.click();
});

Then('the vote is recorded', async function (this: OpsWorld) {
  await expect((await this.actor('customer')).kb.el.voteConfirmation).toBeVisible();
});

When('the {role} creates, edits and deletes a knowledge article', async function (this: OpsWorld, role: Role) {
  const kb = (await this.actor(role)).kb;
  const art = newArticle();
  this.scratch.articleTitle = art.title;
  await kb.open();
  await kb.create(art.title, art.body);
  await kb.editBody(art.editedBody);
  await kb.remove();
});

Then('the article no longer exists', async function (this: OpsWorld) {
  const kb = (await this.actor('employee')).kb;
  await kb.open();
  await expect(kb.page.getByText(this.scratch.articleTitle as string)).toHaveCount(0);
});
