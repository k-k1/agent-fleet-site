// Heading ids with the Console's rule (console/src/lib/filemeta.ts slug()), not GitHub's:
// the guide's #fragments are written against the Console, so `a — b` must be `a-b`.
// Astro's own heading-id pass keeps an id that is already set, so the TOC follows this.
const text = (n) => n.type === 'text' ? n.value : (n.children || []).map(text).join('');
const consoleSlug = (t) => t.toLowerCase().trim().replace(/[^\p{L}\p{N} -]/gu, '').replace(/\s+/g, '-');
// Runbooks are deploy/*/README.md, read on GitHub, so their anchors follow github-slugger.
const githubSlug = (t) => t.toLowerCase().trim().replace(/[^\p{L}\p{M}\p{N}\p{Pc} -]/gu, '').replace(/ /g, '-');

export default function rehypeConsoleSlug() {
  return (tree, file) => {
    const slug = /operate\/runbooks\//.test(file?.path || '') ? githubSlug : consoleSlug;
    const seen = new Map();
    const walk = (n) => {
      if (n.type === 'element' && /^h[1-6]$/.test(n.tagName) && !n.properties?.id) {
        let id = slug(text(n));
        const k = seen.get(id) || 0;
        seen.set(id, k + 1);
        if (k) id = `${id}-${k}`;
        n.properties = { ...n.properties, id };
      }
      (n.children || []).forEach(walk);
    };
    walk(tree);
  };
}
