import { Page } from 'playwright';

export const knowledgeBaseModal = (page: Page) => ({
  heading: page.getByRole('heading', { name: /knowledge|articles|help/i }).first(),
  search: page.getByRole('searchbox', { name: /search articles/i }),
  // Articles are buttons labelled "<title> <audience> <n> views updated <when>"
  articleLinks: page.getByRole('button', { name: / views? updated /i }),
  customerVisibleArticles: page.getByRole('button', { name: /customers and agents/i }),
  articleBody: page.getByRole('article').or(page.getByRole('main')).first(),
  helpfulVote: page.getByRole('button', { name: /helpful|yes|👍|thumbs up|upvote/i }).first(),
  voteConfirmation: page.getByText(/thanks|thank you|recorded|voted/i).first(),
  newArticle: page.getByRole('button', { name: /new article|create article|add article/i })
    .or(page.getByRole('link', { name: /new article|create article|add article/i })).first(),
  title: page.getByLabel(/title/i).first(),
  body: page.getByLabel(/body|content/i).or(page.locator('[contenteditable="true"]')).first(),
  save: page.getByRole('button', { name: /save|publish|create/i }).first(),
  edit: page.getByRole('button', { name: /^edit/i }).or(page.getByRole('link', { name: /^edit/i })).first(),
  remove: page.getByRole('button', { name: /delete|remove/i }).first(),
  confirm: page.getByRole('dialog').getByRole('button', { name: /delete|confirm|yes|ok/i }).last(),
});
