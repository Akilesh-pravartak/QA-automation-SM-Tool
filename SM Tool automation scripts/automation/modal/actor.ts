import { Page } from 'playwright';
import { Role, users } from '../support/config';
import { LoginPage } from './login/login.page';
import { NewTicketPage, TicketDetailPage, TicketListPage } from './ticket/ticket.page';
import { DashboardPage } from './dashboard/dashboard.page';
import { ReportsPage } from './reports/reports.page';
import { KnowledgeBasePage } from './knowledgeBase/knowledgeBase.page';
import { AdminPage } from './admin/admin.page';

/** One signed-in user and every page object bound to their browser page. */
export class Actor {
  readonly login: LoginPage;
  readonly newTicket: NewTicketPage;
  readonly list: TicketListPage;
  readonly ticket: TicketDetailPage;
  readonly dashboard: DashboardPage;
  readonly reports: ReportsPage;
  readonly kb: KnowledgeBasePage;
  readonly admin: AdminPage;

  constructor(readonly role: Role, readonly page: Page) {
    this.login = new LoginPage(page);
    this.newTicket = new NewTicketPage(page);
    this.list = new TicketListPage(page);
    this.ticket = new TicketDetailPage(page);
    this.dashboard = new DashboardPage(page);
    this.reports = new ReportsPage(page);
    this.kb = new KnowledgeBasePage(page);
    this.admin = new AdminPage(page);
  }

  get user() {
    return users[this.role]!;
  }

  /** Open a ticket: directly by URL when known, otherwise through the list search. */
  async openTicket(number: string, url?: string) {
    if (url) {
      await this.page.goto(url);
      await this.ticket.settle();
      if (await this.page.getByText(number).first().isVisible().catch(() => false)) return;
    }
    await this.list.openTicket(number);
  }
}
