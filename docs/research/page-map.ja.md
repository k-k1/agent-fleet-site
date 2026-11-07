# guide/ から新しいページ構成への対応表

k-k1/agent-fleet#3463 の「今の `guide/` の各節を新しい構成のページに割り当て、ユーザーと合意する」段階の成果物です。
ページの型と書き方は ADR 0131 §3–§5 に従います。ページの書き直しはこの表に従います。表を変えるときは `page-map.tsv` を直して `--write` で作り直します。

- 元にしたのは agent-fleet の `main`（`afc94df70`、2026-11-07）の英語版 `guide/`（55 ファイル、見出し 616 個）です。
  書き直すのは `main` の `guide/` なので、タグではなく `main` に合わせています（`v0.41.0` には `operate/04-secure` と
  `operate/12-keys` の節が 1 つずつまだありません）。日本語版は同じ構成なので同じ表に従います。
- 割り当ての規則は [`page-map.tsv`](page-map.tsv)、タイトルとサイドバーのグループは [`page-titles.tsv`](page-titles.tsv) にあります。
  `scripts/page_map.py <agent-fleet のチェックアウト>` が、**すべての見出しがどこかのページに入っていること**と、
  **どの見出しにも当たらない規則がないこと**（見出しの名前が変わったときに黙って既定のページに落ちるのを防ぐ）を確かめます。
  `--write` を付けると、この文書の目次と対応表を作り直します。
- この表は、のちの `guide/_redirects.tsv`（古いパスから新しいパスへのリダイレクト）の元になります。

## 決めかた

1. **1 ページに 1 つの「やりたいこと」。** タイトルは動詞で終わる形にしました（「AWS SSO を使う」）。
2. **設定画面の章（`member/20-settings`）はタブごとにばらして、そのタブを使うタスクのページに入れました。**
   「どのタブで何ができるか」という引き方は `ref/settings` に残します。
3. **網羅的な説明はリファレンスに移しました。** たとえば AWS の章にある「ターミナル・SDK・ビルドツールからプロファイルを使う」
   （3,632 語）は `ref/cli/af-aws-exec` に入れ、タスクのページには使い方の流れだけを書きます。
4. **困ったときのページは分野ごとに残しました。** 各タスクページの「うまくいかないとき」には、そのページに固有の症状だけを書き、
   分野をまたぐ症状は `user/troubleshooting/` に置きます。
5. **`member/` は `user/` に名前を変えます**（パイロットと同じ）。`admin/`・`operate/`・`ref/` はそのままです。
6. **設計の理由は公開しません**（ADR 0131 §4）。理由だけの節（「Claude Code 自身の仕組みとの違い」など）も表では
   どこかのページに割り当てていますが、書き直すときに落とします。

## 決まったこと（2026-11-07、ユーザーと合意）

1. **ページ数は 190 ページのまま進めます。** ADR の見積もり（約 110 ページ）より多くなりますが、「1 ページに 1 機能」を優先します。
   元の分量が 200 語に満たないページ（Codex・GitHub Copilot・Cursor を接続する、など 12 ページ）もまとめません。
   「画面の見かた」は元が 51 語しかないので書き足します。
2. **大きすぎるページは分けます。** `operate/07-engines` の推論エンジンの節は、動かす（`operate/engines/gpu`）・
   モデルを取り込む（`operate/engines/models`）・状態と履歴を見る（`operate/engines/status`）の 3 ページにしました。
   `ref/agents`（6,574 語）はリファレンスなので 1 ページのままにします。
3. **「ターミナルを使わずに使う」（今の `member/lite`）は中身を各ページに散らします。** 番号付きの節はそれぞれのタスクページへ移し、
   `user/start/without-terminal` は「まず読むページ」を案内する入口と「人あての質問に代わりに答えない」という約束だけを残します。

## 新しいページ構成

「元の節」は、そのページに入る今の章（`ファイル › 見出し`、H2 まで）です。語数は英語版の元の分量で、書き直したあとの長さではありません。
「（新規）」は元の節がないページです。

<!-- generated:tree -->
### ユーザーガイド（user/）

**はじめに**

| ページ | タイトル | 元の節 | 語数 |
|---|---|---|--:|
| `user/start/overview` | Agent Fleet でできること | `README`<br>`member/README`<br>`member/lite › 1. What you can do with Agent Fleet` | 800 |
| `user/start/quickstart` | 最初のセッションを始める | `member/01-first-day`<br>`member/lite › 3. One-time setup` | 1133 |
| `user/start/concepts` | 用語と全体像 | （新規） |  |
| `user/start/console-tour` | 画面の見かた | `member/02-console-basics`<br>`member/lite › 2. Logging in and reading the screen` | 258 |
| `user/start/shortcuts` | キーボードとコマンドパレットで操作する | `member/02-console-basics › Shortcuts`<br>`member/02-console-basics › Command palette`<br>`member/20-settings › Keyboard` | 1555 |
| `user/start/panes` | 画面を分けて並べる | `member/02-console-basics › Arranging multiple views (panes)` | 433 |
| `user/start/phone` | スマートフォンで使う | `member/02-console-basics › Using it on a phone` | 365 |
| `user/start/end-of-day` | 一日の終わりにワークスペースを止める | `member/01-first-day › At the end of the day — is it OK to stop the workspace?` | 402 |
| `user/start/without-terminal` | ターミナルを使わない人のための入口 | `member/lite` | 226 |

**セッション**

| ページ | タイトル | 元の節 | 語数 |
|---|---|---|--:|
| `user/sessions/start` | セッションを始める | `member/03-starting-sessions` | 1062 |
| `user/sessions/worktrees` | ワークツリーで並行して作業する | `member/03-starting-sessions › Worktrees and new branches — the key to parallel work`<br>`member/03-starting-sessions › Working folder — starting inside a subfolder` | 452 |
| `user/sessions/from-issues` | Issue やチケットから始める | `member/03-starting-sessions › Starting from the issue tracker` | 1856 |
| `user/sessions/status` | セッションの状態を読む | `member/03-starting-sessions › Reading state — badges and notifications`<br>`member/lite › 7. Watching development progress` | 654 |
| `user/sessions/reply` | セッションに返事をする | `member/04-conversation` | 1193 |
| `user/sessions/queue` | 送る内容を待たせる・ターンを止める | `member/04-conversation › Stopping a turn when something is queued`<br>`member/04-conversation › Holding follow-ups before sending (send queue)` | 1021 |
| `user/sessions/plans` | プランにコメントする・レビューさせる | `member/04-conversation › Writing comments on a plan`<br>`member/04-conversation › Having another session review the plan` | 797 |
| `user/sessions/skills` | スキルやコマンドを呼び出す | `member/04-conversation › Calling a skill or a command` | 168 |
| `user/sessions/branch-message` | 過去のメッセージから分岐する | `member/04-conversation › Branch from a past message` | 261 |
| `user/sessions/changes` | セッションが変えた内容を見る | `member/04-conversation › Seeing what a session changed` | 174 |
| `user/sessions/export` | 会話を Markdown で保存する | `member/04-conversation › Saving a conversation as Markdown` | 219 |
| `user/sessions/translate` | 回答を自分の言語で読む | `member/04-conversation › Reading an answer in your own language (translation)` | 261 |
| `user/sessions/stop-resume` | セッションを止める・再開する | `member/05-stopping-and-tidying` | 1378 |
| `user/sessions/auto-stop` | 終わったら止める・起こしたままにする | `member/05-stopping-and-tidying › Keeping a session awake`<br>`member/05-stopping-and-tidying › Having a session stop when it is done` | 309 |
| `user/sessions/cleanup` | 終わったセッションを片付ける | `member/05-stopping-and-tidying › Tidying up in bulk (cleanup)`<br>`member/05-stopping-and-tidying › Clearing one finished job (deleting a working copy)`<br>`member/05-stopping-and-tidying › Locking something against deletion` | 1139 |
| `user/sessions/budget` | 使いすぎたセッションを止める（支出の上限） | `member/05-stopping-and-tidying › A spend budget — pausing a session that spends too much` | 361 |
| `user/sessions/handoff` | 別のセッションやエージェントに引き継ぐ | `member/05-stopping-and-tidying › Continuing elsewhere — handoff, branch, move` | 1230 |

**たくさんのセッション**

| ページ | タイトル | 元の節 | 語数 |
|---|---|---|--:|
| `user/fleet/overview` | 動いているセッションを一覧する | `member/11-many-sessions › Seeing every running session at once (the sessions overview)` | 835 |
| `user/fleet/graph` | セッションのつながりを時系列で見る | `member/11-many-sessions › Seeing how sessions relate over time (the fleet graph)` | 608 |
| `user/fleet/working-sets` | ワーキングセットで絞り込む | `member/11-many-sessions › Narrowing the view with working sets` | 245 |
| `user/fleet/child-sessions` | セッションから子セッションを起動する | `member/11-many-sessions › Starting sessions from a session (child sessions)` | 1105 |
| `user/fleet/messages` | セッション同士でやりとりさせる | `member/11-many-sessions › Messages between sessions` | 1060 |
| `user/fleet/pr-feedback` | PR のレビューをセッションに伝える | `member/11-many-sessions › Telling a session about its pull request's feedback` | 358 |
| `user/fleet/fleet-visibility` | セッションに全体を見せる | `member/11-many-sessions › Letting a session see the fleet` | 324 |
| `user/fleet/operator` | Fleet Operator に任せる | `member/11-many-sessions` | 1994 |
| `user/fleet/operator-patterns` | Fleet Operator の使いかたの例 | `member/11-many-sessions › Use-case patterns` | 764 |
| `user/fleet/schedules` | 決まった時刻に実行する | `member/11-many-sessions › Scheduled runs` | 561 |

**コード**

| ページ | タイトル | 元の節 | 語数 |
|---|---|---|--:|
| `user/code/connect-git` | Git のサービスを接続する | `member/06-code › Connect a git provider`<br>`member/06-code › Push and authentication`<br>`member/20-settings › Git hosting` | 415 |
| `user/code/clone` | リポジトリをクローンする | `member/06-code` | 495 |
| `user/code/internal-git` | 内蔵の Git を使う | `member/06-code › The built-in git provider (internal Git)`<br>`member/20-settings › Internal repos` | 201 |
| `user/code/launch-from-repo` | リポジトリからセッションを起動する | `member/06-code › Launch a session from a repository row` | 1042 |
| `user/code/git-flow` | Git Flow を初期化する | `member/06-code › Initialize Git Flow` | 353 |
| `user/code/commit` | コミットグラフでコミットする | `member/06-code › Commit in the commit graph view` | 312 |
| `user/code/svn` | Subversion のリポジトリを使う | `member/06-code › Subversion (SVN) repositories` | 504 |

**ファイルとターミナル**

| ページ | タイトル | 元の節 | 語数 |
|---|---|---|--:|
| `user/files/browse` | ファイルを見る・ダウンロードする | `member/07-files` | 913 |
| `user/files/view` | ドキュメントや図を表示する | `member/07-files › File viewer`<br>`member/lite › 5. Reading documents and slides` | 1365 |
| `user/files/edit` | ファイルを編集する | `member/07-files › Editing a file` | 299 |
| `user/files/send` | ファイルをセッションに渡す | `member/07-files › Send a file to a session / chat` | 136 |
| `user/files/terminal` | ターミナルを使う | `member/08-terminal` | 671 |

**エージェント**

| ページ | タイトル | 元の節 | 語数 |
|---|---|---|--:|
| `user/agents/choose` | エージェントを選ぶ | `member/09-agents`<br>`member/20-settings › Agents` | 566 |
| `user/agents/claude` | Claude を接続する | `member/09-agents › Claude` | 1062 |
| `user/agents/codex` | Codex を接続する | `member/09-agents › Codex` | 133 |
| `user/agents/opencode` | OpenCode を接続する | `member/09-agents › OpenCode` | 1094 |
| `user/agents/copilot` | GitHub Copilot を接続する | `member/09-agents › GitHub Copilot` | 100 |
| `user/agents/cursor` | Cursor を接続する | `member/09-agents › Cursor` | 157 |
| `user/agents/kiro` | Kiro を接続する | `member/09-agents › Kiro` | 229 |
| `user/agents/agy` | Antigravity を接続する | `member/09-agents › Antigravity (agy)` | 458 |
| `user/agents/muse` | Muse Code を接続する | `member/09-agents › Muse Code` | 406 |
| `user/agents/lcpp` | lcpp を使う | `member/09-agents › lcpp` | 303 |
| `user/agents/usage` | 料金と使用量を確かめる | `member/09-agents › Model prices and usage chips`<br>`member/09-agents › Checking remaining context`<br>`member/09-agents › RTK (token savings)`<br>`member/20-settings › Agent usage` | 847 |
| `user/agents/instructions` | 作業のしかたを一度だけ書いておく | `member/09-agents › Agent instructions (write down how you work, once)`<br>`member/20-settings › Agent instructions` | 431 |
| `user/agents/bring-claude-setup` | 手元の Claude Code の設定を持ち込む | `member/09-agents › Bringing your personal Claude Code setup`<br>`member/20-settings › Skills` | 871 |

