import { existsSync } from 'node:fs';
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import starlightLinksValidator from 'starlight-links-validator';
import starlightSidebarTopics from 'starlight-sidebar-topics';
import rehypeConsoleSlug from './src/console-slug.mjs';

const group = (en, ja, dir, collapsed = false) => ({
  label: en, translations: { ja }, collapsed, items: [{ autogenerate: { directory: dir } }],
});
const t = (en, ja) => ({ en, ja });

// The sidebar is built from the directories this build actually has. Pages reach src/content/docs/ from two places:
// the agent-fleet release (guide/, which gains task pages under user/ as the rewrite lands) and the pilot drafts
// (docs/pilot/, left out when DOCS_PILOT=0). A group for a directory that is not there, or a page that is in no
// group, fails the build or leaves a dead link in the top bar (the link validator does not check this config).
const CONTENT = new URL('./src/content/docs/', import.meta.url);
// Either language counts: the task pages are written in Japanese first.
const has = (dir) => existsSync(new URL(dir, CONTENT)) || existsSync(new URL(`ja/${dir}`, CONTENT));
const groups = (...defs) => defs.filter(([, , dir]) => has(dir)).map((d) => group(...d));

const userTopic = {
  // The task pages are written in Japanese first, so the topic lands on a page that exists in both languages.
  id: 'user', label: t('User guide', 'ユーザーガイド'), icon: 'open-book', link: '/member/',
  items: [
    // Every group of the page map (research/page-titles.tsv), in its order. A directory that is not there yet is
    // skipped, so a lane that adds the first page of a group needs no change here.
    ...groups(
      ['Getting started', 'はじめに', 'user/start'],
      ['Sessions', 'セッション', 'user/sessions'],
      ['Many sessions', 'たくさんのセッション', 'user/fleet'],
      ['Agents', 'エージェント', 'user/agents'],
      ['Code', 'コード', 'user/code'],
      ['Files and terminal', 'ファイルとターミナル', 'user/files'],
      ['Preview and browser', 'プレビューとブラウザ', 'user/preview'],
      ['Chat and memos', 'チャットとメモ', 'user/chat'],
      ['Working as a team', 'チームで使う', 'user/team'],
      ['Integrations', '連携', 'user/integrations'],
      ['Workspace', 'ワークスペース', 'user/workspace'],
      ['Images', '画像', 'user/images'],
      ['Memory', '記憶', 'user/memory'],
      ['Settings', '設定', 'user/settings'],
      ['Using it from outside', '外部から使う', 'user/outside'],
      ['Security', 'セキュリティ', 'user/security'],
      ['Troubleshooting', '困ったとき', 'user/troubleshooting'],
    ),
    group('All chapters (current layout)', '全章（現行の構成）', 'member', has('user')),
  ],
};

const referenceItems = [
  ...groups(['Commands', 'コマンド', 'ref/cli'], ['MCP tools', 'MCP ツール', 'ref/mcp']),
  ...(has('ref/cli') || has('ref/mcp')
    ? [group('Everything else (current layout)', 'その他（現行の構成）', 'ref', true)]
    : [{ autogenerate: { directory: 'ref' } }]),
];

// One topic per reader, like the shelves of guide/; each topic has its own sidebar.
const topics = [
  userTopic,
  {
    label: t('Team admin', 'チーム管理'), icon: 'setting', link: '/admin/',
    items: [{ autogenerate: { directory: 'admin' } }],
  },
  {
    id: 'operate', label: t('Self-hosting', 'セルフホスト'), icon: 'rocket', link: '/operate/',
    items: [
      { label: 'Guide', translations: { ja: 'ガイド' }, items: [{ autogenerate: { directory: 'operate' } }] },
      // The runbooks are hidden from autogenerate (scripts/to_starlight.py) and listed here, so the group gets a
      // real label. The list is deploy/release/stage-docs.sh's RUNBOOKS; a slug that is not built fails the build,
      // but a runbook added there is not listed until it is added here too.
      {
        label: 'Runbooks', translations: { ja: 'Runbook' },
        items: ['compose', 'native', 'wsl', 'aws-ec2-single', 'aws-ecs', 'kubernetes']
          .map((name) => ({ slug: `operate/runbooks/${name}` })),
      },
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
