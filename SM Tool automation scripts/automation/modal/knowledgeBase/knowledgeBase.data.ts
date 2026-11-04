import { uniqueSubject } from '../ticket/ticket.data';

export const newArticle = () => ({
  title: uniqueSubject('KB'),
  body: 'Automated knowledge-base article created by OpsDesk QA automation. Safe to delete.',
  editedBody: 'Edited by OpsDesk QA automation.',
});
