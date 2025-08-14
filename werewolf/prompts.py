# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

GAME = """あなたはソーシャルディダクションゲーム「人狼」（Mafia とも呼ばれる）のデジタル版をプレイしています。

ゲームのルール:
- プレイヤーの役割: {{num_players}} 人のプレイヤー - 人狼2人、占い師1人、医者1人、村人 {{num_villagers}} 人。
- 各ラウンドは2つのフェーズから成ります:
    - 夜のフェーズ: 人狼は1人を襲撃し、占い師は1人の役職を占い、医者は1人を守ります。誰も襲撃されなかった場合、医者が人狼の標的を救いました。
    - 昼のフェーズ: プレイヤーは議論し、1人を追放するために投票します。
- 勝利条件: 村人陣営は2人の人狼を追放すれば勝利。人狼陣営は人狼の数が村人を上回った時点で勝利します。"""

STATE = """ゲームの状態:
- 現在はラウンド {{round}} です。{% if round == 0 %}ゲームは始まったばかりです。{% endif %}
- あなたは {{role}} の {{name}} です。{{werewolf_context}}
{% if personality -%}
- 性格: {{ personality }}
{% endif -%}
- 残りのプレイヤー: {{remaining_players}}"""

OBSERVATIONS = """{% if observations|length -%}あなたの秘密の観察:
{% for turn in observations -%}
{{ turn }}
{% endfor %}
{% endif %}"""

DEBATE_SO_FAR_THIS_ROUND = """\nラウンド {{round}} の議論:
{% if debate|length -%}
{% for turn in debate -%}
{{ turn }}
{% endfor -%}
{% else -%}
まだ議論は始まっていません。{% endif %}\n\n"""

PREFIX = f"""{GAME}

{STATE}

{OBSERVATIONS}
""".strip()

BIDDING = (
    PREFIX
    + DEBATE_SO_FAR_THIS_ROUND
    + """コンテキスト: 次に発言する権利を得るために入札を行います。最も高い入札をしたプレイヤーが先に発言します。
- 入札の選択肢:
  0: 今は様子を見て静かに聞きたい。
  1: グループに共有したい一般的な考えがある。
  2: この議論に対して重要かつ具体的な意見を持っている。
  3: 次に発言することが絶対に必要だ。
  4: 誰かに直接呼びかけられたので応答しなければならない。
- あなたが発言できる残りの回数: {{debate_turns_left}} 回

指示:
- {{role}} の {{name}} として戦略的に考えてください。
- 影響力のある発言がある場合にのみ発言を優先してください。
- 特にこれまで非常に発言していたり、目立って静かだった場合は、参加のバランスを取ってください。
{% if role == 'Werewolf' -%}
- 会話を混乱や不信に導くか、村人への疑念を植え付けるか、自分や仲間への疑いをそらすかを判断してください。
- 沈黙は強力な戦術ですが、参加しないことは疑いを招く場合があります。
{% else -%}
- 議論が繰り返しになったり脱線している場合は、より戦略的な方向へ導く準備をしてください。
- 疑いをかけられている場合や、議論があなたの役職に直接関係する場合は発言を優先してください。
- 情報を共有し、告発を戦略的に行いましょう。ただし、そうすることで標的にされる可能性があることに注意してください。
{% endif %}

```json
{
"reasoning": "string",  // 今すぐ議論に参加することがどれほど重要かを一、二文で説明してください。暴力的または有害な言葉は避けてください。
"bid": "string" // 上記の理由に基づき入札を行ってください。応答は "0" | "1" | "2" | "3" | "4" のいずれかの数字です。
}"
"""
)

BIDDING_SCHEMA = {
    "type": "object",
    "properties": {
        "reasoning": {"type": "string"},
        "bid": {"type": "string"},
    },
    "required": ["reasoning", "bid"],
}

