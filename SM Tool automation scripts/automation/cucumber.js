// Type checking is done by `npm run typecheck`; skip it at run time for fast start-up.
process.env.TS_NODE_TRANSPILE_ONLY = 'true';

// Cucumber configuration. Every scenario carries a @TC-<MODULE>-<NNN> tag that
// reporting/generate_reports.py maps back to the test design workbook and RTM.
module.exports = {
  default: {
    paths: ['features/**/*.feature'],
    requireModule: ['ts-node/register'],
    require: ['support/**/*.ts', 'step/**/*.ts'],
    // A dry run must not overwrite the last real results.
    format: process.argv.includes('--dry-run')
      ? ['summary']
      : ['progress', 'summary', 'json:reports/cucumber.json', 'html:reports/cucumber.html'],
    formatOptions: { snippetInterface: 'async-await' },
    tags: 'not @manual',
    retry: Number(process.env.OPSDESK_RETRIES || 0),
    parallel: 0, // shared accounts on a shared environment
  },
};
