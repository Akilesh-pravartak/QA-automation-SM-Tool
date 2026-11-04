import { Page } from 'playwright';

export const dashboardModal = (page: Page) => ({
  heading: page.getByRole('heading', { name: /^dashboard$/i }),
  widget: (name: RegExp) => page.getByText(name).first(),
  periodButton: (days: number) => {
    const name = new RegExp(`^\\s*(last )?${days}( days|d)?\\s*$`, 'i');
    return page.getByRole('button', { name }).or(page.getByRole('tab', { name })).or(page.getByRole('radio', { name })).first();
  },
  periodControl: page.getByLabel(/period/i).first(),
  accountFilter: page.getByRole('combobox', { name: /^account$/i }).first(),
  openNowValue: page.getByRole('link', { name: /open now$/i }).first(),
  errorBanner: page.getByText(/something went wrong|failed to load|could not load/i).first(),
});
