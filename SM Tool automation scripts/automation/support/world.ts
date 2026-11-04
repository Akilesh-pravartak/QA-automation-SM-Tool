import { IWorldOptions, setWorldConstructor, World } from '@cucumber/cucumber';
import { Browser, BrowserContext, Page } from 'playwright';
import fs from 'fs';
import path from 'path';
import { env, Role, storageStatePath, users } from './config';
import { Actor } from '../modal/actor';
import { LoginPage } from '../modal/login/login.page';
import { CreatedTicket } from '../modal/ticket/ticket.data';

const SESSION_MAX_AGE_MS = 30 * 60 * 1000;

export class OpsWorld extends World {
  static browser: Browser;

  private contexts: BrowserContext[] = [];
  private actors = new Map<Role, Actor>();
  /** Signed-out page for authentication scenarios. */
  anonymous?: Page;
  /** The page the most recent step acted on; screenshotted after every step. */
  activePage?: Page;
  /** Ticket created in the current scenario. */
  ticket?: CreatedTicket;
  /** Free-form values shared between steps of one scenario. */
  scratch: Record<string, unknown> = {};

  constructor(options: IWorldOptions) {
    super(options);
  }

  hasCredential(role: Role) {
    return !!users[role];
  }

  private async newContext(storageState?: string) {
    const ctx = await OpsWorld.browser.newContext({
      baseURL: env.baseUrl,
      storageState,
      acceptDownloads: true,
      ignoreHTTPSErrors: false,
      extraHTTPHeaders: { 'ngrok-skip-browser-warning': '1' }, // bypass ngrok free-tier interstitial
    });
    ctx.setDefaultTimeout(env.actionTimeoutMs);
    ctx.setDefaultNavigationTimeout(env.navigationTimeoutMs);
    const newPage = ctx.newPage.bind(ctx);
    ctx.newPage = async () => OpsWorld.domReadyNavigation(await newPage());
    this.contexts.push(ctx);
    return ctx;
  }

  /**
   * OpsDesk holds a live event stream open, and the 'load' event is not reliable through the
   * tunnel (navigations hung for minutes). Navigate to DOM-ready by default; BasePage.settle()
   * then waits for the SPA to render.
   */
  private static domReadyNavigation(page: Page): Page {
    const opts = <T extends object | undefined>(o: T) => ({ waitUntil: 'domcontentloaded' as const, ...(o ?? {}) });
    const goto = page.goto.bind(page);
    const reload = page.reload.bind(page);
    const goBack = page.goBack.bind(page);
    page.goto = (url, o) => goto(url, opts(o));
    page.reload = (o) => reload(opts(o));
    page.goBack = (o) => goBack(opts(o));
    return page;
  }

  async anonymousPage(): Promise<Page> {
    if (!this.anonymous) this.anonymous = await (await this.newContext()).newPage();
    this.activePage = this.anonymous;
    return this.anonymous;
  }

  /** A signed-in actor; the session is cached on disk and reused for 30 minutes. */
  async actor(role: Role): Promise<Actor> {
    const existing = this.actors.get(role);
    if (existing) {
      this.activePage = existing.page;
      return existing;
    }
    const user = users[role];
    if (!user) throw new Error(`No credential configured for role "${role}" (fixture/users.json)`);
    const state = storageStatePath(role);
    const fresh = fs.existsSync(state) && Date.now() - fs.statSync(state).mtimeMs < SESSION_MAX_AGE_MS;
    const ctx = await this.newContext(fresh ? state : undefined);
    const page = await ctx.newPage();
    if (fresh) {
      await page.goto('/');
    } else {
      await new LoginPage(page).loginAs(user);
      fs.mkdirSync(path.dirname(state), { recursive: true });
      await ctx.storageState({ path: state });
    }
    const actor = new Actor(role, page);
    this.actors.set(role, actor);
    this.activePage = page;
    return actor;
  }

  allPages(): Page[] {
    return this.contexts.flatMap((c) => c.pages());
  }

  async dispose() {
    for (const c of this.contexts) await c.close().catch(() => {});
    this.contexts = [];
    this.actors.clear();
    this.anonymous = undefined;
    this.activePage = undefined;
  }
}

setWorldConstructor(OpsWorld);
