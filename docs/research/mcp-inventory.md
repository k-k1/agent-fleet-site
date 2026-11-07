# Agent Fleet MCP tool inventory (raw material)

Total: 81 distinct tool names (70 on the Workspace Agent's local servers, 41 on the Control Plane's /mcp, 30 shared by both; 11 are CP-only).
Source tree: /home/dev/repos/agent-fleet@wip-svtrqfp (paths below are relative to it).
Ground truth for "who sees what": the golden files
`workspace/agent/internal/mcpx/testdata/mcp_tools/list.json` and `control-plane/internal/mcpsrv/testdata/mcp_tools/list.json`.

## 1. Servers and routes

Route codes used in the tables:

| Code | Server / route | Who connects | Tool list built at |
|---|---|---|---|
| S | Session-side "af" server: `workspace-agent mcp-stdio --self-report ...` (stdio child of each session's CLI, all agent kinds). Always carries the base set; each extra family is added by a flag. | the agent inside a session | `workspace/agent/internal/mcpx/mcp_tool_list.go:15-40` (`mcpStdioToolList`, `selfReportOnly()` branch); flags parsed in `mcp_stdio.go:113-169` |
| A-R | Assistant server, read-only: `mcp-stdio` (no flag) | the Console's chat Assistant, af tools set to read ("af_read") | `mcp_tool_list.go:41-47` -> `operatorTools(false)` in `mcp_toolspec.go:127-142` |
| A-W | Assistant server, write: `mcp-stdio --write --conv <id>` ("af_write"); a superset of A-R | the Console's chat Assistant with write grant | same, `operatorTools(true)`; argv built in `workspace/agent/internal/chatx/chat_mcp.go:52-65` |
| CP | Control Plane hosted `/mcp` (Streamable HTTP, Bearer PAT or OAuth; enabled by `AF_MCP_ENABLED`) | hosted assistants / PAT or OAuth clients (claude.ai, ChatGPT, Claude Code on another machine) | `control-plane/internal/mcpsrv/mcp.go:901-908` (`mcpToolList`) from `toolsFor` `mcp.go:869-899`; member tools `mcp.go:452` (`memberTools`), admin tools `adminTools` (`mcp.go:~1140`), memory tools `mcp_memory.go:69` |
| CPM | Control Plane `/mcp/memory` (memory-only endpoint, memory tools and nothing else; accepts only tokens bound to it) | claude.ai-style external connector for memory | `mcp.go:56-61` (`MemoryOnly`), `toolsFor` returns after memory tools; routing `control-plane/mcp_oauth.go:131` |

Which tools the CP lists depends on the PAT's scope tier (read < write < admin:dangerous; per-tool `minScope`) and, for admin tools, the live role (super_admin / tenant_admin; a plain member never sees them). The CP list is per-principal ("cacheScope: private").

### How the Session (S) set is decided
`mcpStdioToolList()` (`mcp_tool_list.go:15`) starts with the base set, then appends families by flag. The flags come from the argv that `mcpreg/builtin.go:builtinRunArgsFor` (`workspace/agent/internal/mcpreg/builtin.go:~176-197`) writes from user settings (ui-prefs, `workspace/agent/internal/uiprefs/prefs.go:217-270`). A flag only counts when `--self-report` is also present (`mcp_stdio.go:161-168`), so it can never widen the assistant.

| Family | Argv flag | ui-prefs key (default) | Extra condition |
|---|---|---|---|
| base (handoff, report, stop-after-turn, status, usage, memos, branch_name, link_work_item) | `--self-report` | always | — |
| Chromium | `--chromium-attach` (always passed for "af") | always | removed on both surfaces when the workspace has no browser (`--browser-unavailable <runtime>`; Kubernetes/ECS) (`mcp_tool_list.go:18`, `mcp_stdio.go:~101-110`) |
| peer messaging | `--peer-messaging` | `peerMessaging` (OFF) | — |
| session search | `--session-search` | `sessionSearch` (ON) | Agent re-checks the switch on every call |
| agent memory | `--agent-memory` | `agentMemory` (OFF) | memory routes also refuse when off (`memoryx/agent_memory_handlers.go:67-76`) |
| fleet spawn (child sessions) | `--fleet-spawn` | `sessionFleetSpawn` (OFF) | calls that target a session only allowed on the caller's own children (`sessionDriveAllowed`, `mcp_fleet_spawn.go:~50`) |
| image generation | `--image-gen` | `imageGeneration` (OFF) | also needs a ready provider (loopback `/imagegen/status`), a non-studio session, and the session's own CLI is excluded from providers (`mcp_imagegen.go:750-`) |
| image studio | none | none | only a session bound to an image studio (or one whose identity can't be told apart in a folder where a studio session exists) (`mcp_studio.go:99`) |

The advertised set is also the call-side scope boundary: a call to a name not in the last tools/list is refused (`mcp_tool_list.go:~160`), and most specs also have a `refuse` gate.
The tool list is re-derived every minute and a `notifications/tools/list_changed` is sent when it changes (`mcp_tool_list.go:130-150`).

Assistant (A-R / A-W): read-only tools (`spec.operator` with `operatorWrite=false`) for A-R; `operatorWrite=true` ones only under `--write`. The Chromium five mutating tools are write-only; the Chromium read pair is in A-R. No browser: all Chromium tools are removed (`mcp_tool_list.go:41-46`).

Not listed here: other builtin servers (`mcp-run pagerduty|grafana|cloudwatch|aws`, `workspace/agent/internal/mcpreg/builtin.go`) proxy third-party MCP servers and are not Agent Fleet's own tools. `workspace/agent/internal/mcpc/mcpc.go` is an MCP client, not a server.

Surface sizes (golden): S base 10; S with every flag 37 (+4 studio, session-bound only); A-R 15 (13 without a browser); A-W 49 (42 without a browser); CP member 10/25 tools (read / write+) + 6 memory (4 read, 2 write) + 10 admin.

Notes on descriptions: S descriptions are English (cost), A and CP descriptions are Japanese/English respectively; the same name can have different text and slightly different parameters per route (e.g. `create_session`, `add_memo`, `update_memo`, `get_session_status`).

## 2. Tables by functional group

"Gate" column: setting key = ui-prefs; "write" = A-W only. Source = file:line of the spec's `name:` (mcpx files are under `workspace/agent/internal/mcpx/`; CP files under `control-plane/internal/mcpsrv/`, written `cp/mcp.go`).

### 2.1 Completion and stop (session-only)

| Tool | Routes | Gate | Purpose (JA) | Key parameters | Source |
|---|---|---|---|---|---|
| af_report | S | — (refuses outside S) | 渡された指示が完全に終わったことを一度だけ報告する（`[agent-fleet]` 付きの指示向け） | session | mcp_self_report.go:175 |
| af_stop_after_turn | S | — (user must have asked the session to stop when done) | このターンの終わりに自分自身を停止するよう予約する／解除する | session, on | mcp_self_report.go:228 |
| propose_session_handoff | S | — | 続きの作業用の新しいセッションの最初のプロンプトを利用者に提案する（自分では何も起動しない） | title, prompt | mcp_self_report.go:120 |

### 2.2 Sessions: observe (read)

| Tool | Routes | Gate | Purpose (JA) | Key parameters | Source |
|---|---|---|---|---|---|
| list_my_sessions | A-R, A-W, CP | — | ワークスペースのセッション一覧（名前・種別・状態・作業ディレクトリ）を返す | — | mcp_fleet_observe.go:231; cp/mcp.go:460 (read) |
| get_session_status | S, A-R, A-W, CP | — | セッションの今の状態（作業中・待機中・質問中・プラン待ち）と保留中の質問を返す | name | mcp_fleet_observe.go:246; cp/mcp.go:468 (read) |
| get_session_output | A-R, A-W, CP; S only with fleet spawn | S: `sessionFleetSpawn`, only own children | セッションの最近の端末出力を読む（前回の続きから） | name, since | mcp_fleet_observe.go:299; cp/mcp.go:476 (read) |
| get_session_usage | S, A-R, A-W, CP | — | セッションごとのコンテキスト使用量と累積トークン消費を返す | name | mcp_fleet_observe.go:374; cp/mcp.go:645 (read) |
| get_agent_usage | A-R, A-W, CP; S only with fleet spawn | S: `sessionFleetSpawn` | 各エージェントCLIのサブスクリプション使用量とレート制限を返す | — | mcp_fleet_observe.go:416; cp/mcp.go:659 (read) |
| search_sessions | S | `sessionSearch` (default ON) | 過去のセッション（停止・アーカイブ含む全エージェント）の会話を全文検索する | query, session, idx, kind, repo, limit | mcp_session_search.go:106 (schema :24) |

### 2.3 Sessions and child sessions: start and drive

| Tool | Routes | Gate | Purpose (JA) | Key parameters | Source |
|---|---|---|---|---|---|
| create_session | S, A-W, CP | S: `sessionFleetSpawn` (max N children at once, no grandchildren, no shell); A-W: write; CP: write scope | 新しいセッションを起動して最初の作業を渡す（子セッションの起動） | S: kind, model, effort, dir, subdir, worktree, branch, new_branch, title, initial_prompt, route, route_connection, report_back, spend_cap_usd, work_item, allow_shared_working_copy; A-W/CP: similar minus S-only fields (A-W also effort, report-related via conv) | mcp_fleet_spawn.go:211; cp/mcp.go:705 |
| list_child_sessions | S | `sessionFleetSpawn` | 自分が起動した子セッションの一覧（状態・残り枠）を返す | — | mcp_fleet_spawn.go:457 |
| rename_child_session | S | `sessionFleetSpawn`; refused once the user renamed it | 自分が起動した子セッションのタイトルを付け直す | name, title | mcp_fleet_spawn.go:492 |
| list_repos | S, A-R, A-W, CP | S: `sessionFleetSpawn` | ワークスペース内のgit作業コピー（~/repos）の一覧を返す | — | mcp_fleet_observe.go:473; cp/mcp.go:682 (read) |
| list_models | S, A-W, CP | S: `sessionFleetSpawn`; A-W: write | エージェント種別ごとに今選べるモデルの一覧を返す | kind | mcp_fleet_spawn.go:158; cp/mcp.go:690 (read) |
| send_to_session | A-W, CP | write | 指定セッションにプロンプトを送って実行させる（停止中なら再開してから） | name, prompt | mcp_drive.go:46; cp/mcp.go:498 (write) |
| answer_session_question | A-W | write | セッションが出している質問に選択肢で答える | name, choices | mcp_drive.go:102 |
| respond_session_plan | A-W | write | セッションが承認待ちのプランを承認／却下する（claudeのみ） | name, decision, feedback | mcp_drive.go:140 |
| stop_session | S (own children), A-W, CP | S: `sessionFleetSpawn`; write | セッションを停止する（会話と作業コピーは残り再開できる） | name | mcp_drive.go:179; cp/mcp.go:519 (write) |
| stop_session_after_turn | S (own children), A-W, CP | S: `sessionFleetSpawn`; write | 今のターンが終わったら止まるよう予約する（中断しない） | name, on | mcp_drive.go:246; cp/mcp.go:530 (write) |
| resume_session | S (own children), A-W, CP | S: `sessionFleetSpawn`; write | 停止中のセッションを会話を保ったまま再開する | name | mcp_drive.go:313; cp/mcp.go:551 (write) |

### 2.4 Peer messaging (session-only)

| Tool | Routes | Gate | Purpose (JA) | Key parameters | Source |
|---|---|---|---|---|---|
| list_peer_sessions | S | `peerMessaging` (default OFF) | 同じワークスペースの他のセッション一覧を返す（自分は除く） | — | mcp_peer.go:78 |
| send_to_peer_session | S | `peerMessaging` | 他のセッションに短いメッセージを送る（停止中なら再開して届く） | name, intent, message | mcp_peer.go:115 |
| peek_session_output | S | `peerMessaging` | 他のセッションの最近の出力を読み取り専用で見る | name, lines, since | mcp_peer.go:222 |

### 2.5 Memos (the user's memo queue)

| Tool | Routes | Gate | Purpose (JA) | Key parameters | Source |
|---|---|---|---|---|---|
| list_memos | S, A-R, A-W, CP | — | 利用者のメモキューの一覧を返す | — | mcp_memos.go:16; cp/mcp.go:767 (read) |
| add_memo | S, A-W, CP | write for A-W / CP (S always allowed: `memoWriteAllowed`) | 利用者のメモキューにメモを1件追加する | kind, body, refPath, repo, category | mcp_memos.go:44; cp/mcp.go:779 |
| update_memo | S, A-W, CP | same as add_memo | 既存のメモを編集する（渡した項目だけ変わる） | id, body, refPath, repo, category, (position: A-W/CP only) | mcp_memos.go:107; cp/mcp.go:803 |
| delete_memo | A-W, CP | write | メモをidで削除する | id | mcp_memos.go:170; cp/mcp.go:829 |
| flush_memos | A-W, CP | write | 選んだメモを1通にまとめてセッションへ送る | sessionName, ids | mcp_memos.go:201; cp/mcp.go:840 |

### 2.6 Schedules (assistant-only; no CP route)

| Tool | Routes | Gate | Purpose (JA) | Key parameters | Source |
|---|---|---|---|---|---|
| list_schedules | A-R, A-W | — | 定時実行スケジュールの一覧を返す | — | mcp_schedules.go:14 |
| get_schedule_runs | A-R, A-W | — | スケジュールの実行履歴（最新50件）を返す | id | mcp_schedules.go:31 |
| create_schedule | A-W | write | 定時実行スケジュールを登録する | spec_kind, spec, prompt, tz, repo, agent_kind, model, session_mode, report, ... | mcp_schedules.go:55 |
| update_schedule | A-W | write | 既存のスケジュールを編集する | id, spec, spec_kind, tz, prompt, ... | mcp_schedules.go:115 |
| delete_schedule | A-W | write | スケジュールを削除する | id | mcp_schedules.go:169 |
| pause_schedule | A-W | write | スケジュールを一時停止する | id | mcp_schedules.go:199 |
| resume_schedule | A-W | write | 一時停止したスケジュールを再開する | id | mcp_schedules.go:210 |
| run_schedule_now | A-W | write | スケジュールを今すぐ発火させる（動作確認用） | id | mcp_schedules.go:221 |

### 2.7 Cleanup (sessions, worktrees, branches)

| Tool | Routes | Gate | Purpose (JA) | Key parameters | Source |
|---|---|---|---|---|---|
| list_cleanup_candidates | A-R, A-W, CP | — | 溜まったセッション・worktreeの掃除候補を点検して返す | — | mcp_fleet_observe.go:344; cp/mcp.go:559 (read) |
| list_cleanup_archives | A-R, A-W, CP | — | 掃除で退避したアーカイブの一覧を返す | — | mcp_fleet_observe.go:359; cp/mcp.go:617 (read) |
| archive_session | A-W, CP | write | 終わったセッションをアーカイブして一覧から隠す（復元可） | name | mcp_drive.go:364; cp/mcp.go:567 |
| delete_worktree | A-W, CP | write | 不要なworktreeを削除する（未コミット／未pushがあると拒否） | name | mcp_drive.go:397; cp/mcp.go:575 |
| delete_session | A-W, CP | write | セッションを完全に削除して容量を回収する（退避アーカイブから復元可） | name | mcp_drive.go:438; cp/mcp.go:591 |
| delete_branch | A-W, CP | write | マージ済みのローカルブランチを削除する | repo, branch | mcp_drive.go:477; cp/mcp.go:605 |
| restore_cleanup_archive | A-W, CP | write | 退避したアーカイブからセッション／ブランチを復元する | id | mcp_drive.go:515; cp/mcp.go:625 |
| purge_cleanup_archive | A-W, CP | write | アーカイブを完全削除する（復元不可） | id | mcp_drive.go:548; cp/mcp.go:635 |

### 2.8 Agent memory (AF memory shared by all agent kinds)

Two different implementations: the session-side tools (S) use the workspace's own memory and are gated by the "agent memory" switch; the CP tools are for agents outside Agent Fleet.

| Tool | Routes | Gate | Purpose (JA) | Key parameters | Source |
|---|---|---|---|---|---|
| memory_index | S; CP, CPM | S: `agentMemory` (default OFF; `--agent-memory`). CP/CPM: tenant switch for external memory (`GetTenantExternalMemory`, `cp/mcp.go:874`) and the member's `externalMemory` setting (off/read/write, enforced on the Agent) | 共有メモリ（全エージェント共通）の一覧を返す（本文なし） | S: budget; CP: budget, project, repository | mcp_memory.go:329; cp/mcp_memory.go:89 |
| memory_search | S; CP, CPM | same | 共有メモリを全文検索する | query, limit (CP also project, repository) | mcp_memory.go:340; cp/mcp_memory.go:106 |
| memory_read | S; CP, CPM | same | 共有メモリを1件、本文付きで読む | name, scope (CP also project, repository) | mcp_memory.go:354; cp/mcp_memory.go:124 |
| memory_save | S; CP, CPM | same; CP: write scope | 共有メモリを新規作成／更新する（即公開。秘密情報は拒否） | name, description, body, scope, revision, type, kinds (CP also project, repository) | mcp_memory.go:368; cp/mcp_memory.go:138 |
| memory_forget | S; CP, CPM | same; CP: write scope | 共有メモリを公開から外す（履歴は残る） | name, revision, scope (CP also project, repository) | mcp_memory.go:390; cp/mcp_memory.go:163 |
| memory_projects | CP, CPM | tenant external-memory switch | メモリのプロジェクト一覧（id・リポジトリ・件数）を返す | — | cp/mcp_memory.go:81 |

Memory snapshots (the agents' own auto-memory history: claude auto-memory / codex memories):

| Tool | Routes | Gate | Purpose (JA) | Key parameters | Source |
|---|---|---|---|---|---|
| list_memory_snapshots | A-R, A-W | — | エージェントメモリの変更履歴（スナップショット）を新しい順に返す | limit | mcp_memory_snapshots.go:35 |
| get_memory_snapshot | A-R, A-W | — | 指定時点のエージェントメモリの中身と差分を返す | rev, at, path | mcp_memory_snapshots.go:66 |
| restore_memory_snapshot | A-W | write | エージェントメモリを指定時点に戻す（範囲の明示が必須） | rev, at, all, projects, kinds | mcp_memory_snapshots.go:123 |

### 2.9 Browser (Chromium hand-off)

Gate for the whole group: removed from every surface when the workspace has no browser (`--browser-unavailable`, `$AF_BROWSER_UNAVAILABLE`; a call answers `browser_unavailable`). S: always offered otherwise (`--chromium-attach`). Mutating five: S, or A-W; not A-R (`mcp_chromium.go:607-612`, `mcpChromiumWriteEnabled`).

| Tool | Routes | Gate | Purpose (JA) | Key parameters | Source |
|---|---|---|---|---|---|
| list_chromium_targets | S, A-R, A-W | browser available | ループバックのChromiumデバッグポートにあるページ一覧を返す | port | mcp_chromium.go:615 |
| get_chromium_attachment | S, A-R, A-W | browser available | Chromium接続の状態・操作モード・結果を確認する | attachment_id | mcp_chromium.go:621 |
| attach_chromium | S, A-W | browser available | 既存のページに表示・入力の経路をつないで利用者に見せる | port, target_id, expected_browser_id, label | mcp_chromium.go:627 |
| detach_chromium | S, A-W | browser available | Chromiumとの接続だけを切る（ページやブラウザは閉じない） | attachment_id | mcp_chromium.go:633 |
| request_browser_action | S, A-W | browser available | 利用者に操作を引き渡す指示（ログイン等）を作る／更新する | attachment_id, message, control_mode, completion_label, allow_cancel | mcp_chromium.go:639 |
| get_browser_action_result | S, A-W | browser available | 利用者が自己申告した操作の結果（完了・取消・保留）を確認する | attachment_id | mcp_chromium.go:645 |
| set_chromium_control_mode | S, A-W | browser available | 接続の入力モード（閲覧のみ／利用者操作／ロック）を切り替える | attachment_id, control_mode | mcp_chromium.go:651 |

### 2.10 Images

| Tool | Routes | Gate | Purpose (JA) | Key parameters | Source |
|---|---|---|---|---|---|
| generate_image | S | `imageGeneration` (default OFF; `--image-gen`); at least one provider ready; not a studio-bound session; session's own CLI is not offered as a provider; schema (model enum, ops, aspect ratios, loras) is built from the live offer and the list re-checked every minute | プロンプトから画像を生成して、生成ファイルのパスを返す（利用者のプラン枠を消費） | prompt, op, provider, size, aspect_ratio, background, count, inputs, mask, model, loras, seed, negative_prompt, strength, params (actual set depends on the offer) | mcp_imagegen.go:885 (schema :603) |
| get_image_studio | S | session bound to an image studio | 利用者と一緒に作業中のスタジオのドラフトを読む | — | mcp_studio.go:349 |
| set_image_draft | S | image studio session | スタジオのドラフトの項目を変更する | op, prompt, negativePrompt, size, strength, inputs, loras, params, suggest_model, clear | mcp_studio.go:358 |
| add_image_knowledge | S | image studio session | スタジオのモデル／系統の知識メモに1行追記する（利用者が頼んだ時だけ） | scope, key, note, evidence | mcp_studio.go:405 |
| run_image_trial | S | image studio session; call is refused unless the studio allows agent trials | ドラフトのまま試し画像を1枚作る | — | mcp_studio.go:424 |

### 2.11 Usage and models
(see also 2.2 `get_session_usage`, `get_agent_usage`, and 2.3 `list_models`)

| Tool | Routes | Gate | Purpose (JA) | Key parameters | Source |
|---|---|---|---|---|---|
| get_session_usage | S, A-R, A-W, CP | — | セッションのコンテキスト使用量と累積トークン消費 | name | mcp_fleet_observe.go:374; cp/mcp.go:645 |
| get_agent_usage | A-R, A-W, CP; S with `sessionFleetSpawn` | see 2.2 | エージェントCLIのサブスクリプション使用量・レート制限 | — | mcp_fleet_observe.go:416; cp/mcp.go:659 |
| list_models | S (spawn), A-W, CP | see 2.3 | 指定エージェントで選べるモデルの一覧 | kind | mcp_fleet_spawn.go:158; cp/mcp.go:690 |

### 2.12 Repos, branches and work items

| Tool | Routes | Gate | Purpose (JA) | Key parameters | Source |
|---|---|---|---|---|---|
| branch_name | S | — | 利用者のブランチ命名規則に沿ったブランチ名とベースを決めて返す（ブランチを作る／改名する前に呼ぶ） | repo, session, kind, slug, item | mcp_branch.go:161 (schema :127) |
| link_work_item | S | — (links the calling session only) | 自分のセッションをIssue・チケット・PRに紐づける（Consoleの行と項目に表示） | provider, key, role, title, url, remove | mcp_branch.go:166 (schema mcp_work_links.go:81) |
| list_repos | see 2.3 | | | | |

### 2.13 Other: assistant conversation tools

| Tool | Routes | Gate | Purpose (JA) | Key parameters | Source |
|---|---|---|---|---|---|
| get_chat_plan | A-W | write (refuses without `--write`) | この会話に固定された作業計画を読む | — | mcp_chat_plan.go:26 |
| set_chat_plan | A-W | write | この会話の作業計画を全文置換する | plan | mcp_chat_plan.go:37 |
| list_assistants | A-W | write | 相談できるアシスタント（組み込み＋ユーザー定義）の一覧を返す | — | mcp_assistants.go:16 |
| ask_assistant | A-W | write | 別の専門アシスタントに助言を求める（読み取り専用で1ターンだけ） | assistant, prompt | mcp_assistants.go:40 |

### 2.14 Control Plane admin tools (CP only; hidden unless the PAT's owner is super_admin / tenant_admin in the PAT's tenant)

`minScope` in parentheses. Source `cp/mcp.go`.

| Tool | Routes | Gate | Purpose (JA) | Key parameters | Source |
|---|---|---|---|---|---|
| list_workspaces | CP | admin (read) | テナントのメンバーとワークスペースの状態を一覧する | — | cp/mcp.go:1141 |
| get_usage | CP | admin (read) | テナントのリソース使用量（メンバー数・稼働数・上限）を返す | — | cp/mcp.go:1149 |
| list_sessions | CP | admin (read) | テナント全体（またはメンバー指定）のセッション一覧 | user_key | cp/mcp.go:1157 |
| stop_workspace | CP | admin (write) | メンバーのワークスペースコンテナを強制停止する（ホームは残る） | user_key | cp/mcp.go:1165 |
| stop_user_session | CP | admin (write) | メンバーのワークスペース内のセッションを停止する | user_key, name | cp/mcp.go:1175 |
| set_user_quota | CP | admin (write) | メンバーごとのクォータ（セッション数・CPU・メモリ・ディスク等）を設定する | user_key, max_sessions, cpu_units, mem_mib, disk_gb, slot_class | cp/mcp.go:1185 |
| get_egress_stats | CP | super_admin (read) | 送信先ホスト別のegress観測を返す | days | cp/mcp.go:1207 |
| list_allowlist | CP | super_admin (read) | egress許可リストの項目を返す | state | cp/mcp.go:1217 |
| propose_allowlist_change | CP | super_admin (write) | 許可リストへの追加を「提案」状態で作る（有効化はしない） | entry, reason | cp/mcp.go:1225 |
| tail_audit | CP | super_admin whole deployment / else own tenant (read) | 直近の監査ログを返す | limit | cp/mcp.go:1236 |

Scope tiers of the CP member tools (from `minScope`): read = list_my_sessions, get_session_status, get_session_output, list_cleanup_candidates, list_cleanup_archives, get_session_usage, get_agent_usage, list_repos, list_models, list_memos (+ memory_projects/index/search/read); write = the rest (send_to_session, stop_session, stop_session_after_turn, resume_session, archive_session, delete_worktree, delete_session, delete_branch, restore_cleanup_archive, purge_cleanup_archive, create_session, add_memo, update_memo, delete_memo, flush_memos, memory_save, memory_forget). `admin:dangerous` has no tools of its own (same list as write in the golden).

CP-only differences from the Workspace Agent versions: CP `create_session` has fewer parameters (branch, dir, initial_prompt, kind, model, new_branch, route, route_connection, subdir, title, worktree); no schedules, chat plan, assistants, Chromium, peer, spawn-only, snapshot, image or studio tools. The CP does not expose `answer_session_question` / `respond_session_plan`. A stopped workspace answers that memory lives inside it (memory tools need the workspace running).

## 3. Not determined / caveats

- The user-facing Settings labels for each switch were not looked up (only the ui-prefs keys: `peerMessaging`, `sessionFleetSpawn`, `sessionSearch`, `agentMemory`, `imageGeneration`, `externalMemory`). The error text for image generation says "設定 > エージェント".
- Whether claude/codex/etc. each show all S tools depends on the CLI; no per-agent-kind gating of tool lists was found in mcpx, except `generate_image` excluding the session's own CLI as a provider, and `respond_session_plan` working for claude sessions only.
- Exact `create_session` parameter differences A-W vs S vs CP are from the golden (A-W: branch, dir, effort, initial_prompt, kind, model, new_branch, route, route_connection, subdir, title, worktree; S adds allow_shared_working_copy, report_back, spend_cap_usd, work_item).
- Limits of the child-session feature (number of children, spend cap default) are settings-driven (`session.SpawnChildLimit`), value not recorded here.
- CP admin tool line numbers were taken from the `name:` grep, and tenant-role detail (super_admin vs tenant_admin per admin tool) was inferred from descriptions ("super_admin" in text), not checked in the gate code: tail_audit and the egress tools mention super_admin; golden shows tenant_admin sees the same 41 tools as super_admin, so the per-tool restriction is likely enforced at call time.
- Whether the CP's `/mcp` is hosted-assistant specific (as opposed to PAT/OAuth clients generally) could not be told: the code treats every caller as a PAT/OAuth principal.
- Prompts to the assistants/Console's own approval gating (e.g. Discord approval for shell `create_session` in an unattended operator turn, `mcp_fleet_spawn.go:~322`) are not tabulated.
