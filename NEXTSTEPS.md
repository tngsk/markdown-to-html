# 開発ステップとフェーズ管理 (NEXTSTEPS.md)

## インタラクティブ機能（新規追加）
目的: 参加者の能動的なインタラクションとセッション運用性を向上させる小規模コンポーネント群を追加する。各機能は独立コンポーネントとして実装し、依存先がない場合は安全に非表示（エラーを出さずドキュメントに含めない）になる設計とする。

### 1) situ-reaction（ユーザーリアクション）
- マークダウン構文案: `@[reaction: "手を挙げる,？マーク"]`
- 概要: ユーザーが手を挙げる、質問あり（？）などのリアクションを送れる小さなUI。各リアクションはカウントされ、表示される。
- 実装場所（推奨）:
  - templates/components/situ-reaction/
    - situ-reaction.html
    - situ-reaction.js
    - situ-reaction.css
- 動作:
  - Local Storage キー: `situ_reaction_{component_id}`
  - 送信ペイロード（例）:
    {
      "timestamp": "ISO8601",
      "componentId": "reaction-xxx",
      "reactionType": "hand_up",
      "reactionLabel": "手を挙げる"
    }
  - オフライン時も Local Storage に蓄え、通信復帰時に送信可能。
  - WebSocket インフラが存在する場合は主催者へリアルタイム通知（オプション）。
- 依存: なし（独立で機能）

### 2) situ-session-join（セッション参加）
- マークダウン構文案: `@[session-join: "セッション参加"]`
- 概要: セッション番号を入力して参加するためのコンポーネント。参加状態は Local Storage に保存され、他コンポーネントはこれを参照できる。
- 実装場所（推奨）:
  - templates/components/situ-session-join/
    - situ-session-join.html
    - situ-session-join.js
    - situ-session-join.css
- 動作:
  - Local Storage キー: `situ_session_id`（ドキュメント/ブラウザ単位）
  - 送信ペイロード（例）:
    {
      "timestamp": "ISO8601",
      "sessionId": "SESSION-12345",
      "userId": "generated-uuid"
    }
  - 入力バリデーション（英数字、ハイフン許可）。参加後は確認表示に切替、変更可能。
  - 依存: なし（独立で機能）

### 3) situ-group-assignment（グループ分け）
- マークダウン構文案: `@[group-assignment: "グループ分け"]`
- 概要: セッション参加中のユーザーを指定のロジックでグループ分配し、割り当てられたグループをユーザーにフィードバックする。
- 実装場所（推奨）:
  - templates/components/situ-group-assignment/
    - situ-group-assignment.html
    - situ-group-assignment.js
    - situ-group-assignment.css
- 動作:
  - Local Storage キー: `situ_group_assignment`
  - 送信ペイロード（例）:
    {
      "timestamp": "ISO8601",
      "sessionId": "SESSION-12345",
      "userId": "generated-uuid",
      "groupId": "GROUP-A",
      "groupName": "グループA",
      "assignmentMethod": "round-robin"
    }
  - グループ分配アルゴリズム（選択肢）:
    - round-robin（参加順で割当）
    - random（ランダム）
    - server-driven（サーバからの指示を受信）
  - 依存:
    - 基本動作は situ-session-join の sessionId を参照（セッション未参加時は「セッションに参加してください」と表示し、コンポーネント自体はドキュメントに含めない）。
    - WebSocket やサーバAPI が存在する場合はサーバ側の割当情報を優先して反映。
- エラー挙動:
  - セッション未参加や分配情報未取得時はエラーにせず、ユーザー向けの案内表示のみ行う。
