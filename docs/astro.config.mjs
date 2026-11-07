import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import starlightLinksValidator from 'starlight-links-validator';
import starlightSidebarTopics from 'starlight-sidebar-topics';
import rehypeConsoleSlug from './src/console-slug.mjs';

const group = (en, ja, dir, collapsed = false) => ({
  label: en, translations: { ja }, collapsed, items: [{ autogenerate: { directory: dir } }],
});
const t = (en, ja) => ({ en, ja });

// The pilot pages (docs/pilot/) are drafts; scripts/build.sh leaves them out when DOCS_PILOT=0, which the
// production deploy does. Every sidebar entry that points into them has to go with them, or the top bar links
// to pages that were never built (the link validator does not check the sidebar config).
const pilot = process.env.DOCS_PILOT !== '0';

const userTopic = pilot
  ? {
      // The pilot pages are Japanese only, so the topic lands on a page that exists in both languages.
      id: 'user', label: t('User guide', 'ユーザーガイド'), icon: 'open-book', link: '/member/',
      items: [
        group('Getting started', 'はじめに', 'user/start'),
        group('Integrations', '連携', 'user/integrations'),
        group('Security', 'セキュリティ', 'user/security'),
        group('All chapters (current layout)', '全章（現行の構成）', 'member', true),
      ],
    }
  : {
      id: 'user', label: t('User guide', 'ユーザーガイド'), icon: 'open-book', link: '/member/',
      items: [{ autogenerate: { directory: 'member' } }],
    };

const referenceItems = pilot
  ? [
      group('Commands', 'コマンド', 'ref/cli'),
      group('MCP tools', 'MCP ツール', 'ref/mcp'),
      group('Everything else (current layout)', 'その他（現行の構成）', 'ref', true),
    ]
  : [{ autogenerate: { directory: 'ref' } }];

// One topic per reader, like the shelves of guide/; each topic has its own sidebar.
const topics = [
  userTopic,
  {
    label: t('Team admin', 'チーム管理'), icon: 'setting', link: '/admin/',
    items: [{ autogenerate: { directory: 'admin' } }],
  },
  {
    label: t('Self-hosting', 'セルフホスト'), icon: 'rocket', link: '/operate/',
    items: [
      { label: 'Guide', translations: { ja: 'ガイド' }, items: [{ autogenerate: { directory: 'operate' } }] },
    ],
  },
  {
    label: t('Reference', 'リファレンス'), icon: 'information', link: '/ref/',
    items: referenceItems,
  },
  {
    label: t('Release notes', 'リリースノート'), icon: 'list-format', link: '/ref/releases/summary/',
    items: [{ autogenerate: { directory: 'ref/releases' } }],
  },
];

export default defineConfig({
  site: 'https://agent-fleet.org',
  base: '/docs',
  trailingSlash: 'always',
  markdown: { rehypePlugins: [rehypeConsoleSlug] },
  integrations: [
    starlight({
      title: 'Agent Fleet',
      customCss: ['./src/styles/custom.css'],
      logo: { src: './src/assets/icon.png' },
      favicon: '/favicon.png',
      defaultLocale: 'root',
      locales: {
        root: { label: 'English', lang: 'en' },
        ja: { label: '日本語', lang: 'ja' },
      },
      social: [{ icon: 'github', label: 'GitHub', href: 'https://github.com/k-k1/agent-fleet' }],
      lastUpdated: false,
      plugins: [
        starlightSidebarTopics(topics),
        starlightLinksValidator({ errorOnRelativeLinks: false }),
      ],
    }),
  ],
});
