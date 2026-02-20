# ゼノフラクタル残響コヒーレント蒸留アプリをStreamlitで新規構築する

このExecPlanは生きたドキュメントです。実装中は `Progress`、`Surprises & Discoveries`、`Decision Log`、`Outcomes & Retrospective` を更新し続けます。リポジトリ直下の `PLANS.md` に従って運用します。

## Purpose / Big Picture

この変更により、ユーザーは「ゼノフラクタルの残響」をパラメータで生成し、位相整列とスペクトル重み付けによって「コヒーレントに蒸留された信号」を可視化しながら比較できるようになります。変更前は実行可能なアプリが存在しませんが、変更後は `streamlit run app.py` だけで対話的に操作し、波形・周波数分布・蒸留指標を確認できます。

## Progress

- [x] (2026-02-20 00:00Z) 既存ファイルを確認し、リポジトリが最小構成であることを把握。
- [x] (2026-02-20 00:05Z) Streamlitアプリの設計（入力、生成、蒸留、可視化、履歴保存）を決定。
- [x] (2026-02-20 00:12Z) `app.py` を新規作成し、信号生成・蒸留・可視化・SQLite履歴保存を実装。
- [x] (2026-02-20 00:14Z) `requirements.txt` と `.gitignore` を追加し、実行と成果物管理を明示。
- [x] (2026-02-20 00:18Z) `README.md` を更新し、起動手順と機能説明を追加。
- [x] (2026-02-20 00:22Z) `python -m compileall app.py` で構文検証を完了。
- [x] (2026-02-20 00:24Z) 依存導入・起動確認・スクリーンショット取得を試行し、環境制約を記録。
- [ ] (2026-02-20 00:24Z) 変更をコミットし、PRメッセージを作成。

## Surprises & Discoveries

- Observation: 初期状態のリポジトリは実装コードがなく、READMEもプレースホルダーのみだった。
  Evidence: `rg --files` の結果が `LICENSE README.md AGENTS.md PLANS.md` のみ。

- Observation: ネットワーク制約で `pip install -r requirements.txt` が失敗し、`streamlit` 実行バイナリも利用不可だった。
  Evidence: `ProxyError ... 403 Forbidden` と `bash: command not found: streamlit`。

- Observation: ブラウザキャプチャを試したが、アプリ未起動のため `ERR_EMPTY_RESPONSE` となった。
  Evidence: Playwright の `Page.goto: net::ERR_EMPTY_RESPONSE at http://127.0.0.1:8501/`。

## Decision Log

- Decision: 実装言語はPython、UIはStreamlit、履歴保存はSQLiteを採用。
  Rationale: 利用許可済み技術のみで、対話性と再現性（履歴）を両立できるため。
  Date/Author: 2026-02-20 / Codex

- Decision: 残響生成は「複数周波数の減衰正弦波 + 擬似フラクタル変調 + ノイズ」で近似する。
  Rationale: ユーザー語彙を厳密定義せず、操作可能で視覚的に理解しやすいモデルを提供するため。
  Date/Author: 2026-02-20 / Codex

- Decision: 環境上で実行不可だった検証は失敗として隠さず記録し、再現手順はREADMEへ残す。
  Rationale: 次の実行者が制約を把握しやすく、同じ確認を迅速に再試行できるため。
  Date/Author: 2026-02-20 / Codex

## Outcomes & Retrospective

アプリ本体、依存定義、実行手順、成果物管理は実装完了しました。構文レベルの検証は成功し、UI起動検証とスクリーンショット取得は環境制約で未達です。目的である「利用可能なアプリの実装」は達成しましたが、実環境での最終確認は依存導入が可能な環境で追加実施が必要です。

## Context and Orientation

対象リポジトリの実装起点はルートディレクトリです。主要ファイルは以下です。

- `app.py`: Streamlitアプリ本体。信号生成、蒸留処理、可視化、履歴保存を行う。
- `requirements.txt`: 依存ライブラリ定義。
- `.gitignore`: 画像成果物とDBをGit追跡対象外にする。
- `README.md`: 起動手順と利用方法。

ここでの「蒸留」は、元信号から一貫性の高い成分を強調し、雑音と位相ばらつきを抑える処理として実装する。

## Plan of Work

まず `app.py` を新規作成し、サイドバー入力でユーザーが信号パラメータを調整できるUIを作る。次に、時間軸を生成して残響信号を合成する関数、周波数領域で重み付けと位相整列を行う蒸留関数、品質指標を算出する関数を実装する。続いて、元信号と蒸留信号の比較チャート、周波数成分ヒートマップ、指標カードを配置する。最後にSQLiteへ履歴を保存し、直近結果を表で表示する。補助として依存関係とREADMEを更新し、再現手順を固定する。

## Concrete Steps

作業ディレクトリは `/workspace/LLM_Unknown_build`。

1. ファイル作成・更新
   - `app.py` を新規作成
   - `requirements.txt` を新規作成
   - `.gitignore` を新規作成
   - `README.md` を更新
2. 構文検証
   - `python -m compileall app.py`
3. 起動・画面確認（試行）
   - `python -m pip install -r requirements.txt`（環境制約で失敗）
   - `streamlit run app.py --server.headless true --server.port 8501`（未インストールで失敗）
   - Playwrightで `http://127.0.0.1:8501` を開く（サーバー未起動で失敗）
4. Git
   - `git add ...`
   - `git commit -m "..."`
   - make_pr ツールでタイトル・本文を記録

## Validation and Acceptance

受け入れ基準は次のとおり。

- `streamlit run app.py` でアプリが起動する。
- スライダー操作で波形と指標が変化する。
- 「履歴を保存」操作でSQLiteに記録され、画面上の履歴表に反映される。
- READMEの手順に従って第三者が同様に起動できる。

現時点では、最初の3項目は依存未導入環境で未検証、4項目は文書として整備済み。

## Idempotence and Recovery

`app.py` の処理は読み取り中心であり、履歴保存はSQLiteの追記で安全に繰り返し可能。誤った履歴を消す場合は `xeno_resonance.db` を削除すれば初期状態に戻る。依存導入後の再実行は `pip install -r requirements.txt` を再実行すれば回復できる。

## Artifacts and Notes

実行ログ（抜粋）。

    python -m compileall app.py
    Compiling 'app.py'...

    python -m pip install -r requirements.txt
    ERROR: ... ProxyError ... 403 Forbidden

    streamlit run app.py --server.headless true --server.port 8501
    bash: command not found: streamlit

## Interfaces and Dependencies

依存ライブラリは `streamlit`、`numpy`、`pandas`。標準ライブラリの `sqlite3` と `datetime` を使用する。

アプリ内部には以下の関数インターフェースを定義する。

- `generate_xeno_echo(...) -> tuple[np.ndarray, np.ndarray]`
  時間軸と元信号を返す。
- `distill_coherence(...) -> tuple[np.ndarray, np.ndarray]`
  蒸留信号と周波数ごとの重みを返す。
- `compute_metrics(...) -> dict[str, float]`
  エネルギー比率や位相安定度などの指標を返す。
- `ensure_db()`, `save_run(...)`, `fetch_recent_runs(...)`
  履歴保存と取得を提供する。

---
更新履歴: 2026-02-20 第2版更新。理由: 実装完了と検証結果（環境制約を含む）を反映するため。