**チャットとメモ**

| ページ | タイトル | 元の節 | 語数 |
|---|---|---|--:|
| `user/chat/assistant` | アシスタントに質問する | `member/09-agents › Default model for the assistant chat`<br>`member/10-chat-memo`<br>`member/20-settings › Assistant`<br>`member/lite › 4. Using chat (questions, translation, text cleanup)` | 1796 |
| `user/chat/purpose-assistants` | 翻訳や専用のアシスタントを使う | `member/10-chat-memo › Purpose-built assistants and translation`<br>`member/20-settings › AI assistance` | 1025 |
| `user/chat/memos` | メモをためて渡す | `member/10-chat-memo › Memo queue`<br>`member/lite › 6. The memo queue (collect ideas and hand them over)` | 714 |

**チームで使う**

| ページ | タイトル | 元の節 | 語数 |
|---|---|---|--:|
| `user/team/hand-over` | セッションをメンバーに渡す | `member/12-collaboration` | 682 |
| `user/team/inbox` | チームメイトに頼む（受信箱） | `member/12-collaboration › Asking a teammate: the inbox` | 770 |
| `user/team/share` | 会話を共有する | `member/12-collaboration › Sharing a conversation (shared sessions)`<br>`member/lite › Reading work that was shared with you` | 622 |
| `user/team/usage-limits` | 使用量の上限の状況を見せ合う | `member/12-collaboration › Showing teammates where you stand on usage limits`<br>`member/20-settings › Limit board` | 433 |

**画像**

| ページ | タイトル | 元の節 | 語数 |
|---|---|---|--:|
| `user/images/gallery` | 画像ギャラリーを使う | `member/13-images` | 1143 |
| `user/images/generate` | 画像を生成する | `member/13-images › Image generation` | 1451 |
| `user/images/studio` | スタジオで画像を仕上げる | `member/13-images › Studio — refine the draft by talking to an agent` | 1220 |
| `user/images/from-session` | セッションに画像を作らせる | `member/13-images › Having a session generate an image` | 849 |

**プレビューとブラウザ**

| ページ | タイトル | 元の節 | 語数 |
|---|---|---|--:|
| `user/preview/browser-pane` | 起動した Web アプリを見る | `member/14-preview-browser` | 1543 |
| `user/preview/subdomains` | プレビュー用のサブドメインを使う | `member/14-preview-browser › Preview subdomains (only where they are issued)`<br>`member/20-settings › Preview subdomains` | 1268 |
| `user/preview/dev-signin` | プレビューで Google ログインを試す | `member/14-preview-browser › Signing in with Google on a preview URL (development OIDC IdP)` | 1269 |
| `user/preview/agent-browser` | エージェントが開いたブラウザを操作する | `member/14-preview-browser › Operating a browser the agent opened` | 291 |

**連携**

| ページ | タイトル | 元の節 | 語数 |
|---|---|---|--:|
| `user/integrations/gh-bkt` | GitHub・Bitbucket の CLI を使う | `member/15-external-services` | 317 |
| `user/integrations/issue-tracker` | 課題管理サービスを接続する | `member/20-settings › Issue tracker` | 414 |
| `user/integrations/jira` | Jira を使う | `member/15-external-services › Use `jira` in a session` | 1308 |
| `user/integrations/confluence` | Confluence を使う | `member/15-external-services › Use `confluence` in a session` | 557 |
| `user/integrations/chat-bridge` | Discord・Slack とつなぐ | `member/15-external-services › Connecting Discord / Slack (chat bridge)`<br>`member/20-settings › Chat` | 386 |
| `user/integrations/ops-monitoring` | 監視ツールとつなぐ | `member/15-external-services › PagerDuty / Grafana / CloudWatch / AWS connect from the "Ops & monitoring" tab (recommended)`<br>`member/20-settings › Ops & monitoring` | 860 |
| `user/integrations/aws-sso` | AWS SSO を使う | `member/16-cloud-accounts`<br>`member/20-settings › AWS profiles/SSM` | 2512 |
| `user/integrations/aws-ssm` | 社内の別のホストにログインする（SSM） | `member/16-cloud-accounts › Logging in to another in-house host (SSM)` | 1231 |
| `user/integrations/gcloud` | Google Cloud を使う | `member/16-cloud-accounts › Running commands in Google Cloud as you (af-gcloud-exec)`<br>`member/20-settings › Google Cloud` | 2634 |
| `user/integrations/mcp-servers` | セッションに MCP サーバーを追加する | `member/20-settings › MCP servers (used by sessions)` | 1336 |

**ワークスペース**

| ページ | タイトル | 元の節 | 語数 |
|---|---|---|--:|
| `user/workspace/recreate` | ワークスペースを作り直す | `member/17-workspace-environment`<br>`member/20-settings › Danger zone` | 670 |
| `user/workspace/machine` | マシンの大きさを変える | `member/20-settings › Machine` | 1263 |
| `user/workspace/toolchains` | ツールチェーンを選ぶ | `member/20-settings › Toolchains` | 282 |
| `user/workspace/databases` | データベースを使うテストを動かす | `member/17-workspace-environment › Running database-backed tests`<br>`member/20-settings › Databases` | 1158 |
| `user/workspace/aws-emulator` | AWS のコードを手元のエミュレーターで試す | `member/17-workspace-environment › Trying AWS code against a local emulator (MiniStack)` | 576 |
| `user/workspace/export-import` | ワークスペースを書き出す・取り込む | `member/20-settings › Export / import` | 313 |
| `user/workspace/cost` | 稼働時間とクラウド費用を見る | `member/20-settings › Cloud cost`<br>`member/20-settings › Running time` | 367 |

**記憶**

| ページ | タイトル | 元の節 | 語数 |
|---|---|---|--:|
| `user/memory/overview` | エージェントの記憶を見る・直す | `member/18-agent-memory` | 1471 |
| `user/memory/changes` | 記憶の変更を確かめる | `member/18-agent-memory › Changes` | 465 |
| `user/memory/import-export` | 記憶を取り込む・書き出す | `member/18-agent-memory › Import & export` | 1720 |
| `user/memory/settings` | 記憶のしかたを設定する | `member/18-agent-memory › Settings`<br>`member/20-settings › Agent memory` | 1231 |
| `user/memory/snapshots` | スナップショットで記憶を戻す | `member/18-agent-memory › Memory snapshots`<br>`member/20-settings › Memory snapshots` | 500 |
| `user/memory/external` | 外部のエージェントから記憶を使う | `member/18-agent-memory › Using Agent Fleet memory from an external agent`<br>`member/19-outside-access › A memory-only connector (for claude.ai)`<br>`member/19-outside-access › Using Agent Fleet memory from an external agent` | 1552 |

**外部から使う**

| ページ | タイトル | 元の節 | 語数 |
|---|---|---|--:|
| `user/outside/external-claude` | 外部の Claude からワークスペースを動かす | `member/19-outside-access`<br>`member/20-settings › MCP tokens & apps` | 1068 |
| `user/outside/oauth-client` | リモートの MCP クライアントをサインインでつなぐ | `member/19-outside-access › Connecting a remote MCP client by signing in (OAuth)` | 683 |
| `user/outside/move-work-in` | 手元の Claude Code の作業をワークスペースに移す | `member/19-outside-access › Moving work from your own Claude Code into the workspace` | 775 |

**設定**

| ページ | タイトル | 元の節 | 語数 |
|---|---|---|--:|
| `user/settings/display` | 表示とアカウントを変える | `member/20-settings › Display`<br>`member/20-settings › Account` | 669 |
| `user/settings/notifications` | 通知を受け取る | `member/20-settings › Notifications` | 583 |
| `user/settings/read-aloud` | 読み上げを使う | `member/20-settings › Read aloud` | 160 |

**セキュリティ**

| ページ | タイトル | 元の節 | 語数 |
|---|---|---|--:|
| `user/security/credentials` | 資格情報の扱い | （新規） |  |

**困ったとき**

| ページ | タイトル | 元の節 | 語数 |
|---|---|---|--:|
| `user/troubleshooting/workspace` | ワークスペースが起動しない・止まった | `member/21-troubleshooting › Workspace: start, stop and disk` | 613 |
| `user/troubleshooting/sessions` | セッションが再開できない・見当たらない | `member/04-conversation › When a turn is interrupted`<br>`member/05-stopping-and-tidying › A claude session whose conversation log was deleted`<br>`member/21-troubleshooting › Sessions: resuming, sharing, tidying` | 1782 |
| `user/troubleshooting/agents` | エージェントにログインできない・モデルが出ない | `member/21-troubleshooting › Agents: sign-in and models`<br>`member/21-troubleshooting › Assistants` | 1216 |
| `user/troubleshooting/git` | クローンや認証に失敗する | `member/21-troubleshooting › Repositories and git` | 193 |
| `user/troubleshooting/preview` | プレビューやブラウザが表示されない | `member/21-troubleshooting › Preview and browser` | 1098 |
| `user/troubleshooting/integrations` | MCP・クラウド・Jira が動かない | `member/21-troubleshooting › Integrations: MCP, cloud accounts, Jira, outside apps` | 1197 |
| `user/troubleshooting/terminal-phone` | ターミナルやスマートフォンで操作できない | `member/21-troubleshooting › Terminal and phone`<br>`member/badges-and-menus › When a menu doesn't appear` | 447 |
| `user/troubleshooting/faq` | よくある質問 | `member/21-troubleshooting`<br>`member/lite › 8. When you're stuck + FAQ` | 1061 |
| `user/troubleshooting/report` | 不具合を報告する・要望を出す | `member/21-troubleshooting › Reporting a bug or requesting a feature` | 81 |

### チーム管理（admin/）

**はじめに**

| ページ | タイトル | 元の節 | 語数 |
|---|---|---|--:|
| `admin/overview` | チーム管理者の仕事 | `admin/README` | 683 |

**メンバー**

| ページ | タイトル | 元の節 | 語数 |
|---|---|---|--:|
| `admin/members/roster` | メンバーの状況を見る | `admin/01-members` | 1321 |
| `admin/members/add` | メンバーを追加する | `admin/01-members › Adding a member`<br>`admin/01-members › Auto-join and invite-only` | 484 |
| `admin/members/remove` | メンバーを外す | `admin/01-members › Removing a member` | 519 |
| `admin/members/git-token` | メンバーの Git トークンを入れ替える | `admin/01-members › Rotating a member's git token` | 183 |

**リソース**

| ページ | タイトル | 元の節 | 語数 |
|---|---|---|--:|
| `admin/resources/overview` | リソースの使われかたを見る | `admin/02-limits` | 822 |
| `admin/resources/session-limits` | セッション数の上限を決める | `admin/02-limits › Two kinds of limits` | 520 |
| `admin/resources/engines` | 推論エンジンを使える人とモデルを決める | `admin/02-limits › Who may use the inference engines (you can set this)`<br>`admin/02-limits › Taking engine models in (only if your tenant was granted it)` | 495 |
| `admin/resources/workspace-size` | ワークスペースの大きさを決める | `admin/02-limits › Workspace size (memory, CPU, disk)`<br>`admin/02-limits › When someone says their home (`~`) is full`<br>`admin/02-limits › Machine (available on some deployments)` | 1142 |
| `admin/resources/idle-stop` | 放置されたワークスペースを止める | `admin/02-limits › Idle auto-stop`<br>`admin/02-limits › Force-stopping a workspace` | 646 |

**監査と使用量**

| ページ | タイトル | 元の節 | 語数 |
|---|---|---|--:|
| `admin/audit` | 監査ログを見る | `admin/03-audit-usage` | 1247 |
| `admin/usage` | 稼働時間とクラウド費用を見る | `admin/03-audit-usage › Running time ("Running time")`<br>`admin/03-audit-usage › Cloud cost ("Cloud cost")` | 368 |

**外部との接続**

| ページ | タイトル | 元の節 | 語数 |
|---|---|---|--:|
| `admin/mcp-distribute` | MCP サーバーを全員に配る | `admin/04-mcp-outside` | 1116 |
| `admin/memory-outside` | 外部からの記憶の利用を許可する | `admin/04-mcp-outside › Memory from outside Agent Fleet` | 285 |

**サインイン**

| ページ | タイトル | 元の節 | 語数 |
|---|---|---|--:|
| `admin/access/signin-methods` | サインインの方法を決める | `admin/05-access` | 331 |
| `admin/access/networks` | サインインできるネットワークを絞る | `admin/05-access › Allowed networks` | 229 |
| `admin/access/oauth-apps` | 連携に使う OAuth アプリを選ぶ | `admin/05-access › Integration OAuth apps` | 1194 |