DEBATE = PREFIX + DEBATE_SO_FAR_THIS_ROUND + """指示:
- あなたは {{role}} の {{name}} として次に発言します。
- 次に発言することについてのあなたの考え: {{bidding_rationale}}
{% if role == 'Werewolf' -%}
- 目的は混乱を招き、正体を隠すことです。
- 村人に疑いを向けさせ、お互いを信用できなくさせましょう。
- 自分や仲間の人狼から話題をそらしてください。
- 村人を助けているように見せかけながらも、その努力を妨害します。
- 欺瞞は最大の武器です。例えば、特殊役職を名乗って村人を偽って告発したり、矛盾を作り出して混乱させたりできます。ただし、怪しまれないようにこれらの強力な手段は控えめに使ってください。
{% else -%}
- 目的は人狼を見つけ出し、村を守ることです。
- すべての告発を精査し、矛盾を暴き、怪しい行動や異常に静かなプレイヤーを指摘してください。大胆な告発もためらわないでください。
- 協力を強調し、人狼を暴くための戦略を提案しましょう。協力が人狼特定の鍵になります。
{% if role == 'Villager' -%}
- 誰かが占い師や医者だと名乗った場合は、自分が知っている情報と照らし合わせて確認してください。
{% elif role in ['Seer', 'Doctor'] -%}
- 自分の役職を明かすことは強力ですが、同時に標的にもなります。秘密のまま村を助けるべきか、それとも自分だけが持つ情報を明かして大きな影響を与えるべきか、賢く選びましょう。
{% endif -%}
{% endif %}

```json
{
  "reasoning": "string", // 現在のゲーム状態とあなたの役割の目的に基づき、戦略を説明してください。何を達成したいですか？どのようなメッセージがそれを助けますか？暴力的または有害な言葉は避けてください。
  "say": "string" // 議論でのあなたの公開発言です。簡潔かつ説得力のあるものにし、他のプレイヤーの発言に直接応答してください。単に他人の発言を繰り返したり上記の指示を書き写したりしないでください。
}
"""

DEBATE_SCHEMA = {
    "type": "object",
    "properties": {
        "reasoning": {"type": "string"},
        "say": {"type": "string"},
    },
    "required": ["reasoning", "say"],
}

VOTE = PREFIX + DEBATE_SO_FAR_THIS_ROUND + """指示:
- {{role}} の {{name}} として、誰を追放するか戦略的に決定してください。
- あなたの投票は他のプレイヤーには公開されず、非公開のままです。
- 告発を精査し、行動を分析し、過去のパターンを考慮してください。
{% if role == 'Werewolf' -%}
- 計画を妨害する、特に影響力があり医者や占い師である可能性のある村人、またはあなたや仲間にとって脅威となる村人を狙いましょう。
- 村人たちが誰かを疑い始めたら、その流れに乗り、既に疑われている不運な村人に投票しましょう。
{% else -%}
- 人狼と思われる者を見つけるため、話の矛盾や責任転嫁、他の村人の間に不和をまこうとする行動、または異常に静かなプレイヤーを探してください。
{% endif -%}
- 必ず誰かを選ばなければなりません。

```json
{
  "reasoning": "string", // 誰を追放すべきかについてのあなたの理由を説明してください。暴力的または有害な言葉は避けてください。
  "vote": "string" // プレイヤー名。選択肢: {{options}}
}"""

VOTE_SCHEMA = {
    "type": "object",
    "properties": {
        "reasoning": {"type": "string"},
        "vote": {"type": "string"},
    },
    "required": ["reasoning", "vote"],
}

INVESTIGATE = PREFIX + """指示:
- ラウンド {{round}} の夜のフェーズです。{{role}} の {{name}} として、最も怪しいプレイヤーを1人調べてください。
{% if round == 0 -%}
- 初日の夜には情報がないため、ランダムに選んでください。
{% else -%}
- 典型的な村人の行動と異なる振る舞いを探してください。
- 影響力のあるプレイヤーに注目してください。
- 必ず誰かを選ばなければなりません。
{% endif %}

```json
{
"reasoning": "string", // 証拠を分析し、誰を調べたいかその理由を説明してください。
"investigate": "string" // プレイヤー名。選択肢: {{options}}
}
"""

INVESTIGATE_SCHEMA = {
    "type": "object",
    "properties": {
        "reasoning": {"type": "string"},
        "investigate": {"type": "string"},
    },
    "required": ["reasoning", "investigate"],
}

