import * as dotenv from 'dotenv';
import path from 'path';
import usersJson from '../fixture/users.json';

export const ROOT = path.resolve(__dirname, '..');
dotenv.config({ path: path.join(ROOT, '.env') });

export type Role = 'customer' | 'employee' | 'manager' | 'teamlead' | 'superadmin';

export interface Credential {
  role: Role;
  email: string;
  password: string;
  displayName: string;
}

const v = (k: string, d = '') => (process.env[k] ?? d).trim();

export const env = {
  baseUrl: v('OPSDESK_BASE_URL', 'https://retiree-crying-manhandle.ngrok-free.dev/').replace(/\/$/, ''),
  browser: v('BROWSER', 'chromium') as 'chromium' | 'firefox' | 'msedge' | 'webkit',
  headless: v('HEADLESS', 'true') !== 'false',
  stepTimeoutMs: 90_000,
  actionTimeoutMs: 15_000,
  navigationTimeoutMs: 45_000,
};

const ROLE_ENV: Record<Role, string> = {
  customer: 'CUSTOMER', employee: 'EMPLOYEE', manager: 'MANAGER', teamlead: 'TEAMLEAD', superadmin: 'SUPERADMIN',
};

function credential(role: Role): Credential | undefined {
  const u = (usersJson as unknown as Record<string, { email: string; displayName: string }>)[role];
  const password = v(`OPSDESK_${ROLE_ENV[role]}_PASSWORD`, v('OPSDESK_PASSWORD'));
  if (!u?.email || !password) return undefined;
  return { role, email: u.email, password, displayName: u.displayName || u.email.split('@')[0] };
}

export const users: Record<Role, Credential | undefined> = {
  customer: credential('customer'),
  employee: credential('employee'),
  manager: credential('manager'),
  teamlead: credential('teamlead'),
  superadmin: credential('superadmin'),
};

export const storageStatePath = (role: Role) => path.join(ROOT, '.auth', `${role}.json`);