**チームの既定値**

| ページ | タイトル | 元の節 | 語数 |
|---|---|---|--:|
| `admin/defaults/branch-rules` | ブランチ名の規則を決める | `admin/06-team-defaults` | 459 |
| `admin/defaults/members` | メンバーの既定値を決める | `admin/06-team-defaults › Member defaults` | 247 |

### セルフホスト（operate/）

**はじめに**

| ページ | タイトル | 元の節 | 語数 |
|---|---|---|--:|
| `operate/overview` | セルフホストの全体像 | `operate/README` | 1135 |
| `operate/choose` | デプロイ先を選ぶ | `operate/01-choose` | 1378 |

**インストール**

| ページ | タイトル | 元の節 | 語数 |
|---|---|---|--:|
| `operate/install` | インストールする | `operate/02-install` | 1603 |
| `operate/install-decisions` | テナントとプロビジョニングの方式を決める | `operate/02-install › 4. Decision points` | 1613 |

**日々の運用**

| ページ | タイトル | 元の節 | 語数 |
|---|---|---|--:|
| `operate/run/backup-restore` | バックアップして復元する | `operate/03-run` | 655 |
| `operate/run/upgrade` | アップグレードする | `operate/03-run › Upgrade` | 533 |
| `operate/run/air-gapped` | 閉じたネットワークに入れる | `operate/03-run › Installing into an air-gapped network` | 416 |
| `operate/run/fleet-policy` | 全エージェントに指示を配る | `operate/03-run › Distributing fleet policy (instructions to every agent)` | 349 |
| `operate/run/opencode-server` | opencode の共有サーバーを運用する | `operate/03-run › opencode 2: Terminal sessions and the shared server` | 297 |
| `operate/run/public-internet` | インターネットに公開する | `operate/03-run › Once it is on the public internet` | 239 |
| `operate/run/deployment-label` | 複数のデプロイを見分ける | `operate/03-run › Telling two deployments apart (colour and label)` | 434 |
| `operate/run/idle-stop` | アイドル停止と強制停止を使う | `operate/03-run › Idle stop and force-stop`<br>`operate/03-run › Pausing an idle deployment` | 1957 |
| `operate/ecs-ec2-slots` | ecs-ec2 のスロットを入れ替える・止める | `operate/11-slot-pool` | 1506 |

**セキュリティ**

| ページ | タイトル | 元の節 | 語数 |
|---|---|---|--:|
| `operate/secure/threat-model` | 脅威モデルと残るリスク | `operate/04-secure › Threat model (summary)`<br>`operate/04-secure › Residual risks: what to do about them`<br>`operate/04-secure › Reporting vulnerabilities` | 662 |
| `operate/secure/egress` | 外向きの通信を制御する | `operate/04-secure › Operating egress control` | 1180 |
| `operate/secure/mcp` | MCP と外部接続のサインインを運用する | `operate/04-secure › MCP servers and external connections` | 2107 |
| `operate/secure/dev-signin` | 開発用サインインを使う | `operate/04-secure › `AUTH=dev` is not a default`<br>`operate/04-secure › Development sign-in (dev OIDC IdP — super_admin only)` | 299 |
| `operate/secure/controls` | そのほかの運用上の制御 | `operate/04-secure` | 1260 |
| `operate/secure/offboarding` | アクセスを取り消す・super_admin を引き継ぐ | `operate/04-secure › Offboarding: how access is actually revoked`<br>`operate/04-secure › Handing over `super_admin`` | 874 |

**鍵**

| ページ | タイトル | 元の節 | 語数 |
|---|---|---|--:|
| `operate/keys/kms` | 保存時の鍵を AWS KMS にする | `operate/12-keys` | 1227 |
| `operate/keys/home-keys` | ホームごとに鍵を分ける | `operate/12-keys › A key of its own for each home` | 1629 |
| `operate/keys/bridge-tokens` | ブリッジトークンを入れ替える | `operate/12-keys › Rotating the bridge tokens` | 265 |

**サインイン**

| ページ | タイトル | 元の節 | 語数 |
|---|---|---|--:|
| `operate/signin/overview` | サインインの方法を設定する | `operate/05-signin` | 1312 |
| `operate/signin/google` | Google でサインインする | `operate/05-signin › 3. Google` | 316 |
| `operate/signin/entra` | Microsoft Entra ID でサインインする | `operate/05-signin › 4. Microsoft Entra ID` | 821 |
| `operate/signin/github` | GitHub でサインインする | `operate/05-signin › 5. GitHub` | 702 |
| `operate/signin/oidc` | そのほかの OIDC でサインインする | `operate/05-signin › 6. Okta, Keycloak, Auth0, Cognito, GitLab, and other OIDC IdPs` | 274 |
| `operate/signin/tenant-idp` | テナント独自のサインインを承認する | `operate/05-signin › 7. A sign-in method a tenant defines itself` | 1157 |

**推論エンジン**

| ページ | タイトル | 元の節 | 語数 |
|---|---|---|--:|
| `operate/engines/gpu` | 自前の GPU で推論エンジンを動かす | `operate/07-engines` | 1537 |
| `operate/engines/models` | 推論エンジンにモデルを取り込む | `operate/07-engines › Taking models in, and what that has to do with tenants` | 1904 |
| `operate/engines/status` | 推論エンジンの状態と履歴を見る | `operate/07-engines › Reading the current state`<br>`operate/07-engines › History (14 days)` | 496 |
| `operate/engines/read-aloud` | 読み上げエンジンを動かす | `operate/07-engines › Read aloud (the speech engine and the shared dictionary)` | 242 |
| `operate/engines/comfyui` | 自前の ComfyUI で画像を生成する | `operate/08-image-engine` | 3107 |
| `operate/engines/borrow` | 別のデプロイのエンジンを借りる | `operate/09-borrowed-engine` | 2795 |
| `operate/engines/llama-cpp` | LAN の llama.cpp でチャットする | `operate/10-llm-lan` | 1604 |

**困ったとき**

| ページ | タイトル | 元の節 | 語数 |
|---|---|---|--:|
| `operate/diagnose/checklist` | 症状から原因を探す | `operate/06-diagnose` | 2053 |
| `operate/diagnose/cannot-login` | ログインできない | `operate/05-signin › 9. When it still does not work`<br>`operate/06-diagnose › Cannot log in` | 722 |

### リファレンス（ref/）

**リファレンス**

| ページ | タイトル | 元の節 | 語数 |
|---|---|---|--:|
| `ref/overview` | リファレンスの読みかた | `ref/README` | 219 |
| `ref/features` | 機能の一覧 | `ref/features` | 3160 |
| `ref/agents` | エージェントごとの対応状況 | `ref/agents` | 6574 |
| `ref/repos` | リポジトリのサービスごとの対応状況 | `ref/repos` | 812 |
| `ref/deploy-targets` | デプロイ先ごとの違い | `ref/deploy-targets` | 2209 |
| `ref/roles` | ロールとできること | `admin/01-members › What the roles mean`<br>`ref/roles` | 980 |
| `ref/limits` | 上限と既定値 | `ref/limits` | 1795 |
| `ref/settings` | 設定の場所 | `member/20-settings`<br>`ref/settings` | 3094 |
| `ref/console-ui` | アイコン・バッジ・メニュー | `member/badges-and-menus` | 3318 |
| `ref/browser-pane` | ブラウザペインの仕様 | `ref/browser-pane` | 992 |
| `ref/glossary` | 用語集 | `ref/glossary` | 1828 |

**コマンド**

| ページ | タイトル | 元の節 | 語数 |
|---|---|---|--:|
| `ref/cli/README` | コマンドの一覧 | `member/15-external-services › CLIs that are already signed in` | 197 |
| `ref/cli/af-aws-exec` | af-aws-exec | `member/16-cloud-accounts › Using the profiles from the terminal, SDKs and build tools` | 3632 |
| `ref/cli/af-gcloud-exec` | af-gcloud-exec | `member/16-cloud-accounts › Running a command as a profile` | 917 |
| `ref/cli/af-db` | af-db | （新規） |  |
| `ref/cli/af-memory` | af-memory | （新規） |  |
| `ref/cli/af-scratch` | af-scratch | （新規） |  |
| `ref/cli/af-arch-repair` | af-arch-repair | （新規） |  |

**MCP ツール**

| ページ | タイトル | 元の節 | 語数 |
|---|---|---|--:|
| `ref/mcp/README` | af の MCP ツール | （新規） |  |
<!-- /generated:tree -->

## 元の節ごとの行き先

見出しのすべて（H1–H3）です。字下げは見出しの深さを表します。