ELIMINATE = PREFIX + """指示:
- ラウンド {{round}} の夜のフェーズです。{{role}} の {{name}} として、最も戦略的に除去すべきプレイヤーを選んでください。
{% if round == 0 -%}
- 初日の夜には情報がないため、ランダムに選んでください。
{% else -%}
- 告発を分析し、あなたの正体を脅かす影響力のある村人を特定してください。
- プレイヤーの行動と、除去することのリスクを考慮してください。
- 必ず誰かを選ばなければなりません。
{% endif %}

```json
{
"reasoning": "string", // 誰をゲームから除外したいか、段階的に理由を説明してください。暴力的または有害な言葉は避けてください。
"remove": "string" // プレイヤー名。選択肢: {{options}}
}
"""

ELIMINATE_SCHEMA = {
    "type": "object",
    "properties": {
        "reasoning": {"type": "string"},
        "remove": {"type": "string"},
    },
    "required": ["reasoning", "remove"],
}

PROTECT = PREFIX + """指示:
- ラウンド {{round}} の夜のフェーズです。{{role}} の {{name}} として、最も守るべきプレイヤーを選んでください。
{% if round == 0 -%}
- 初日の夜には情報がないため、ランダムに選んでください。
{% else -%}
- 人狼が狙いそうなプレイヤーを考えてください。
- 占い師や自分など、重要な役職のプレイヤーを優先して守ってください。
- 必ず誰かを選ばなければなりません。
{% endif %}

```json
{
"reasoning": "string", // 誰を守るべきかの理由を分析して説明してください。
"protect": "string" // プレイヤー名。選択肢: {{options}}
}
"""

PROTECT_SCHEMA = {
    "type": "object",
    "properties": {
        "reasoning": {"type": "string"},
        "protect": {"type": "string"},
    },
    "required": ["reasoning", "protect"],
}

SUMMARIZE = PREFIX + DEBATE_SO_FAR_THIS_ROUND + """指示:
- {{role}} の {{name}} として、このラウンドの議論を振り返ってください。
- 重要なポイントと戦略的な示唆を要約してください。
{% if role == 'Werewolf' -%}
- あなたや仲間への告発に注意を払いましょう。
- 共感的または影響されやすいプレイヤーを特定してください。
- 除去候補となる重要な役職を特定してください。
{% else -%}
- プレイヤーが重要な発言や情報を共有したとき、その信頼性を慎重に判断してください。それはあなたの知っている情報と一致していますか？
- 議論への他者の参加の仕方を分析してください。発言に矛盾はありますか？行動の裏に隠された意図は？異常に静かなプレイヤーは？
- 議論に基づき、潜在的な味方、信頼できるプレイヤー、占い師や医者の可能性がある人物を特定できますか？
{% endif %}

```json
{
"reasoning": "string", // この議論から何を記憶すべきか、なぜそれが重要かを説明してください。
"summary": "string" // 議論の主要な点や注目すべき観察を数文で要約してください。できるだけ多くのプレイヤーについてメモを取りましょう。些細に見える詳細でも後のラウンドで重要になるかもしれません。具体的に書いてください。あなたは {{name}} であることを忘れず、「私」を使ってあなたの視点からまとめてください。
} """

SUMMARIZE_SCHEMA = {
    "type": "object",
    "properties": {
        "reasoning": {"type": "string"},
        "summary": {"type": "string"},
    },
    "required": ["reasoning", "summary"],
}

ACTION_PROMPTS_AND_SCHEMAS = {
    "bid": (BIDDING, BIDDING_SCHEMA),
    "debate": (DEBATE, DEBATE_SCHEMA),
    "vote": (VOTE, VOTE_SCHEMA),
    "investigate": (INVESTIGATE, INVESTIGATE_SCHEMA),
    "remove": (ELIMINATE, ELIMINATE_SCHEMA),
    "protect": (PROTECT, PROTECT_SCHEMA),
    "summarize": (SUMMARIZE, SUMMARIZE_SCHEMA),
}