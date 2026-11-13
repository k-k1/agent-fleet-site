// The product site's header links (site/index.html and site/ja/index.html, same wording), for the docs header.
// Paths outside /docs/ are the product site on the same origin.
const RELEASES = 'https://github.com/k-k1/agent-fleet-dist/releases';
const GITHUB = 'https://github.com/k-k1/agent-fleet';

export interface ProductLink {
  text: string;
  href: string;
  current?: boolean; // the docs site itself
  github?: boolean; // Starlight's GitHub icon covers it where that icon is shown
}

export function productLinks(locale: string | undefined) {
  const ja = locale === 'ja';
  const links: ProductLink[] = ja
    ? [
        { text: '機能', href: '/ja/features/' },
        { text: 'ドキュメント', href: '/docs/ja/', current: true },
        { text: 'リリース', href: RELEASES },
        { text: 'GitHub', href: GITHUB, github: true },
      ]
    : [
        { text: 'Features', href: '/features/' },
        { text: 'Docs', href: '/docs/', current: true },
        { text: 'Releases', href: RELEASES },
        { text: 'GitHub', href: GITHUB, github: true },
      ];
  return {
    links,
    top: ja ? '/ja/' : '/',
    label: ja ? 'Agent Fleet のサイト' : 'Agent Fleet site',
    menu: ja ? 'サイトのメニュー' : 'Site menu',
  };
}
