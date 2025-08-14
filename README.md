# Werewolf Arena: ソーシャルディダクションゲーム

このリポジトリは [Werewolf Arena](https://arxiv.org/abs/2407.13943) のコードを提供します。Werewolf Arena は、人狼ゲームを通じて大規模言語モデル（LLM）の社会的推論能力を評価するためのフレームワークです。
ゲームは夜フェーズ（人狼が村人を襲撃、占い師が調査、医者が保護）と昼フェーズ（全員で議論・投票して追放者を決定）を交互に繰り返します。 
各プレイヤーはLLMによって自動制御され、ゲーム実行中にユーザーの介入は一切必要ありません。 
村人チーム（占い師・医者・村人）が人狼を全員追放するか、人狼チームが村人と同数以上になるまでゲームが続きます。 



---

## 環境のセットアップ（Windows）

### 1. Python 仮想環境の作成

PowerShell などで以下を実行:

```powershell
python -m venv venv
```

### 2. 仮想環境の有効化

```powershell
.\venv\Scripts\activate
```

### 3. 依存関係のインストール

```powershell
pip install -r requirements.txt
```

### 4. OpenAI API キーの設定

PowerShell で以下を実行（`xxxxx` は自分のキーに置き換え）:

```powershell
setx OPENAI_API_KEY "xxxxx"
```

その後、ターミナルを再起動してください。

### 5. Gemini を利用する場合（任意）

* [gcloud CLI をインストール](https://cloud.google.com/sdk/docs/install)
* 認証を行い GCP プロジェクトを設定
* 以下を実行してアプリケーションデフォルトの認証情報を作成

```powershell
gcloud auth application-default login
```

---

## 単一ゲームの実行（Windows）

`gpt4o-mini` モデルを使用して実行する例:

```powershell
python main.py --run --v_models=gpt4o-mini --w_models=gpt4o-mini
```

---

## すべてのモデル組み合わせでのゲーム実行

```powershell
python main.py --eval --num_games=5 --v_models=pro1.5,flash --w_models=gpt4,gpt4o
```

---

## 失敗したゲームの一括再開

```powershell
python main.py --resume
```

（再開対象は `runner.py` にハードコードされています）

---

## インタラクティブビューアの起動（Windows）
![alt text](viewer.png)

### 1. Node.js をインストール

* [Node.js公式サイト](https://nodejs.org/) から LTS 版をインストール
* 確認:

```powershell
node -v
npm -v
```

### 2. ビューアの起動

プロジェクトのルートで:

```powershell
npm install
npm run start
```

### 3. ブラウザでログを開く

例: `werewolf_arena_ja\logs\session_20250814_001710` の場合

```
http://localhost:8080/?session_id=session_20250814_001710
```

ブラウザ上でプレイヤーの推論・投票の流れを視覚的に確認できます。