<!-- generated:sections -->
| 元のファイル | 見出し | 語数 | 新しいページ |
|---|---|--:|---|
| `README.md` | Agent Fleet user guide | 189 | `user/start/overview` |
| `admin/01-members.md` | 01. Member management | 48 | `admin/members/roster` |
| `admin/01-members.md` | 　Finding your way around | 64 | `admin/members/roster` |
| `admin/01-members.md` | 　　The roster cards | 247 | `admin/members/roster` |
| `admin/01-members.md` | 　　Needs attention | 203 | `admin/members/roster` |
| `admin/01-members.md` | 　　Notifications to tenant admins | 234 | `admin/members/roster` |
| `admin/01-members.md` | 　　Where the numbers come from | 313 | `admin/members/roster` |
| `admin/01-members.md` | 　　Member detail | 212 | `admin/members/roster` |
| `admin/01-members.md` | 　Adding a member | 200 | `admin/members/add` |
| `admin/01-members.md` | 　　How email addresses relate to internal identifiers | 89 | `admin/members/add` |
| `admin/01-members.md` | 　Auto-join and invite-only | 195 | `admin/members/add` |
| `admin/01-members.md` | 　Removing a member | 519 | `admin/members/remove` |
| `admin/01-members.md` | 　Rotating a member's git token | 183 | `admin/members/git-token` |
| `admin/01-members.md` | 　What the roles mean | 206 | `ref/roles` |
| `admin/02-limits.md` | 02. Resource limits, idle auto-stop, and the sessions overview | 43 | `admin/resources/overview` |
| `admin/02-limits.md` | 　Two kinds of limits | 17 | `admin/resources/session-limits` |
| `admin/02-limits.md` | 　　Tenant-wide limits (set by super_admin) | 310 | `admin/resources/session-limits` |
| `admin/02-limits.md` | 　　Who may use the inference engines (you can set this) | 189 | `admin/resources/engines` |
| `admin/02-limits.md` | 　　Taking engine models in (only if your tenant was granted it) | 306 | `admin/resources/engines` |
| `admin/02-limits.md` | 　　The limit board (you can set this) | 117 | `admin/resources/session-limits` |
| `admin/02-limits.md` | 　　Per-member session limits (you can set these) | 76 | `admin/resources/session-limits` |
| `admin/02-limits.md` | 　　Workspace size (memory, CPU, disk) | 263 | `admin/resources/workspace-size` |
| `admin/02-limits.md` | 　　When someone says their home (`~`) is full | 258 | `admin/resources/workspace-size` |
| `admin/02-limits.md` | 　　Machine (available on some deployments) | 621 | `admin/resources/workspace-size` |
| `admin/02-limits.md` | 　Idle auto-stop | 353 | `admin/resources/idle-stop` |
| `admin/02-limits.md` | 　Viewing a member's resources | 293 | `admin/resources/overview` |
| `admin/02-limits.md` | 　Viewing sessions / getting the whole picture | 129 | `admin/resources/overview` |
| `admin/02-limits.md` | 　Force-stopping a workspace | 293 | `admin/resources/idle-stop` |
| `admin/02-limits.md` | 　What members experience when a limit is hit | 149 | `admin/resources/overview` |
| `admin/02-limits.md` | 　How to act when resources are under pressure | 208 | `admin/resources/overview` |
| `admin/03-audit-usage.md` | 03. Audit log and usage | 32 | `admin/audit` |
| `admin/03-audit-usage.md` | 　Audit log ("Audit") | 154 | `admin/audit` |
| `admin/03-audit-usage.md` | 　　What is recorded, and what is not | 380 | `admin/audit` |
| `admin/03-audit-usage.md` | 　　Operations that cannot be undone leave two rows | 177 | `admin/audit` |
| `admin/03-audit-usage.md` | 　Running time ("Running time") | 152 | `admin/usage` |
| `admin/03-audit-usage.md` | 　Cloud cost ("Cloud cost") | 216 | `admin/usage` |
| `admin/03-audit-usage.md` | 　FAQ | 504 | `admin/audit` |
| `admin/04-mcp-outside.md` | 04. MCP distribution and outside access | 37 | `admin/mcp-distribute` |
| `admin/04-mcp-outside.md` | 　Distributing an MCP server to everyone in the tenant (your permission) | 49 | `admin/mcp-distribute` |
| `admin/04-mcp-outside.md` | 　　Only remote (HTTP) can be distributed | 50 | `admin/mcp-distribute` |
| `admin/04-mcp-outside.md` | 　　Decide how credentials are handled (this is the important one) | 503 | `admin/mcp-distribute` |
| `admin/04-mcp-outside.md` | 　　When it takes effect | 74 | `admin/mcp-distribute` |
| `admin/04-mcp-outside.md` | 　　Practical notes | 80 | `admin/mcp-distribute` |
| `admin/04-mcp-outside.md` | 　MCP OAuth | 188 | `admin/mcp-distribute` |
| `admin/04-mcp-outside.md` | 　Memory from outside Agent Fleet | 85 | `admin/memory-outside` |
| `admin/04-mcp-outside.md` | 　　The switch | 200 | `admin/memory-outside` |
| `admin/04-mcp-outside.md` | 　Outbound traffic is not yours to control | 77 | `admin/mcp-distribute` |
| `admin/04-mcp-outside.md` | 　A template for asking upstream | 58 | `admin/mcp-distribute` |
| `admin/05-access.md` | 05. Who may sign in, and from where | 94 | `admin/access/signin-methods` |
| `admin/05-access.md` | 　Allowed networks | 229 | `admin/access/networks` |
| `admin/05-access.md` | 　Integration OAuth apps | 38 | `admin/access/oauth-apps` |
| `admin/05-access.md` | 　　GitHub: choose which app | 345 | `admin/access/oauth-apps` |
| `admin/05-access.md` | 　　Bitbucket and Jira | 811 | `admin/access/oauth-apps` |
| `admin/05-access.md` | 　Sign-in methods, and login rules | 237 | `admin/access/signin-methods` |
| `admin/06-team-defaults.md` | 06. Team defaults | 35 | `admin/defaults/branch-rules` |
| `admin/06-team-defaults.md` | 　Branch naming rules | 158 | `admin/defaults/branch-rules` |
| `admin/06-team-defaults.md` | 　　Editing the rules | 204 | `admin/defaults/branch-rules` |
| `admin/06-team-defaults.md` | 　　When it reaches members | 62 | `admin/defaults/branch-rules` |
| `admin/06-team-defaults.md` | 　Member defaults | 110 | `admin/defaults/members` |
| `admin/06-team-defaults.md` | 　　Setting the default agent | 67 | `admin/defaults/members` |
| `admin/06-team-defaults.md` | 　　When members see it | 70 | `admin/defaults/members` |
| `admin/README.md` | Administering a tenant | 52 | `admin/overview` |
| `admin/README.md` | 　The short version | 52 | `admin/overview` |
| `admin/README.md` | 　Chapters | 97 | `admin/overview` |
| `admin/README.md` | 　Getting in | 60 | `admin/overview` |
| `admin/README.md` | 　What is yours, and what is not | 299 | `admin/overview` |
| `admin/README.md` | 　Your first day as an administrator | 123 | `admin/overview` |
| `member/01-first-day.md` | 01. First day — from login to your first session | 3 | `user/start/quickstart` |
| `member/01-first-day.md` | 　Log in | 119 | `user/start/quickstart` |
| `member/01-first-day.md` | 　Home and the welcome card — 2 steps + picking a goal | 419 | `user/start/quickstart` |
| `member/01-first-day.md` | 　　It's fine to close the card | 173 | `user/start/quickstart` |
| `member/01-first-day.md` | 　Clone your first repository | 120 | `user/start/quickstart` |
| `member/01-first-day.md` | 　At the end of the day — is it OK to stop the workspace? | 183 | `user/start/end-of-day` |
| `member/01-first-day.md` | 　　"A new version is available" and the **Restart needed** badge | 114 | `user/start/end-of-day` |
| `member/01-first-day.md` | 　　End-of-first-day checklist | 105 | `user/start/end-of-day` |
| `member/02-console-basics.md` | 02. Console basics — shortcuts, command palette, panes, phones | 51 | `user/start/console-tour` |
| `member/02-console-basics.md` | 　Shortcuts | 437 | `user/start/shortcuts` |
| `member/02-console-basics.md` | 　Command palette | 36 | `user/start/shortcuts` |
| `member/02-console-basics.md` | 　　Sessions | 293 | `user/start/shortcuts` |
| `member/02-console-basics.md` | 　　Keys inside the palette | 261 | `user/start/shortcuts` |
| `member/02-console-basics.md` | 　　Conversations | 204 | `user/start/shortcuts` |
| `member/02-console-basics.md` | 　　Memory | 109 | `user/start/shortcuts` |
| `member/02-console-basics.md` | 　Arranging multiple views (panes) | 433 | `user/start/panes` |
| `member/02-console-basics.md` | 　Using it on a phone | 365 | `user/start/phone` |
| `member/03-starting-sessions.md` | 03. Starting a session — kinds, execution method, the Start dialog, the issue tracker | 97 | `user/sessions/start` |
| `member/03-starting-sessions.md` | 　Session types | 169 | `user/sessions/start` |
| `member/03-starting-sessions.md` | 　Execution method — Managed and Terminal (CLI) | 335 | `user/sessions/start` |
| `member/03-starting-sessions.md` | 　Creating a new session — "Start" at the top of the screen | 249 | `user/sessions/start` |
| `member/03-starting-sessions.md` | 　　Worktrees and new branches — the key to parallel work | 272 | `user/sessions/worktrees` |
| `member/03-starting-sessions.md` | 　　Working folder — starting inside a subfolder | 180 | `user/sessions/worktrees` |
| `member/03-starting-sessions.md` | 　Starting from the issue tracker | 93 | `user/sessions/from-issues` |
| `member/03-starting-sessions.md` | 　　Reading the list | 378 | `user/sessions/from-issues` |
| `member/03-starting-sessions.md` | 　　From a row to a session | 605 | `user/sessions/from-issues` |
| `member/03-starting-sessions.md` | 　　Pull request details | 489 | `user/sessions/from-issues` |
| `member/03-starting-sessions.md` | 　　From a ticket number in the conversation | 291 | `user/sessions/from-issues` |
| `member/03-starting-sessions.md` | 　Reading state — badges and notifications | 443 | `user/sessions/status` |
| `member/03-starting-sessions.md` | 　Changing the title and branch name | 212 | `user/sessions/start` |
| `member/04-conversation.md` | 04. Talking to a session — replying, plans, highlights, suggestions, translation | 58 | `user/sessions/reply` |
| `member/04-conversation.md` | 　Reading and replying to a running agent's conversation | 342 | `user/sessions/reply` |
| `member/04-conversation.md` | 　　Questions and plans left by a stopped session | 216 | `user/sessions/reply` |
| `member/04-conversation.md` | 　　Stopping a turn when something is queued | 643 | `user/sessions/queue` |
| `member/04-conversation.md` | 　　Holding follow-ups before sending (send queue) | 378 | `user/sessions/queue` |
| `member/04-conversation.md` | 　　Reusing something you sent earlier | 197 | `user/sessions/reply` |
| `member/04-conversation.md` | 　　Writing comments on a plan | 107 | `user/sessions/plans` |
| `member/04-conversation.md` | 　　Having another session review the plan | 690 | `user/sessions/plans` |
| `member/04-conversation.md` | 　　Calling a skill or a command | 168 | `user/sessions/skills` |
| `member/04-conversation.md` | 　　Reply suggestions | 218 | `user/sessions/reply` |
| `member/04-conversation.md` | 　　Branch from a past message | 261 | `user/sessions/branch-message` |
| `member/04-conversation.md` | 　Highlighting a line in a conversation | 162 | `user/sessions/reply` |
| `member/04-conversation.md` | 　Seeing what a session changed | 174 | `user/sessions/changes` |
| `member/04-conversation.md` | 　When a turn is interrupted | 133 | `user/troubleshooting/sessions` |
| `member/04-conversation.md` | 　Saving a conversation as Markdown | 219 | `user/sessions/export` |
| `member/04-conversation.md` | 　Reading an answer in your own language (translation) | 261 | `user/sessions/translate` |
| `member/05-stopping-and-tidying.md` | 05. Stopping, resuming and tidying up | 45 | `user/sessions/stop-resume` |
| `member/05-stopping-and-tidying.md` | 　Stopping and tidying up sessions | 721 | `user/sessions/stop-resume` |
| `member/05-stopping-and-tidying.md` | 　　Tidying up in bulk (cleanup) | 777 | `user/sessions/cleanup` |
| `member/05-stopping-and-tidying.md` | 　　Clearing one finished job (deleting a working copy) | 266 | `user/sessions/cleanup` |
| `member/05-stopping-and-tidying.md` | 　　A spend budget — pausing a session that spends too much | 361 | `user/sessions/budget` |
| `member/05-stopping-and-tidying.md` | 　When you can — and can't — resume | 530 | `user/sessions/stop-resume` |
| `member/05-stopping-and-tidying.md` | 　　A claude session whose conversation log was deleted | 488 | `user/troubleshooting/sessions` |
| `member/05-stopping-and-tidying.md` | 　　The warning when the branch has been swapped | 82 | `user/sessions/stop-resume` |
| `member/05-stopping-and-tidying.md` | 　Continuing elsewhere — handoff, branch, move | 212 | `user/sessions/handoff` |
| `member/05-stopping-and-tidying.md` | 　　Handing a conversation off (handoff) | 226 | `user/sessions/handoff` |
| `member/05-stopping-and-tidying.md` | 　　Moving a session to another agent (move) | 792 | `user/sessions/handoff` |
| `member/05-stopping-and-tidying.md` | 　Keeping a session awake | 65 | `user/sessions/auto-stop` |
| `member/05-stopping-and-tidying.md` | 　Having a session stop when it is done | 244 | `user/sessions/auto-stop` |
| `member/05-stopping-and-tidying.md` | 　Locking something against deletion | 96 | `user/sessions/cleanup` |
| `member/06-code.md` | 06. Repositories and git — cloning, reviewing changes, committing, pushing | 3 | `user/code/clone` |
| `member/06-code.md` | 　Connect a git provider | 254 | `user/code/connect-git` |
| `member/06-code.md` | 　Clone a repository | 115 | `user/code/clone` |
| `member/06-code.md` | 　Starting with nothing to import from (a new folder) | 179 | `user/code/clone` |
| `member/06-code.md` | 　　Submodules and Git LFS | 198 | `user/code/clone` |
| `member/06-code.md` | 　The built-in git provider (internal Git) | 159 | `user/code/internal-git` |
| `member/06-code.md` | 　Launch a session from a repository row | 483 | `user/code/launch-from-repo` |
| `member/06-code.md` | 　　First-prompt templates | 263 | `user/code/launch-from-repo` |
| `member/06-code.md` | 　　What you can do with right-click | 296 | `user/code/launch-from-repo` |
| `member/06-code.md` | 　　Initialize Git Flow | 353 | `user/code/git-flow` |
| `member/06-code.md` | 　Commit in the commit graph view | 156 | `user/code/commit` |
| `member/06-code.md` | 　　Changes → stage → commit | 102 | `user/code/commit` |
| `member/06-code.md` | 　　History and diffs | 54 | `user/code/commit` |
| `member/06-code.md` | 　Push and authentication | 61 | `user/code/connect-git` |
| `member/06-code.md` | 　Subversion (SVN) repositories | 504 | `user/code/svn` |
| `member/07-files.md` | 07. Files — tree, viewer, Markdown/slides | 3 | `user/files/browse` |
| `member/07-files.md` | 　File tree | 172 | `user/files/browse` |
| `member/07-files.md` | 　　Open a shell from a folder | 55 | `user/files/browse` |
| `member/07-files.md` | 　　Download a folder as zip | 630 | `user/files/browse` |
| `member/07-files.md` | 　　Why some folders are invisible | 53 | `user/files/browse` |
| `member/07-files.md` | 　File viewer | 107 | `user/files/view` |
| `member/07-files.md` | 　　Markdown and Mermaid | 59 | `user/files/view` |
| `member/07-files.md` | 　　Links in rendered Markdown | 390 | `user/files/view` |
| `member/07-files.md` | 　　Marp slides | 51 | `user/files/view` |
| `member/07-files.md` | 　　Diagrams (`.drawio`) | 286 | `user/files/view` |
| `member/07-files.md` | 　　PDFs and Office documents | 266 | `user/files/view` |
| `member/07-files.md` | 　Editing a file | 227 | `user/files/edit` |
| `member/07-files.md` | 　　Have an AI propose the change | 72 | `user/files/edit` |
| `member/07-files.md` | 　Send a file to a session / chat | 136 | `user/files/send` |
| `member/08-terminal.md` | 08. Terminal — copy & paste, round-trip time, font and size | 104 | `user/files/terminal` |
| `member/08-terminal.md` | 　Copy & paste | 315 | `user/files/terminal` |
| `member/08-terminal.md` | 　How far away the terminal is (round-trip time) | 154 | `user/files/terminal` |
| `member/08-terminal.md` | 　Changing the font and size | 98 | `user/files/terminal` |
| `member/09-agents.md` | 09. Agents — connecting one, and choosing between them | 18 | `user/agents/choose` |
| `member/09-agents.md` | 　Supported agents and how to choose | 366 | `user/agents/choose` |
| `member/09-agents.md` | 　Model prices and usage chips | 280 | `user/agents/usage` |
| `member/09-agents.md` | 　Default model for the assistant chat | 138 | `user/chat/assistant` |
| `member/09-agents.md` | 　Claude | 1062 | `user/agents/claude` |
| `member/09-agents.md` | 　Codex | 133 | `user/agents/codex` |
| `member/09-agents.md` | 　OpenCode | 853 | `user/agents/opencode` |
| `member/09-agents.md` | 　　When the provider returns an error | 186 | `user/agents/opencode` |
| `member/09-agents.md` | 　　How opencode 2 differs | 55 | `user/agents/opencode` |
| `member/09-agents.md` | 　GitHub Copilot | 100 | `user/agents/copilot` |
| `member/09-agents.md` | 　Cursor | 157 | `user/agents/cursor` |
| `member/09-agents.md` | 　Kiro | 229 | `user/agents/kiro` |
| `member/09-agents.md` | 　Antigravity (agy) | 458 | `user/agents/agy` |
| `member/09-agents.md` | 　Muse Code | 406 | `user/agents/muse` |
| `member/09-agents.md` | 　lcpp | 303 | `user/agents/lcpp` |
| `member/09-agents.md` | 　Checking remaining context | 94 | `user/agents/usage` |
| `member/09-agents.md` | 　RTK (token savings) | 83 | `user/agents/usage` |
| `member/09-agents.md` | 　Agent instructions (write down how you work, once) | 365 | `user/agents/instructions` |
| `member/09-agents.md` | 　Bringing your personal Claude Code setup | 762 | `user/agents/bring-claude-setup` |
| `member/10-chat-memo.md` | 10. Chat and memos — quick questions, translation, and memo capture | 3 | `user/chat/assistant` |
| `member/10-chat-memo.md` | 　What the assistant chat is | 241 | `user/chat/assistant` |
| `member/10-chat-memo.md` | 　　Purpose-built assistants and translation | 408 | `user/chat/purpose-assistants` |
| `member/10-chat-memo.md` | 　　Switching the agent mid-conversation | 329 | `user/chat/assistant` |
| `member/10-chat-memo.md` | 　　When a conversation gets long (a context rule of thumb) | 276 | `user/chat/assistant` |
| `member/10-chat-memo.md` | 　　Put what must not be forgotten in the work plan | 126 | `user/chat/assistant` |
| `member/10-chat-memo.md` | 　Memo queue | 416 | `user/chat/memos` |
| `member/11-many-sessions.md` | 11. Running many sessions at once — overview, child sessions, the Fleet Operator | 43 | `user/fleet/operator` |
| `member/11-many-sessions.md` | 　Seeing every running session at once (the sessions overview) | 835 | `user/fleet/overview` |
| `member/11-many-sessions.md` | 　　Seeing how sessions relate over time (the fleet graph) | 608 | `user/fleet/graph` |
| `member/11-many-sessions.md` | 　Narrowing the view with working sets | 245 | `user/fleet/working-sets` |
| `member/11-many-sessions.md` | 　Starting sessions from a session (child sessions) | 1105 | `user/fleet/child-sessions` |
| `member/11-many-sessions.md` | 　Messages between sessions | 837 | `user/fleet/messages` |
| `member/11-many-sessions.md` | 　　How this differs from Claude Code's own version | 223 | `user/fleet/messages` |
| `member/11-many-sessions.md` | 　Telling a session about its pull request's feedback | 358 | `user/fleet/pr-feedback` |
| `member/11-many-sessions.md` | 　Letting a session see the fleet | 324 | `user/fleet/fleet-visibility` |
| `member/11-many-sessions.md` | 　What is the Fleet Operator? | 160 | `user/fleet/operator` |
| `member/11-many-sessions.md` | 　What it can do | 0 | `user/fleet/operator` |
| `member/11-many-sessions.md` | 　　See (read) | 260 | `user/fleet/operator` |
| `member/11-many-sessions.md` | 　　Drive (write) | 413 | `user/fleet/operator` |
| `member/11-many-sessions.md` | 　　Session reports and auto-reply | 486 | `user/fleet/operator` |
| `member/11-many-sessions.md` | 　Basic usage | 125 | `user/fleet/operator` |
| `member/11-many-sessions.md` | 　Use-case patterns | 23 | `user/fleet/operator-patterns` |
| `member/11-many-sessions.md` | 　　Pattern 1: research session → handover to the operator → parallel implementation → integration | 244 | `user/fleet/operator-patterns` |
| `member/11-many-sessions.md` | 　　Pattern 2: fan-out of same-kind fixes | 99 | `user/fleet/operator-patterns` |
| `member/11-many-sessions.md` | 　　Pattern 3: agent comparison / cross-review | 96 | `user/fleet/operator-patterns` |
| `member/11-many-sessions.md` | 　　Pattern 4: serial pipeline (implement → test → review) | 79 | `user/fleet/operator-patterns` |
| `member/11-many-sessions.md` | 　　Pattern 5: status briefing and memo triage | 223 | `user/fleet/operator-patterns` |
| `member/11-many-sessions.md` | 　Scheduled runs | 561 | `user/fleet/schedules` |
| `member/11-many-sessions.md` | 　Constraints and caveats | 507 | `user/fleet/operator` |
| `member/12-collaboration.md` | 12. Working with others — sharing, handing over, the inbox, usage limits | 40 | `user/team/hand-over` |
| `member/12-collaboration.md` | 　Sharing and handing over | 71 | `user/team/hand-over` |
| `member/12-collaboration.md` | 　Handing a session to another member | 571 | `user/team/hand-over` |
| `member/12-collaboration.md` | 　Asking a teammate: the inbox | 770 | `user/team/inbox` |
| `member/12-collaboration.md` | 　Showing teammates where you stand on usage limits | 379 | `user/team/usage-limits` |
| `member/12-collaboration.md` | 　Sharing a conversation (shared sessions) | 507 | `user/team/share` |
| `member/13-images.md` | 13. Images — gallery, generation, studio | 29 | `user/images/gallery` |
| `member/13-images.md` | 　Image gallery | 1114 | `user/images/gallery` |
| `member/13-images.md` | 　Image generation | 1451 | `user/images/generate` |
| `member/13-images.md` | 　　Studio — refine the draft by talking to an agent | 1220 | `user/images/studio` |
| `member/13-images.md` | 　Having a session generate an image | 849 | `user/images/from-session` |
| `member/14-preview-browser.md` | 14. Preview and browser — browser pane, preview URLs, dev sign-in, an agent's browser | 40 | `user/preview/browser-pane` |
| `member/14-preview-browser.md` | 　Viewing a web app you started — browser pane and lightweight preview | 715 | `user/preview/browser-pane` |
| `member/14-preview-browser.md` | 　　How to use it | 138 | `user/preview/browser-pane` |
| `member/14-preview-browser.md` | 　　Preview subdomains (only where they are issued) | 1168 | `user/preview/subdomains` |
| `member/14-preview-browser.md` | 　　Examples by setup | 208 | `user/preview/browser-pane` |
| `member/14-preview-browser.md` | 　　Status display and recovery | 231 | `user/preview/browser-pane` |
| `member/14-preview-browser.md` | 　　Limits and transience (good to know) | 211 | `user/preview/browser-pane` |
| `member/14-preview-browser.md` | 　Signing in with Google on a preview URL (development OIDC IdP) | 973 | `user/preview/dev-signin` |
| `member/14-preview-browser.md` | 　　Using it from an app on your own machine | 296 | `user/preview/dev-signin` |
| `member/14-preview-browser.md` | 　Operating a browser the agent opened | 291 | `user/preview/agent-browser` |
| `member/15-external-services.md` | 15. External services and signed-in CLIs — gh / bkt / jira / confluence, Discord / Slack, ops tooling | 51 | `user/integrations/gh-bkt` |
| `member/15-external-services.md` | 　Use `gh` and `bkt` in a session | 266 | `user/integrations/gh-bkt` |
| `member/15-external-services.md` | 　Use `jira` in a session | 1308 | `user/integrations/jira` |
| `member/15-external-services.md` | 　Use `confluence` in a session | 557 | `user/integrations/confluence` |
| `member/15-external-services.md` | 　CLIs that are already signed in | 197 | `ref/cli/README` |
| `member/15-external-services.md` | 　Connecting Discord / Slack (chat bridge) | 365 | `user/integrations/chat-bridge` |
| `member/15-external-services.md` | 　PagerDuty / Grafana / CloudWatch / AWS connect from the "Ops & monitoring" tab (recommended) | 503 | `user/integrations/ops-monitoring` |
| `member/15-external-services.md` | 　　Amazon Managed Grafana: issuing the token | 74 | `user/integrations/ops-monitoring` |
| `member/15-external-services.md` | 　　Other tools (Zabbix and the like) | 235 | `user/integrations/ops-monitoring` |
| `member/16-cloud-accounts.md` | 16. Cloud accounts — AWS profiles, SSM hosts and Google Cloud | 3 | `user/integrations/aws-sso` |
| `member/16-cloud-accounts.md` | 　Logging in to another in-house host (SSM) | 820 | `user/integrations/aws-ssm` |
| `member/16-cloud-accounts.md` | 　　Importing profiles from ~/.aws/config | 594 | `user/integrations/aws-sso` |
| `member/16-cloud-accounts.md` | 　　Importing SSM hosts from ~/.ssh/config | 411 | `user/integrations/aws-ssm` |
| `member/16-cloud-accounts.md` | 　　Exporting profiles as ~/.aws/config | 287 | `user/integrations/aws-sso` |
| `member/16-cloud-accounts.md` | 　　Shared sign-ins: one login for several profiles | 835 | `user/integrations/aws-sso` |
| `member/16-cloud-accounts.md` | 　　Profile type: assume a role from another profile | 442 | `user/integrations/aws-sso` |
| `member/16-cloud-accounts.md` | 　　Using the profiles from the terminal, SDKs and build tools | 3632 | `ref/cli/af-aws-exec` |
| `member/16-cloud-accounts.md` | 　　The AWS badge in the WS bar | 271 | `user/integrations/aws-sso` |
| `member/16-cloud-accounts.md` | 　Running commands in Google Cloud as you (af-gcloud-exec) | 374 | `user/integrations/gcloud` |
| `member/16-cloud-accounts.md` | 　　Importing profiles from gcloud configurations | 266 | `user/integrations/gcloud` |
| `member/16-cloud-accounts.md` | 　　Running a command as a profile | 917 | `ref/cli/af-gcloud-exec` |
| `member/16-cloud-accounts.md` | 　　Logging in | 1036 | `user/integrations/gcloud` |
| `member/16-cloud-accounts.md` | 　　The Google Cloud badge in the WS bar | 310 | `user/integrations/gcloud` |
| `member/16-cloud-accounts.md` | 　　When it stops | 541 | `user/integrations/gcloud` |
| `member/17-workspace-environment.md` | 17. Workspace environment — settings, recreating, test databases, a local AWS emulator | 31 | `user/workspace/recreate` |
| `member/17-workspace-environment.md` | 　Environment settings and recreating the workspace | 325 | `user/workspace/recreate` |
| `member/17-workspace-environment.md` | 　　Recreating the workspace (danger zone) | 163 | `user/workspace/recreate` |
| `member/17-workspace-environment.md` | 　　Cleaning home (an even deeper reset) | 106 | `user/workspace/recreate` |
| `member/17-workspace-environment.md` | 　Running database-backed tests | 509 | `user/workspace/databases` |
| `member/17-workspace-environment.md` | 　　MySQL | 188 | `user/workspace/databases` |
| `member/17-workspace-environment.md` | 　　Console Databases tab | 399 | `user/workspace/databases` |
| `member/17-workspace-environment.md` | 　Trying AWS code against a local emulator (MiniStack) | 576 | `user/workspace/aws-emulator` |
| `member/18-agent-memory.md` | 18. Agent memory — what agents remember, and how you keep it | 40 | `user/memory/overview` |
| `member/18-agent-memory.md` | 　Agent memory | 203 | `user/memory/overview` |
| `member/18-agent-memory.md` | 　　Memories | 1228 | `user/memory/overview` |
| `member/18-agent-memory.md` | 　　Changes | 465 | `user/memory/changes` |
| `member/18-agent-memory.md` | 　　Import & export | 1720 | `user/memory/import-export` |
| `member/18-agent-memory.md` | 　　Settings | 1202 | `user/memory/settings` |
| `member/18-agent-memory.md` | 　Memory snapshots | 84 | `user/memory/snapshots` |
| `member/18-agent-memory.md` | 　　History | 153 | `user/memory/snapshots` |
| `member/18-agent-memory.md` | 　　Targets | 95 | `user/memory/snapshots` |
| `member/18-agent-memory.md` | 　　Export & import (Memory snapshots) | 147 | `user/memory/snapshots` |
| `member/18-agent-memory.md` | 　Using Agent Fleet memory from an external agent | 743 | `user/memory/external` |
| `member/18-agent-memory.md` | 　　Bringing your own Claude Code's memory into Agent Fleet | 575 | `user/memory/external` |
| `member/19-outside-access.md` | 19. Using your workspace from outside — MCP and OAuth | 51 | `user/outside/external-claude` |
| `member/19-outside-access.md` | 　Using your workspace from an external agent (MCP) | 66 | `user/outside/external-claude` |
| `member/19-outside-access.md` | 　　Driving your workspace from an external Claude (MCP) | 538 | `user/outside/external-claude` |
| `member/19-outside-access.md` | 　　Connecting a remote MCP client by signing in (OAuth) | 683 | `user/outside/oauth-client` |
| `member/19-outside-access.md` | 　　Moving work from your own Claude Code into the workspace | 775 | `user/outside/move-work-in` |
| `member/19-outside-access.md` | 　　A memory-only connector (for claude.ai) | 207 | `user/memory/external` |
| `member/19-outside-access.md` | 　　Do not connect this deployment's /mcp to a session | 324 | `user/outside/external-claude` |
| `member/19-outside-access.md` | 　　Using Agent Fleet memory from an external agent | 27 | `user/memory/external` |
| `member/20-settings.md` | 20. Settings — every tab of the ⚙ settings dialog | 20 | `ref/settings` |
| `member/20-settings.md` | 　Opening it, and how it is organised | 234 | `ref/settings` |
| `member/20-settings.md` | 　　When a change takes effect | 192 | `ref/settings` |
| `member/20-settings.md` | 　Personal | 0 | `ref/settings` |
| `member/20-settings.md` | 　　Display | 392 | `user/settings/display` |
| `member/20-settings.md` | 　　Account | 277 | `user/settings/display` |
| `member/20-settings.md` | 　　Keyboard | 215 | `user/start/shortcuts` |
| `member/20-settings.md` | 　　Read aloud | 160 | `user/settings/read-aloud` |
| `member/20-settings.md` | 　　Notifications | 583 | `user/settings/notifications` |
| `member/20-settings.md` | 　　Limit board | 54 | `user/team/usage-limits` |
| `member/20-settings.md` | 　　Assistant | 340 | `user/chat/assistant` |
| `member/20-settings.md` | 　　AI assistance | 617 | `user/chat/purpose-assistants` |
| `member/20-settings.md` | 　　Agent instructions | 66 | `user/agents/instructions` |
| `member/20-settings.md` | 　　Skills | 109 | `user/agents/bring-claude-setup` |
| `member/20-settings.md` | 　　Agent memory | 29 | `user/memory/settings` |
| `member/20-settings.md` | 　　Memory snapshots | 21 | `user/memory/snapshots` |
| `member/20-settings.md` | 　Connections | 0 | `ref/settings` |
| `member/20-settings.md` | 　　Agents | 182 | `user/agents/choose` |
| `member/20-settings.md` | 　　Git hosting | 100 | `user/code/connect-git` |
| `member/20-settings.md` | 　　Ops & monitoring | 48 | `user/integrations/ops-monitoring` |
| `member/20-settings.md` | 　　Issue tracker | 414 | `user/integrations/issue-tracker` |
| `member/20-settings.md` | 　　Chat | 21 | `user/integrations/chat-bridge` |
| `member/20-settings.md` | 　　MCP servers (used by sessions) | 1336 | `user/integrations/mcp-servers` |
| `member/20-settings.md` | 　　AWS profiles/SSM | 80 | `user/integrations/aws-sso` |
| `member/20-settings.md` | 　　Google Cloud | 107 | `user/integrations/gcloud` |
| `member/20-settings.md` | 　Outside access | 0 | `ref/settings` |
| `member/20-settings.md` | 　　MCP tokens & apps | 89 | `user/outside/external-claude` |
| `member/20-settings.md` | 　Workspace | 0 | `ref/settings` |
| `member/20-settings.md` | 　　Agent usage | 390 | `user/agents/usage` |
| `member/20-settings.md` | 　　Cloud cost | 179 | `user/workspace/cost` |
| `member/20-settings.md` | 　　Running time | 188 | `user/workspace/cost` |
| `member/20-settings.md` | 　　Machine | 1263 | `user/workspace/machine` |
| `member/20-settings.md` | 　　Toolchains | 282 | `user/workspace/toolchains` |
| `member/20-settings.md` | 　　Databases | 62 | `user/workspace/databases` |
| `member/20-settings.md` | 　　Preview subdomains | 100 | `user/preview/subdomains` |
| `member/20-settings.md` | 　　Internal repos | 42 | `user/code/internal-git` |
| `member/20-settings.md` | 　　Export / import | 313 | `user/workspace/export-import` |
| `member/20-settings.md` | 　　Danger zone | 45 | `user/workspace/recreate` |
| `member/20-settings.md` | 　What you want to do → which tab | 495 | `ref/settings` |
| `member/21-troubleshooting.md` | 21. Troubleshooting — fixes by symptom and FAQ | 179 | `user/troubleshooting/faq` |
| `member/21-troubleshooting.md` | 　Workspace: start, stop and disk | 91 | `user/troubleshooting/workspace` |
| `member/21-troubleshooting.md` | 　　A **Restart needed** badge sits next to the power button | 45 | `user/troubleshooting/workspace` |
| `member/21-troubleshooting.md` | 　　A **Not responding** badge sits next to the power button | 134 | `user/troubleshooting/workspace` |
| `member/21-troubleshooting.md` | 　　The workspace went from "starting" to "stopped" on its own | 82 | `user/troubleshooting/workspace` |
| `member/21-troubleshooting.md` | 　　The workspace has stopped without me noticing | 34 | `user/troubleshooting/workspace` |
| `member/21-troubleshooting.md` | 　　"Your home disk is nearly full" | 94 | `user/troubleshooting/workspace` |
| `member/21-troubleshooting.md` | 　　Starting a session says the agent's CLI could not be installed | 133 | `user/troubleshooting/workspace` |
| `member/21-troubleshooting.md` | 　Sessions: resuming, sharing, tidying | 135 | `user/troubleshooting/sessions` |
| `member/21-troubleshooting.md` | 　　Sessions or repositories have vanished from the left pane | 169 | `user/troubleshooting/sessions` |
| `member/21-troubleshooting.md` | 　　A session won't resume / is shown struck through | 66 | `user/troubleshooting/sessions` |
| `member/21-troubleshooting.md` | 　　Resuming says "the conversation log was deleted" | 181 | `user/troubleshooting/sessions` |
| `member/21-troubleshooting.md` | 　　A session cannot be moved to another agent | 52 | `user/troubleshooting/sessions` |
| `member/21-troubleshooting.md` | 　　Cleanup won't remove some things | 92 | `user/troubleshooting/sessions` |
| `member/21-troubleshooting.md` | 　　I shared it, but the recipient sees nothing — or only old conversations | 110 | `user/troubleshooting/sessions` |
| `member/21-troubleshooting.md` | 　　I sent something from a session shared with me, but the agent does nothing | 72 | `user/troubleshooting/sessions` |
| `member/21-troubleshooting.md` | 　　A scheduled run doesn't fire | 119 | `user/troubleshooting/sessions` |
| `member/21-troubleshooting.md` | 　　No notifications arrive | 57 | `user/troubleshooting/sessions` |
| `member/21-troubleshooting.md` | 　　claude doesn't know `/list-agents`, or says it can't message another session | 108 | `user/troubleshooting/sessions` |
| `member/21-troubleshooting.md` | 　Agents: sign-in and models | 98 | `user/troubleshooting/agents` |
| `member/21-troubleshooting.md` | 　　Selecting claude shows a login screen ("Select login method") | 69 | `user/troubleshooting/agents` |
| `member/21-troubleshooting.md` | 　　I want to connect codex, but approving doesn't get me anywhere | 32 | `user/troubleshooting/agents` |
| `member/21-troubleshooting.md` | 　　An agent stopped with "your login has expired" | 164 | `user/troubleshooting/agents` |
| `member/21-troubleshooting.md` | 　　A Claude session shows "Login expired — sign in again", or sending starts nothing | 233 | `user/troubleshooting/agents` |
| `member/21-troubleshooting.md` | 　　A model I want isn't offered, or launching with it is refused | 85 | `user/troubleshooting/agents` |
| `member/21-troubleshooting.md` | 　　The launch dialog offers only "Default" | 194 | `user/troubleshooting/agents` |
| `member/21-troubleshooting.md` | 　　An opencode session says "working" but nothing arrives | 109 | `user/troubleshooting/agents` |
| `member/21-troubleshooting.md` | 　　Starting opencode says "This opencode version is not supported" | 37 | `user/troubleshooting/agents` |
| `member/21-troubleshooting.md` | 　Assistants | 40 | `user/troubleshooting/agents` |
| `member/21-troubleshooting.md` | 　　The assistant (operator) stopped carrying things forward on its own | 81 | `user/troubleshooting/agents` |
| `member/21-troubleshooting.md` | 　　The chat says the context went over the limit and won't answer | 74 | `user/troubleshooting/agents` |
| `member/21-troubleshooting.md` | 　Repositories and git | 39 | `user/troubleshooting/git` |
| `member/21-troubleshooting.md` | 　　Cloning fails | 51 | `user/troubleshooting/git` |
| `member/21-troubleshooting.md` | 　　A session says the submodules are missing / broken | 60 | `user/troubleshooting/git` |
| `member/21-troubleshooting.md` | 　　Authentication errors on a private repository | 43 | `user/troubleshooting/git` |
| `member/21-troubleshooting.md` | 　Preview and browser | 123 | `user/troubleshooting/preview` |
| `member/21-troubleshooting.md` | 　　The browser pane shows `target-unreachable` / goes blank or 404 | 199 | `user/troubleshooting/preview` |
| `member/21-troubleshooting.md` | 　　The preview URL I gave a colleague returns 404 | 109 | `user/troubleshooting/preview` |
| `member/21-troubleshooting.md` | 　　HMR (live reload) doesn't work / no automatic refresh / the shell renders but no data | 218 | `user/troubleshooting/preview` |
| `member/21-troubleshooting.md` | 　　Every API call in the preview returns 401 (`preview requires sign-in`) | 88 | `user/troubleshooting/preview` |
| `member/21-troubleshooting.md` | 　　The browser pane shows `crashed` / `disconnected`, or keeps dying | 87 | `user/troubleshooting/preview` |
| `member/21-troubleshooting.md` | 　　Signing in on a preview URL shows an Agent Fleet error page | 154 | `user/troubleshooting/preview` |
| `member/21-troubleshooting.md` | 　　A preview URL says the port changed, too many ports are open, or the workspace must restart | 120 | `user/troubleshooting/preview` |
| `member/21-troubleshooting.md` | 　Integrations: MCP, cloud accounts, Jira, outside apps | 103 | `user/troubleshooting/integrations` |
| `member/21-troubleshooting.md` | 　　An MCP server I registered isn't available in sessions or assistants | 356 | `user/troubleshooting/integrations` |
| `member/21-troubleshooting.md` | 　　An MCP server's row says "Sign in again", "More permission needed" or shows an unfinished sign-in | 230 | `user/troubleshooting/integrations` |
| `member/21-troubleshooting.md` | 　　An outside app connects but shows no tools | 54 | `user/troubleshooting/integrations` |
| `member/21-troubleshooting.md` | 　　Jira says boards, sprints and epics are "not available" | 102 | `user/troubleshooting/integrations` |
| `member/21-troubleshooting.md` | 　　`jira issue create` (or `comment add`) timed out with exit status 124 | 137 | `user/troubleshooting/integrations` |
| `member/21-troubleshooting.md` | 　　`jira` exited with status 3: the description was not set | 88 | `user/troubleshooting/integrations` |
| `member/21-troubleshooting.md` | 　　AWS commands say "Unable to locate credentials", or `af-aws-exec` / `af-gcloud-exec` stops | 127 | `user/troubleshooting/integrations` |
| `member/21-troubleshooting.md` | 　Terminal and phone | 72 | `user/troubleshooting/terminal-phone` |
| `member/21-troubleshooting.md` | 　　Ctrl+C doesn't work in the terminal / I can't copy-paste | 104 | `user/troubleshooting/terminal-phone` |
| `member/21-troubleshooting.md` | 　　App shortcuts such as the command palette don't work | 104 | `user/troubleshooting/terminal-phone` |
| `member/21-troubleshooting.md` | 　　On a phone, the keyboard pops up on its own / it's hard to operate | 48 | `user/troubleshooting/terminal-phone` |
| `member/21-troubleshooting.md` | 　　Only the terminal stays dark on the light theme | 27 | `user/troubleshooting/terminal-phone` |
| `member/21-troubleshooting.md` | 　FAQ | 536 | `user/troubleshooting/faq` |
| `member/21-troubleshooting.md` | 　Reporting a bug or requesting a feature | 81 | `user/troubleshooting/report` |
| `member/README.md` | Using Agent Fleet | 68 | `user/start/overview` |
| `member/README.md` | 　Chapters | 31 | `user/start/overview` |
| `member/README.md` | 　　Getting started | 33 | `user/start/overview` |
| `member/README.md` | 　　Daily work | 76 | `user/start/overview` |
| `member/README.md` | 　　Going further | 131 | `user/start/overview` |
| `member/README.md` | 　　Reference | 88 | `user/start/overview` |
| `member/badges-and-menus.md` | Icons, badges, and menus — common Console reference | 18 | `ref/console-ui` |
| `member/badges-and-menus.md` | 　Session display | 974 | `ref/console-ui` |
| `member/badges-and-menus.md` | 　Repository status display | 283 | `ref/console-ui` |
| `member/badges-and-menus.md` | 　The engine pills in the top bar | 420 | `ref/console-ui` |
| `member/badges-and-menus.md` | 　Other badges | 524 | `ref/console-ui` |
| `member/badges-and-menus.md` | 　Right-click menus | 0 | `ref/console-ui` |
| `member/badges-and-menus.md` | 　　Sessions | 338 | `ref/console-ui` |
| `member/badges-and-menus.md` | 　　Repositories / worktrees | 148 | `ref/console-ui` |
| `member/badges-and-menus.md` | 　　Files / folders | 151 | `ref/console-ui` |
| `member/badges-and-menus.md` | 　　File and folder links in replies and documents | 115 | `ref/console-ui` |
| `member/badges-and-menus.md` | 　　Cards in the image gallery | 157 | `ref/console-ui` |
| `member/badges-and-menus.md` | 　　Assistants | 39 | `ref/console-ui` |
| `member/badges-and-menus.md` | 　　Commit graph | 39 | `ref/console-ui` |
| `member/badges-and-menus.md` | 　Buttons on a pane | 49 | `ref/console-ui` |
| `member/badges-and-menus.md` | 　　Tabs (tabbed grid) | 35 | `ref/console-ui` |
| `member/badges-and-menus.md` | 　　Cards in the sessions overview | 28 | `ref/console-ui` |
| `member/badges-and-menus.md` | 　When a menu doesn't appear | 92 | `user/troubleshooting/terminal-phone` |
| `member/lite.md` | Simple guide (for people who don't use the terminal) | 150 | `user/start/without-terminal` |
| `member/lite.md` | 　1. What you can do with Agent Fleet | 184 | `user/start/overview` |
| `member/lite.md` | 　2. Logging in and reading the screen | 207 | `user/start/console-tour` |
| `member/lite.md` | 　3. One-time setup | 299 | `user/start/quickstart` |
| `member/lite.md` | 　4. Using chat (questions, translation, text cleanup) | 210 | `user/chat/assistant` |
| `member/lite.md` | 　　How is chat different from a session? | 133 | `user/chat/assistant` |
| `member/lite.md` | 　5. Reading documents and slides | 206 | `user/files/view` |
| `member/lite.md` | 　6. The memo queue (collect ideas and hand them over) | 202 | `user/chat/memos` |
| `member/lite.md` | 　　"Who receives my memos?" | 96 | `user/chat/memos` |
| `member/lite.md` | 　7. Watching development progress | 211 | `user/sessions/status` |
| `member/lite.md` | 　　Reading work that was shared with you | 115 | `user/team/share` |
| `member/lite.md` | 　　An important ground rule | 76 | `user/start/without-terminal` |
| `member/lite.md` | 　8. When you're stuck + FAQ | 0 | `user/troubleshooting/faq` |
| `member/lite.md` | 　　First moves when something goes wrong | 80 | `user/troubleshooting/faq` |
| `member/lite.md` | 　　FAQ | 266 | `user/troubleshooting/faq` |
| `operate/01-choose.md` | 01. Choosing a deployment target | 48 | `operate/choose` |
| `operate/01-choose.md` | 　Start here | 248 | `operate/choose` |
| `operate/01-choose.md` | 　What ECS actually costs you | 208 | `operate/choose` |
| `operate/01-choose.md` | 　　Fargate starts are billed by the NAT | 223 | `operate/choose` |
| `operate/01-choose.md` | 　　Choosing the egress route on AWS | 263 | `operate/choose` |
| `operate/01-choose.md` | 　When Kubernetes, and when not | 189 | `operate/choose` |
| `operate/01-choose.md` | 　Where the procedure is | 131 | `operate/choose` |
| `operate/01-choose.md` | 　What you cannot change later without pain | 68 | `operate/choose` |
| `operate/02-install.md` | 02. Initial Setup | 69 | `operate/install` |
| `operate/02-install.md` | 　0. Check the prerequisites | 97 | `operate/install` |
| `operate/02-install.md` | 　1. Prepare the configuration file | 93 | `operate/install` |
| `operate/02-install.md` | 　2. Generate the secrets — put `AF_MASTER_KEY` in a vault at this point | 159 | `operate/install` |
| `operate/02-install.md` | 　3. Configure the login IdP | 564 | `operate/install` |
| `operate/02-install.md` | 　4. Decision points | 10 | `operate/install-decisions` |
| `operate/02-install.md` | 　　When to use `tls internal` | 94 | `operate/install-decisions` |
| `operate/02-install.md` | 　　`AF_PROVISION`: auto or invite | 292 | `operate/install-decisions` |
| `operate/02-install.md` | 　　Single tenant, or separate tenants | 500 | `operate/install-decisions` |
| `operate/02-install.md` | 　　A tenant with its own IdP | 717 | `operate/install-decisions` |
| `operate/02-install.md` | 　5. Start it up | 87 | `operate/install` |
| `operate/02-install.md` | 　6. First login and the first administrator | 105 | `operate/install` |
| `operate/02-install.md` | 　7. The first tenant and members | 429 | `operate/install` |
| `operate/03-run.md` | 03. Day-to-Day Operations | 73 | `operate/run/backup-restore` |
| `operate/03-run.md` | 　Backup | 29 | `operate/run/backup-restore` |
| `operate/03-run.md` | 　　What is included and what is not | 211 | `operate/run/backup-restore` |
| `operate/03-run.md` | 　　Impact on users | 70 | `operate/run/backup-restore` |
| `operate/03-run.md` | 　　Running it from cron | 55 | `operate/run/backup-restore` |
| `operate/03-run.md` | 　Restore | 217 | `operate/run/backup-restore` |
| `operate/03-run.md` | 　Upgrade | 533 | `operate/run/upgrade` |
| `operate/03-run.md` | 　Installing into an air-gapped network | 416 | `operate/run/air-gapped` |
| `operate/03-run.md` | 　Distributing fleet policy (instructions to every agent) | 349 | `operate/run/fleet-policy` |
| `operate/03-run.md` | 　opencode 2: Terminal sessions and the shared server | 120 | `operate/run/opencode-server` |
| `operate/03-run.md` | 　　When an opencode release misbehaves | 177 | `operate/run/opencode-server` |
| `operate/03-run.md` | 　Once it is on the public internet | 239 | `operate/run/public-internet` |
| `operate/03-run.md` | 　Telling two deployments apart (colour and label) | 434 | `operate/run/deployment-label` |
| `operate/03-run.md` | 　Idle stop and force-stop | 0 | `operate/run/idle-stop` |
| `operate/03-run.md` | 　　A start that never finishes | 197 | `operate/run/idle-stop` |
| `operate/03-run.md` | 　　Silent Agent detection | 600 | `operate/run/idle-stop` |
| `operate/03-run.md` | 　　Automatic idle stop (scale-to-zero) | 250 | `operate/run/idle-stop` |
| `operate/03-run.md` | 　　What keeps a Workspace awake | 318 | `operate/run/idle-stop` |
| `operate/03-run.md` | 　　Force-stop (brute force) | 66 | `operate/run/idle-stop` |
| `operate/03-run.md` | 　Pausing an idle deployment | 526 | `operate/run/idle-stop` |
| `operate/04-secure.md` | 04. Security Operations | 62 | `operate/secure/controls` |
| `operate/04-secure.md` | 　Threat model (summary) | 286 | `operate/secure/threat-model` |
| `operate/04-secure.md` | 　Residual risks: what to do about them | 339 | `operate/secure/threat-model` |
| `operate/04-secure.md` | 　Operating egress control | 1180 | `operate/secure/egress` |
| `operate/04-secure.md` | 　MCP servers and external connections | 275 | `operate/secure/mcp` |
| `operate/04-secure.md` | 　　Sign-in for remote MCP clients (OAuth) | 813 | `operate/secure/mcp` |
| `operate/04-secure.md` | 　　Trusted client hosts (deployment-wide — super_admin only) | 392 | `operate/secure/mcp` |
| `operate/04-secure.md` | 　　Sign-in for OAuth-protected MCP servers members register | 349 | `operate/secure/mcp` |
| `operate/04-secure.md` | 　　Reading what a client sent to `/mcp` | 278 | `operate/secure/mcp` |
| `operate/04-secure.md` | 　Handing over the in-workspace browser | 79 | `operate/secure/controls` |
| `operate/04-secure.md` | 　`AUTH=dev` is not a default | 86 | `operate/secure/dev-signin` |
| `operate/04-secure.md` | 　Development sign-in (dev OIDC IdP — super_admin only) | 213 | `operate/secure/dev-signin` |
| `operate/04-secure.md` | 　Other operational controls | 1119 | `operate/secure/controls` |
| `operate/04-secure.md` | 　Offboarding: how access is actually revoked | 539 | `operate/secure/offboarding` |
| `operate/04-secure.md` | 　　The emergency stop: rotating `AF_COOKIE_SECRET` | 136 | `operate/secure/offboarding` |
| `operate/04-secure.md` | 　Handing over `super_admin` | 199 | `operate/secure/offboarding` |
| `operate/04-secure.md` | 　Reporting vulnerabilities | 37 | `operate/secure/threat-model` |
| `operate/05-signin.md` | 05. Sign-in Methods — Setting Up an IdP End to End | 130 | `operate/signin/overview` |
| `operate/05-signin.md` | 　0. Before you start | 176 | `operate/signin/overview` |
| `operate/05-signin.md` | 　1. The one thing that is the same for every IdP: the redirect URI | 137 | `operate/signin/overview` |
| `operate/05-signin.md` | 　2. Where each setting lives | 410 | `operate/signin/overview` |
| `operate/05-signin.md` | 　3. Google | 0 | `operate/signin/google` |
| `operate/05-signin.md` | 　　3.1 What to create in Google Cloud Console | 112 | `operate/signin/google` |
| `operate/05-signin.md` | 　　3.2 The values, and where they go | 75 | `operate/signin/google` |
| `operate/05-signin.md` | 　　3.3 Common failures | 129 | `operate/signin/google` |
| `operate/05-signin.md` | 　4. Microsoft Entra ID | 0 | `operate/signin/entra` |
| `operate/05-signin.md` | 　　4.1 What to create in the Entra admin center | 205 | `operate/signin/entra` |
| `operate/05-signin.md` | 　　4.2 The values, and where they go | 333 | `operate/signin/entra` |
| `operate/05-signin.md` | 　　4.3 One directory behind two app registrations | 113 | `operate/signin/entra` |
| `operate/05-signin.md` | 　　4.4 Common failures | 170 | `operate/signin/entra` |
| `operate/05-signin.md` | 　5. GitHub | 36 | `operate/signin/github` |
| `operate/05-signin.md` | 　　5.1 What to create on GitHub | 185 | `operate/signin/github` |
| `operate/05-signin.md` | 　　5.2 The values, and where they go | 190 | `operate/signin/github` |
| `operate/05-signin.md` | 　　5.3 Two behaviours worth knowing in advance | 187 | `operate/signin/github` |
| `operate/05-signin.md` | 　　5.4 Common failures | 104 | `operate/signin/github` |
| `operate/05-signin.md` | 　6. Okta, Keycloak, Auth0, Cognito, GitLab, and other OIDC IdPs | 274 | `operate/signin/oidc` |
| `operate/05-signin.md` | 　7. A sign-in method a tenant defines itself | 178 | `operate/signin/tenant-idp` |
| `operate/05-signin.md` | 　　7.1 What the tenant administrator fills in | 387 | `operate/signin/tenant-idp` |
| `operate/05-signin.md` | 　　7.2 What you check before approving | 400 | `operate/signin/tenant-idp` |
| `operate/05-signin.md` | 　　7.3 When the tenant uses a GitHub organization | 192 | `operate/signin/tenant-idp` |
| `operate/05-signin.md` | 　8. Check that it worked | 459 | `operate/signin/overview` |
| `operate/05-signin.md` | 　9. When it still does not work | 96 | `operate/diagnose/cannot-login` |
| `operate/06-diagnose.md` | 06. Troubleshooting and FAQ | 62 | `operate/diagnose/checklist` |
| `operate/06-diagnose.md` | 　The first 3 places to look | 128 | `operate/diagnose/checklist` |
| `operate/06-diagnose.md` | 　Symptom-based checklist | 881 | `operate/diagnose/checklist` |
| `operate/06-diagnose.md` | 　Diagnosing the 3 DooD constraints ("starts but silently doesn't work") | 240 | `operate/diagnose/checklist` |
| `operate/06-diagnose.md` | 　Cannot log in | 626 | `operate/diagnose/cannot-login` |
| `operate/06-diagnose.md` | 　TLS is not issued | 61 | `operate/diagnose/checklist` |
| `operate/06-diagnose.md` | 　Triage flow for user inquiries | 212 | `operate/diagnose/checklist` |
| `operate/06-diagnose.md` | 　FAQ (edge cases and common questions) | 469 | `operate/diagnose/checklist` |
| `operate/07-engines.md` | 07. Inference engines and read aloud: the Admin panel | 84 | `operate/engines/gpu` |
| `operate/07-engines.md` | 　Inference engines (self-hosted GPUs — super_admin only) | 446 | `operate/engines/gpu` |
| `operate/07-engines.md` | 　　The GPU instance class | 583 | `operate/engines/gpu` |
| `operate/07-engines.md` | 　　The warning about whether a model fits | 121 | `operate/engines/gpu` |
| `operate/07-engines.md` | 　　Taking models in, and what that has to do with tenants | 1904 | `operate/engines/models` |
| `operate/07-engines.md` | 　　Reading the current state | 276 | `operate/engines/status` |
| `operate/07-engines.md` | 　　History (14 days) | 220 | `operate/engines/status` |
| `operate/07-engines.md` | 　Read aloud (the speech engine and the shared dictionary) | 242 | `operate/engines/read-aloud` |
| `operate/07-engines.md` | 　What a picture keeps out | 303 | `operate/engines/gpu` |
| `operate/08-image-engine.md` | 08. Image generation on your own ComfyUI | 317 | `operate/engines/comfyui` |
| `operate/08-image-engine.md` | 　Running the fleet's image on your GPU host | 591 | `operate/engines/comfyui` |
| `operate/08-image-engine.md` | 　Pointing the Control Plane at it | 550 | `operate/engines/comfyui` |
| `operate/08-image-engine.md` | 　More than one image engine | 414 | `operate/engines/comfyui` |
| `operate/08-image-engine.md` | 　What the modes mean here | 138 | `operate/engines/comfyui` |
| `operate/08-image-engine.md` | 　Registering the models by hand | 637 | `operate/engines/comfyui` |
| `operate/08-image-engine.md` | 　The network is yours to close | 250 | `operate/engines/comfyui` |
| `operate/08-image-engine.md` | 　When it is down | 106 | `operate/engines/comfyui` |
| `operate/08-image-engine.md` | 　What the panel will and will not show you | 104 | `operate/engines/comfyui` |
| `operate/09-borrowed-engine.md` | 09. Borrowing another deployment's engines | 320 | `operate/engines/borrow` |
| `operate/09-borrowed-engine.md` | 　The two variables, and the optional third | 202 | `operate/engines/borrow` |
| `operate/09-borrowed-engine.md` | 　　The rows appear when the far fleet answers, not at boot | 233 | `operate/engines/borrow` |
| `operate/09-borrowed-engine.md` | 　The credential | 423 | `operate/engines/borrow` |
| `operate/09-borrowed-engine.md` | 　What the far catalogue decides, and what you cannot change here | 207 | `operate/engines/borrow` |
| `operate/09-borrowed-engine.md` | 　　When the far side switches a role off | 96 | `operate/engines/borrow` |
| `operate/09-borrowed-engine.md` | 　What the first request waits for | 345 | `operate/engines/borrow` |
| `operate/09-borrowed-engine.md` | 　What the panel will and will not show you | 159 | `operate/engines/borrow` |
| `operate/09-borrowed-engine.md` | 　Who pays, and what is recorded | 185 | `operate/engines/borrow` |
| `operate/09-borrowed-engine.md` | 　　If you are the one being borrowed from | 275 | `operate/engines/borrow` |
| `operate/09-borrowed-engine.md` | 　When it does not work | 350 | `operate/engines/borrow` |
| `operate/10-llm-lan.md` | 10. Chat inference on your own llama.cpp | 152 | `operate/engines/llama-cpp` |
| `operate/10-llm-lan.md` | 　Two paths: the shortcut and the table | 221 | `operate/engines/llama-cpp` |
| `operate/10-llm-lan.md` | 　　Why not `AF_LLM_API_KEY` | 76 | `operate/engines/llama-cpp` |
| `operate/10-llm-lan.md` | 　Running llama-server on the LAN box | 426 | `operate/engines/llama-cpp` |
| `operate/10-llm-lan.md` | 　Switch first, then register the models | 117 | `operate/engines/llama-cpp` |
| `operate/10-llm-lan.md` | 　What you lose (said plainly) | 101 | `operate/engines/llama-cpp` |
| `operate/10-llm-lan.md` | 　What stays the same | 47 | `operate/engines/llama-cpp` |
| `operate/10-llm-lan.md` | 　What it looks like when it is down | 55 | `operate/engines/llama-cpp` |
| `operate/10-llm-lan.md` | 　What the panel will and will not show you | 92 | `operate/engines/llama-cpp` |
| `operate/10-llm-lan.md` | 　A member's own connection | 317 | `operate/engines/llama-cpp` |
| `operate/11-slot-pool.md` | 11. The ecs-ec2 slot pool | 42 | `operate/ecs-ec2-slots` |
| `operate/11-slot-pool.md` | 　ecs-ec2: replacing outdated slots (new AMI or launch template change) | 582 | `operate/ecs-ec2-slots` |
| `operate/11-slot-pool.md` | 　ecs-ec2: memory protection for the management plane | 188 | `operate/ecs-ec2-slots` |
| `operate/11-slot-pool.md` | 　ecs-ec2: stopping a wedged slot | 694 | `operate/ecs-ec2-slots` |
| `operate/12-keys.md` | 12. Keys at rest: AWS KMS and a key for each home | 76 | `operate/keys/kms` |
| `operate/12-keys.md` | 　Keys at rest on AWS KMS | 481 | `operate/keys/kms` |
| `operate/12-keys.md` | 　Re-sealing values stored before the switch | 670 | `operate/keys/kms` |
| `operate/12-keys.md` | 　A key of its own for each home | 74 | `operate/keys/home-keys` |
| `operate/12-keys.md` | 　　Before you turn it on on ECS | 187 | `operate/keys/home-keys` |
| `operate/12-keys.md` | 　　How the home's key behaves | 723 | `operate/keys/home-keys` |
| `operate/12-keys.md` | 　　Disabling the KMS key, restoring a copy, turning it off | 645 | `operate/keys/home-keys` |
| `operate/12-keys.md` | 　Rotating the bridge tokens | 265 | `operate/keys/bridge-tokens` |
| `operate/README.md` | Operating a deployment | 45 | `operate/overview` |
| `operate/README.md` | 　Chapters | 288 | `operate/overview` |
| `operate/README.md` | 　Where the commands are | 130 | `operate/overview` |
| `operate/README.md` | 　For those considering adoption | 312 | `operate/overview` |
| `operate/README.md` | 　The minimal model you must hold in your head | 197 | `operate/overview` |
| `operate/README.md` | 　Responsibility checklist | 163 | `operate/overview` |
| `ref/README.md` | Reference — what Agent Fleet can do | 156 | `ref/overview` |
| `ref/README.md` | 　How to read these tables | 63 | `ref/overview` |
| `ref/agents.md` | Agents — what each kind can do | 1270 | `ref/agents` |
| `ref/agents.md` | 　How to sign in | 371 | `ref/agents` |
| `ref/agents.md` | 　States shown in the mirror | 366 | `ref/agents` |
| `ref/agents.md` | 　Stopping a turn, and messages sent while one runs | 689 | `ref/agents` |
| `ref/agents.md` | 　Moving a session to another agent | 220 | `ref/agents` |
| `ref/agents.md` | 　Each agent's own memory | 124 | `ref/agents` |
| `ref/agents.md` | 　claude: the "API key" route | 954 | `ref/agents` |
| `ref/agents.md` | 　Choosing one | 169 | `ref/agents` |
| `ref/agents.md` | 　lcpp: what hardware measurement found | 321 | `ref/agents` |
| `ref/agents.md` | 　muse: what Agent Fleet does not see | 362 | `ref/agents` |
| `ref/agents.md` | 　Not in this table | 1728 | `ref/agents` |
| `ref/browser-pane.md` | Browser pane — the usage contract | 30 | `ref/browser-pane` |
| `ref/browser-pane.md` | 　The two routes | 194 | `ref/browser-pane` |
| `ref/browser-pane.md` | 　Which route, by example | 52 | `ref/browser-pane` |
| `ref/browser-pane.md` | 　States and recovery | 57 | `ref/browser-pane` |
| `ref/browser-pane.md` | 　Lifecycle and resource limits | 151 | `ref/browser-pane` |
| `ref/browser-pane.md` | 　Scope and known limits | 147 | `ref/browser-pane` |
| `ref/browser-pane.md` | 　Where there is no browser pane | 258 | `ref/browser-pane` |
| `ref/browser-pane.md` | 　For agents working inside a Workspace | 103 | `ref/browser-pane` |
| `ref/deploy-targets.md` | Deployment targets — what exists where | 580 | `ref/deploy-targets` |
| `ref/deploy-targets.md` | 　Capability differences | 1481 | `ref/deploy-targets` |
| `ref/deploy-targets.md` | 　Where the procedure lives | 98 | `ref/deploy-targets` |
| `ref/deploy-targets.md` | 　What is the same everywhere | 50 | `ref/deploy-targets` |
| `ref/features.md` | Features — the catalogue | 52 | `ref/features` |
| `ref/features.md` | 　Working with a session | 649 | `ref/features` |
| `ref/features.md` | 　Working with code | 640 | `ref/features` |
| `ref/features.md` | 　Organising the work | 438 | `ref/features` |
| `ref/features.md` | 　Personal settings | 428 | `ref/features` |
| `ref/features.md` | 　Tenant administration | 389 | `ref/features` |
| `ref/features.md` | 　Operating a deployment | 564 | `ref/features` |
| `ref/glossary.md` | Glossary | 1828 | `ref/glossary` |
| `ref/limits.md` | Limits and defaults | 47 | `ref/limits` |
| `ref/limits.md` | 　Fixed in the product | 744 | `ref/limits` |
| `ref/limits.md` | 　Set by the deployment | 498 | `ref/limits` |
| `ref/limits.md` | 　Set per tenant | 146 | `ref/limits` |
| `ref/limits.md` | 　The limit board: what it collects and how it reads | 360 | `ref/limits` |
| `ref/repos.md` | Repository providers — what each supports | 689 | `ref/repos` |
| `ref/repos.md` | 　Issue trackers are a separate axis | 100 | `ref/repos` |
| `ref/repos.md` | 　Not in this table | 23 | `ref/repos` |
| `ref/roles.md` | Roles — who may do what | 112 | `ref/roles` |
| `ref/roles.md` | 　What each may do | 529 | `ref/roles` |
| `ref/roles.md` | 　Where a tenant administrator has to ask | 75 | `ref/roles` |
| `ref/roles.md` | 　Which documentation each role receives | 58 | `ref/roles` |
| `ref/settings.md` | Settings — where things are configured | 130 | `ref/settings` |
| `ref/settings.md` | 　Personal settings | 573 | `ref/settings` |
| `ref/settings.md` | 　Tenant settings | 407 | `ref/settings` |
| `ref/settings.md` | 　Admin modal | 262 | `ref/settings` |
| `ref/settings.md` | 　Deployment variables | 587 | `ref/settings` |
| `ref/settings.md` | 　　On AWS ECS | 194 | `ref/settings` |
<!-- /generated:sections -->
