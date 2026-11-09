#!/usr/bin/env node
// Search-quality check for the built docs site.
//
//   node scripts/search_quality.mjs [dist dir] [--ranking '{"termSimilarity":9}'] [--queries file.tsv] [--json | --compact]
//
// Runs every query of research/search-queries.tsv against dist/pagefind with Pagefind's own browser library
// (the code the site's search box runs), using the ranking Starlight embedded in the built search bundle, and
// prints the rank of the expected page. Exits 1 when a page is outside its top N, or is not in the build at all
// (a check that cannot find its page must not pass). --ranking overrides the embedded weights, to compare tunings
// without rebuilding. Needs a build that contains the pages named in the list (a ref with user/integrations/aws-sso).
import { readFileSync, readdirSync, existsSync } from 'node:fs';
import { pathToFileURL, fileURLToPath } from 'node:url';
import path from 'node:path';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const argv = process.argv.slice(2);
const opt = (name) => { const i = argv.indexOf(name); return i < 0 ? null : argv.splice(i, 2)[1]; };
const compact = argv.includes('--compact') && argv.splice(argv.indexOf('--compact'), 1);
const asJson = argv.includes('--json') && argv.splice(argv.indexOf('--json'), 1);
const rankingArg = opt('--ranking');
const queriesFile = opt('--queries') ?? path.join(HERE, '../research/search-queries.tsv');
const dist = path.resolve(argv[0] ?? path.join(HERE, '../dist'));

// The weights the site ships: Starlight writes them into the search bundle.
function embeddedRanking() {
  for (const f of readdirSync(path.join(dist, '_astro'))) {
    if (!/^Search.*\.js$/.test(f)) continue;
    const m = readFileSync(path.join(dist, '_astro', f), 'utf8').match(/ranking:(\{[^}]*\})/);
    if (m) return Function(`return (${m[1]})`)();
  }
  throw new Error('no ranking found in the built search bundle');
}
const ranking = rankingArg ? JSON.parse(rankingArg) : embeddedRanking();

const rows = readFileSync(queriesFile, 'utf8').split('\n')
  .filter((l) => l.trim() && !l.startsWith('#'))
  .map((l) => { const [query, lang, page, n] = l.split('\t'); return { query, lang, page, n: Number(n) }; });

// Pagefind fetches its index with fetch(); answer from dist/ so no server (and no network) is involved.
const base = 'http://dist.invalid';
globalThis.fetch = async (url) => {
  const file = path.join(dist, decodeURIComponent(new URL(url).pathname));
  return existsSync(file) ? new Response(readFileSync(file)) : new Response(null, { status: 404 });
};

const results = [];
for (const lang of ['ja', 'en']) {
  // One Pagefind instance per language: the language selects the index, as <html lang> does in the browser.
  // Pagefind reads the language from <html lang>; give it a stand-in document.
  globalThis.document = { currentScript: null, querySelector: () => ({ getAttribute: () => lang }) };
  const pf = await import(`${pathToFileURL(path.join(dist, 'pagefind/pagefind.js'))}?lang=${lang}`);
  await pf.options({ basePath: `${base}/pagefind/`, ranking });
  for (const row of rows.filter((r) => r.lang === lang)) {
    const found = await pf.search(row.query);
    const urls = (await Promise.all(found.results.slice(0, 40).map((r) => r.data()))).map((d) => new URL(d.url, base).pathname.replace(/^\/docs\//, '/').slice(1));
    const idx = urls.findIndex((u) => u.startsWith(row.page));
    const exists = existsSync(path.join(dist, row.page, 'index.html'));
    results.push({ ...row, rank: idx < 0 ? null : idx + 1, total: found.results.length, exists,
      top: urls.slice(0, 3) });
  }
  await pf.destroy?.();
}

if (compact) console.log(results.map((r) => r.rank ?? '-').join(' '));
else if (asJson) console.log(JSON.stringify({ ranking, results }, null, 2));
else {
  console.log('ranking', JSON.stringify(ranking));
  for (const r of results) {
    const ok = r.rank !== null && r.rank <= r.n;
    const why = !r.exists ? ' (page not in this build)' : '';
    console.log(`${ok ? 'ok  ' : 'FAIL'} [${r.lang}] ${r.query.padEnd(24)} rank ${String(r.rank ?? '>40').padStart(3)}/${r.total} want<=${r.n} ${r.page}${why}`);
  }
}
process.exit(results.every((r) => r.rank !== null && r.rank <= r.n) ? 0 : 1);
