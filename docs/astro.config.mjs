import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import starlightLinksValidator from 'starlight-links-validator';
import starlightSidebarTopics from 'starlight-sidebar-topics';
import rehypeConsoleSlug from './src/console-slug.mjs';

const group = (en, ja, dir, collapsed = false) => ({
  label: en, translations: { ja }, collapsed, items: [{ autogenerate: { directory: dir } }],
});
const t = (en, ja) => ({ en, ja });

// One topic per reader, like the shelves of guide/; each topic has its own sidebar.
const topics = [
  {
    id: 'user', label: t('User guide', 'ユーザーガイド'), icon: 'open-book', link: '/user/start/overview/',
    items: [
      group('Getting started', 'はじめに', 'user/start'),
      group('Integrations', '連携', 'user/integrations'),
      group('Security', 'セキュリティ', 'user/security'),
      group('All chapters (current layout)', '全章（現行の構成）', 'member', true),
    ],
  },
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
    items: [
      group('Commands', 'コマンド', 'ref/cli'),
      { label: 'MCP tools', translations: { ja: 'MCP ツール' }, link: '/ref/mcp/' },
      group('Everything else (current layout)', 'その他（現行の構成）', 'ref', true),
    ],
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
