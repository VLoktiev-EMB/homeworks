# Phase 8: Fast CI - Pattern Map

**Mapped:** 2026-10-26
**Files analyzed:** 8 (4 new/modified у scope, 3 видалення, 1 опційний)
**Analogs found:** 5 / 8 (3 мають лише частковий збіг або не мають аналога)

> **Мова:** наративний текст — українською; код, шляхи, ідентифікатори та YAML-ключі — англійською.

---

## ⚠️ Обов'язкове попередження для планера: CONTEXT/RESEARCH застаріли щодо docs-сайту

Перед плануванням треба врахувати розбіжність між upstream-документами та поточним деревом.
Commit `9d28f5d` («remove the generated documentation site», PR #18) виконано **до** збору
контексту Phase 8, і він видалив:

| Шлях, на який спираються CONTEXT/RESEARCH | Стан у дереві |
|---|---|
| `.github/workflows/docs.yml` | **MISSING** |
| `mkdocs.yml` | **MISSING** |
| `requirements-docs.txt` | **MISSING** |
| `docs/assets/vendor/katex/0.19.0/FILES.sha256` (KaTeX ledger) | **MISSING** |

Наслідки, які планер мусить явно розв'язати в PLAN.md:

1. **D-15 частково нездійсненний.** `docs-build` (`mkdocs build --strict` +
   `scripts/ci/check_lfs_pointers.sh site`) не має ні вхідного `mkdocs.yml`, ні
   `requirements-docs.txt`, ні каталогу `site/`. Job `docs-build` треба або прибрати з `gate.needs`,
   або перевизначити на щось інше. Це рішення не входить у мою компетенцію; воно потребує
   підтвердження оркестратора/користувача, бо змінює D-15 і D-1.
2. **D-1 у частині «`docs.yml` stays `main`-only» не має об'єкта** — файлу немає. Топологія
   `ci.yml` + `nightly.yml` лишається чинною; `docs.yml` просто не існує.
3. **`scripts/ci/check_lfs_pointers.sh` залишився сиротою**: його єдиний виклик був у
   `docs.yml`, тепер його викликає лише `scripts/tests/test_ci_workflows.py`. Не видаляти в цій
   фазі (тест на нього лишається зеленим), але й не підключати до нового `docs-build`, якого немає.
4. **Research-таблиця Standard Stack містить `requirements-docs.txt`** — цей рядок для плану
   недійсний.
5. **Кількість workflow у тесті вже 3, не 4.** `scripts/tests/test_ci_workflows.py:109` зараз
   asserts `3` (`generated-views.yml`, `homework.yml`, `security.yml`), а не 4, як цитує
   RESEARCH (Pitfall 17 посилається на рядок 119). Після фази файлів буде **2**
   (`ci.yml`, `nightly.yml`).

Якщо оркестратор вирішить зберегти `docs-build`, йому доведеться спершу відновити
`mkdocs.yml` і `requirements-docs.txt` — це окремий обсяг, не передбачений ні CONTEXT, ні
deferred-списком.

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `.github/workflows/ci.yml` (new) | workflow / config (CI orchestration) | event-driven (PR-події) → job graph | `.github/workflows/homework.yml` + `.github/workflows/generated-views.yml` + `.github/workflows/security.yml` (композит) | role-match (композиція трьох) |
| `.github/workflows/nightly.yml` (new) | workflow / config (scheduled batch) | batch / schedule | `.github/workflows/homework.yml` (команди build/test) + `security.yml` (full-history checkout) | role-match |
| `scripts/tests/test_ci_workflows.py` (modify) | test (stdlib `unittest`, text-contract) | batch assertions | сам себе + `scripts/tests/test_affected.py` (стиль subprocess-виклику) | exact (extend in place) |
| `AGENTS.md` (modify) | config / policy documentation | static | сам себе (`docs/decisions/README.md` як стиль рядка-рішення) | exact (edit in place) |
| `.github/workflows/homework.yml` (delete) | workflow | — | — | n/a |
| `.github/workflows/generated-views.yml` (delete) | workflow | — | — | n/a |
| `.github/workflows/security.yml` (delete) | workflow | — | — | n/a |
| `.github/pull_request_template.md` (modify, optional) | documentation | static | сам себе | exact |
| `docs/decisions/README.md` (modify, optional) | documentation (decision index) | static | сам себе | exact |
| `.yamllint.yaml` (modify, optional) | config | static | сам себе | exact |

**Аналоги, яких НЕМАЄ в репозиторії** (планер бере патерн із `08-RESEARCH.md`):
fan-in `gate`, opt-in `simulate`, `nightly` за розкладом, `static-analysis` job.

---

## Pattern Assignments

### `.github/workflows/ci.yml` (workflow, event-driven → job graph)

Це композит трьох наявних workflow. Жоден наявний файл не є повним аналогом, тому планер має
складати job-и з наведених нижче фрагментів, а не копіювати один файл.

#### Заголовок, тригер, дозволи, concurrency

**Analog:** `.github/workflows/homework.yml:1-12`

```yaml
name: homework

on:
  pull_request:
  workflow_dispatch:

permissions:
  contents: read

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

Що змінити для `ci.yml`:

- `name: ci`.
- `on.pull_request.types:` розширити (Pitfall 15): `opened`, `synchronize`, `reopened`, `edited`
  — інакше редагування заголовка PR не перезапускає title-check.
- `permissions` і `concurrency` — скопіювати дослівно (D-18 не чіпає цей блок; `cancel-in-progress`
  лишається, див. Pitfall 21).

#### Коментар-обґрунтування read-only дозволів

**Analog:** `.github/workflows/generated-views.yml:7-10`

```yaml
# META-05 asks CI to fail on drift; it does not ask CI to repair it. A
# pull-request job runs contributor-controlled code, so it gets read access to
# the repository and nothing else: no secret, no write token, no
# `pull_request_target`.
permissions:
  contents: read
```

Стиль коментаря (англійська, ідентифікатор рішення, причина) — обов'язковий: усі наявні
workflow коментують кожен неочевидний вибір. Для `ci.yml` коментар має пояснити fan-in `gate`
і чому `always()` не використовується (D-2).

#### Піни екшенів і checkout

**Analog:** `.github/workflows/homework.yml:20-24`

```yaml
      # Pinned to the v7.0.1 commit, not the mutable `v7` major tag: a tag can
      # be repointed at other code between runs, a commit SHA cannot.
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1  # v7.0.1
        with:
          persist-credentials: false
```

Для `meta`/`changes` додати `fetch-depth: 0` (D-3, D-14). Зразок `fetch-depth: 0`:

**Analog:** `.github/workflows/security.yml:19-21`

```yaml
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1  # v7.0.1
        with:
          fetch-depth: 0
```

Для `meta` і `changes` обидва параметри разом: `persist-credentials: false` **і** `fetch-depth: 0`.

#### Python і встановлення інструментів

**Analog:** `.github/workflows/homework.yml:31-35`

```yaml
      - uses: actions/setup-python@6d4fd22b20465ccc0f7354476588e8df7c9ca0e0  # v7.1.0
        with:
          python-version: '3.13'
      - name: Install PlatformIO Core
        run: python -m pip install platformio==6.2.0
```

Команда pip-install з точним піном — це наявний патерн репозиторію (не новий). Для `python-tests`
додати `python -m pip install uv==0.13.5` (Pitfall 18, A8).

#### Кеш інструментів

**Analog:** `.github/workflows/homework.yml:25-30`

```yaml
      - uses: actions/cache@55cc8345863c7cc4c66a329aec7e433d2d1c52a9  # v6.1.0
        with:
          path: |
            ~/.cache/pip
            ~/.platformio/.cache
          key: ${{ runner.os }}-pio
```

**Критично:** ключ `${{ runner.os }}-pio` у наявному файлі — саме та пастка, яку D-18 і
Pitfall 6 забороняють повторювати. Для `build`/`simulate`/`nightly` ключ мусить бути похідним
від пінів:

```yaml
          key: ${{ runner.os }}-pio-${{ hashFiles('platformio.shared.ini') }}
```

Без `restore-keys`. Це відхилення від аналога за рішенням D-18, а не копіювання.

#### Кеш pre-commit

**Analog:** той самий `actions/cache` виклик, але з ключем за конфігом (D-13):

```yaml
      - uses: actions/cache@55cc8345863c7cc4c66a329aec7e433d2d1c52a9  # v6.1.0
        with:
          path: ~/.cache/pre-commit
          key: ${{ runner.os }}-pre-commit-${{ hashFiles('.pre-commit-config.yaml') }}
```

#### Лінт-поверхня одним кроком

**Analog:** команда з `.pre-commit-config.yaml` (`minimum_pre_commit_version: '4.7.0'`, 13 хуків),
а форма запуску — з `.github/workflows/generated-views.yml:39-44` (встановлення інструмента
окремим кроком, команда окремим кроком, check-only):

```yaml
      - name: Install PyYAML
        run: python -m pip install PyYAML==6.0.3
      # The same command the pre-commit hook runs, so there is one drift
      # contract. Check-only: the job never regenerates or commits.
      - name: Check generated views
        run: python scripts/gen_views.py --all --check
```

Для `meta` (D-13):

```yaml
      - name: Install the pinned gate tools
        run: python -m pip install pre-commit==4.7.0
      - name: Install pre-commit environments
        run: pre-commit install-hooks
      - name: Run the hook surface
        run: pre-commit run --all-files --show-diff-on-failure
```

Примітка про прибраний `generated-views.yml`: після видалення файлу перевірка drift переїжджає
в `pre-commit run --all-files` (хук `gen-views-check`,
`.pre-commit-config.yaml:188-196`). Окремого кроку `python scripts/gen_views.py --all --check`
у `ci.yml` не потрібно; тест має asserts-ити або id хука, або команду `pre-commit run --all-files`.

#### Gitleaks: встановлення й повний скан

**Analog:** `.github/workflows/security.yml:22-45` — копіювати дослівно в `meta`.

```yaml
      - name: Install gitleaks
        env:
          GITLEAKS_VERSION: 8.30.1
          # Published in gitleaks_8.30.1_checksums.txt and confirmed against
          # the GitHub release-asset digest for the same upload.
          GITLEAKS_SHA256: 551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb
        run: |
          set -euo pipefail
          archive="$RUNNER_TEMP/gitleaks.tar.gz"
          # The release URL is assembled in three parts so the YAML line stays
          # readable; the resulting download is byte-identical to the one-line
          # spelling. The checksum check below still fails closed.
          release="https://github.com/gitleaks/gitleaks/releases/download"
          release="${release}/v${GITLEAKS_VERSION}"
          curl --proto '=https' --tlsv1.2 -sSfL \
            "${release}/gitleaks_${GITLEAKS_VERSION}_linux_x64.tar.gz" \
            -o "$archive"
          # Fail closed: a substituted or truncated artifact stops the job
          # before the binary is unpacked or executed.
          echo "${GITLEAKS_SHA256}  ${archive}" | sha256sum -c -
          tar -xzf "$archive" -C "$RUNNER_TEMP" gitleaks
          install -m 0755 "$RUNNER_TEMP/gitleaks" /usr/local/bin/gitleaks
      - name: Scan full history
        run: gitleaks git --redact --verbose --log-opts="--all"
```

Цей самий блок (встановлення + коментар про fail-closed) — готовий аналог для встановлення
`wokwi-cli` в `simulate`, де публікованого checksum-файлу немає (див. нижче «Немає аналога»).

#### PR-title check (новий крок, але з наявним стилем env-індирекції)

Аналога для regex-check немає; механіка env-індирекції для недовірених значень — з
GitHub-практики, зафіксованої в RESEARCH Pitfall 10. Форму кроку брати з `security.yml:44-45`
(`- name:` + `run: |` з `set -euo pipefail`).

#### Job `gate`

**Немає аналога в репозиторії.** Брати `08-RESEARCH.md` Pattern 1 дослівно (`toJSON(needs)` +
`jq` allowlist `success`/`skipped`, `if: ${{ !cancelled() }}`). Єдине, що береться з аналогів —
`runs-on: ubuntu-24.04`, `timeout-minutes: 5` (D-19), `set -euo pipefail`.

#### Job `simulate`

**Немає аналога.** Брати `08-RESEARCH.md` Pattern 4. Додатково: білд перед сценарієм —
команда з `.github/workflows/homework.yml:36-37`:

```yaml
      - name: Build the target environment
        run: pio run -d homeworks/1_3-police-flasher
      - name: Run native unit tests
        run: pio test -d homeworks/1_3-police-flasher -e native
```

але з `"$PROJECT"` / `"$ENV_NAME"` через `env:` (Pitfall 10).

#### Job `static-analysis` (якщо приймається Open Question 3)

**Analog:** команди з `AGENTS.md:176-186` + `scripts/clang-tidy-db:52-60`:

```bash
pio run -d tests -e native -t compiledb
pre-commit run --all-files --hook-stage pre-push
```

`scripts/clang-tidy-db` — це guard, а не крок, який генерує базу; у CI база генерується
таргетом `compiledb` (A: локально перевірено).

---

### `.github/workflows/nightly.yml` (workflow, scheduled batch)

#### Тригер

**Немає аналога** (жоден наявний workflow не має `schedule:`). Форма — з GitHub-синтаксису:

```yaml
on:
  schedule:
    - cron: '17 3 * * *'
  workflow_dispatch:
```

Хвилина в межах ~03:00 UTC — Claude's Discretion (CONTEXT).

#### Matrix і команди білда

**Analog:** `.github/workflows/homework.yml:14-39` — але `job` і `matrix` замінюються на
`fromJson`; `runs-on`, `timeout-minutes`, кроки `setup-python` + `pip install platformio==6.2.0`
беруться як є. `timeout-minutes: 90` (D-19) замість 45.

Команда розгалуження `native` vs інші env — з `homework.yml:36-39`, оформлена як `if` (D-6).

#### Обчислення повної матриці

**Analog:** той самий виклик `scripts/affected.py`, що й у `changes` в `ci.yml`, але з
`--paths-from` замість `--base`. Контракт CLI:

`scripts/affected.py:56-57`:

```text
  uv run scripts/affected.py [--dir PATH] [--paths-from PATH | --base REV]
                             [--format {json,paths}]
```

`scripts/affected.py:497` — `json.dumps(payload, indent=2)`, тому обов'язковий `jq -c`
(Pitfall 5). Повний widen-all рецепт — `08-RESEARCH.md` Pattern 5 (перевірено локально).

#### Gitleaks у nightly

Той самий блок `security.yml:22-45` плюс `fetch-depth: 0` (Open Question 1, Pitfall 20).

---

### `scripts/tests/test_ci_workflows.py` (test, text-contract)

**Analog:** сам файл; його структура — джерело істини.

Стильові елементи, які треба зберегти:

- Модульний docstring пояснює, що саме доводить текст, а що — поведінка
  (`scripts/tests/test_ci_workflows.py:1-16`).
- `REPO_ROOT = Path(__file__).resolve().parents[2]`, константи шляхів на рівні модуля
  (рядки 25-32). Для фази замінити `GENERATED_VIEWS` на:

```python
WORKFLOWS = REPO_ROOT / ".github" / "workflows"
CI = WORKFLOWS / "ci.yml"
NIGHTLY = WORKFLOWS / "nightly.yml"
PRECOMMIT = REPO_ROOT / ".pre-commit-config.yaml"
```

- Клас `WorkflowTextTests` (рядки 84-89) — місце для нових текстових контрактів:

```python
class WorkflowTextTests(unittest.TestCase):
    """The names and commands the YAML must carry; behaviour lives above."""

    def test_generated_views_names_the_check_command(self) -> None:
        text = GENERATED_VIEWS.read_text(encoding="utf-8")
        self.assertIn("python scripts/gen_views.py --all --check", text)
```

  Замінити цей тест на перевірку `gen-views-check` у `.pre-commit-config.yaml`
  (`.pre-commit-config.yaml:188-196`) **і/або** наявності
  `pre-commit run --all-files` у `ci.yml`. Другий варіант — контракт TOOL-05.
- `test_all_three_workflows_declare_a_textual_trigger_key` (рядки 107-113): число **3**
  змінюється на **2** і назву можна лишити нейтральною (`test_every_workflow_declares_a_textual_trigger_key`).
  Glob `WORKFLOWS.glob("*.yml")` лишається.
- `test_no_workflow_spells_a_trigger_as_a_boolean_key` (115-125) — без змін.
- `test_the_policy_relaxes_truthy_keys_and_keeps_boolean_values` (127-130) — без змін.

Нові контракти, які RESEARCH §Wave 0 Gaps перелічує, і їхній якір у файлі:

| Твердження | Рядок-джерело істини |
|---|---|
| literal job id `gate` і `needs:` покриває всі PR-job-и | `ci.yml` (після створення) |
| `if: ${{ !cancelled() }}` на `gate` | `ci.yml` |
| `gitleaks git --redact --verbose --log-opts="--all"` | `ci.yml` (аналог `security.yml:45`) |
| `wokwi-cli lint` присутній | `ci.yml` |
| `uv run scripts/affected.py --base` | `ci.yml` |
| job-level guard порожньої матриці | `ci.yml` |
| guard `simulate` + `upload-artifact` | `ci.yml` |
| nightly викликає `--paths-from` і не згадує simulation | `nightly.yml` |

Стиль поведінкового тесту (якщо планер додає реальний запуск) — `scripts/tests/test_affected.py:27-49`
(`run_affected` з `uv run`, `shutil.which("uv")` guard, `timeout`). Але для workflow-контрактів
достатньо тексту (04/D-14: stdlib-only, без PyYAML).

---

### `AGENTS.md` (config / policy documentation)

**Analog:** сам файл; точкові місця для D-21:

| Рядок | Що зараз | Що має стати |
|---|---|---|
| 20-26 | quick-start із 4 кроків | додати CI-команди (matrix/`gate`) у визначенні DoD |
| 32 | `.github/workflows/security.yml` — the full-history secret scan | `.github/workflows/ci.yml` — `meta` (full-history scan) + `gate` |
| 48-49 | «`gen-views-check` pre-commit hook and the `generated-views` pull-request workflow both run…» | лишити `gen-views-check`, прибрати workflow |
| 150-155 | Secrets: `security.yml` scans full history | `ci.yml` `meta` сканує повну історію; nightly — теж (якщо прийнято Open Question 1) |
| 158-186 | Quality tooling (pre-commit / pre-push) | додати, що CI запускає hook-поверхню повністю |
| 242 | routing: `.pre-commit-config.yaml` and `.github/workflows/security.yml` | `.pre-commit-config.yaml` and `.github/workflows/ci.yml` |
| (PR/tags §140-146) | немає згадки `gate` | назвати `gate` як єдиний required check |

Стиль рядка-правила (severity + enforcement point) — з `AGENTS.md:74-80`:

```markdown
Every rule carries two dimensions: severity (`[MUST]` or `[SHOULD]`) and where a violation is
caught (`[ENFORCED: pre-commit]`, `[ENFORCED: pre-push]`, `[ENFORCED: CI]`, or
`[ENFORCED: review]`). No `[MAY]`, no `[INFO]`.
```

Нові твердження AGENTS.md про CI мусять мати `[ENFORCED: CI]`.

---

### `.github/pull_request_template.md` (optional, documentation)

Якщо планер додає згадку `gate` у Definition of Done — місце:

```markdown
## Definition of Done

- [ ] `pio run` is green for the affected environment
```

(`.github/pull_request_template.md:15-18`). Додавати рядок на кшталт
`- [ ] The required `gate` check is green`. Не переписувати решту чекліста.

---

### `docs/decisions/README.md` (optional, decision index)

AGENTS.md вимагає рядок на нове рішення. Топологія CI (D-1/D-2) — кандидат. Формат рядка:

```markdown
| 2026-10-26 | <decision> | <why> | <change cost> | accepted | — |
```

(шаблон із `docs/decisions/README.md:12-30`; колонки `Date | Decision | Why | Change cost | Status | Record`).
CONTEXT цього файлу не називає — вважати опційним, рішення за планером.

---

### `.yamllint.yaml` (optional, config)

Коментар рядків 12-17 каже «the four workflows are asserted to keep the textual `on:`». Після
фази workflow два. Оновити коментар; правило `truthy: {check-keys: false}` не чіпати (тест
`test_the_policy_relaxes_truthy_keys_and_keeps_boolean_values` його пінить).

---

## Shared Patterns

### 1. Піни екшенів за commit SHA з версійним коментарем
**Source:** `.github/workflows/homework.yml:20-22`, `security.yml:17-19`, `generated-views.yml:26-28`
**Apply to:** кожен `uses:` у `ci.yml` і `nightly.yml`

```yaml
      # Pinned to the v7.0.1 commit, not the mutable `v7` major tag: a tag can
      # be repointed at other code between runs, a commit SHA cannot.
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1  # v7.0.1
```

Нові екшени фази: `actions/upload-artifact@cf430e030ddbb5b0abf93d22962f4752f3646cd9  # v7.0.2`.

### 2. Мінімальні дозволи
**Source:** `.github/workflows/homework.yml:7-8`, `generated-views.yml:11-12`, `security.yml:9-10`
**Apply to:** обидва нові workflow

```yaml
permissions:
  contents: read
```

### 3. Concurrency
**Source:** `.github/workflows/homework.yml:10-12`
**Apply to:** `ci.yml` (nightly — не обов'язково; розклад рідко перетинається, але патерн
нешкідливий)

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

### 4. Зафіксований раннер і таймаут
**Source:** усі три workflow (`runs-on: ubuntu-24.04`)
**Apply to:** кожен job
`ubuntu-24.04` (не `ubuntu-latest`, Pitfall 16), `timeout-minutes` за D-19.

### 5. Checkout без кредитивів
**Source:** `.github/workflows/homework.yml:22-24`
**Apply to:** усі job-и, плюс `fetch-depth: 0` для `meta`/`changes`/nightly-gitleaks

```yaml
        with:
          persist-credentials: false
```

### 6. Shell-hardening і безпечна індирекція
**Source:** `.github/workflows/security.yml:29` (`set -euo pipefail`)
**Apply to:** кожен `run:` зі складом; недовірений ввід — лише через `env:` (Pitfall 10)

```yaml
        env:
          PR_TITLE: ${{ github.event.pull_request.title }}
          PROJECT: ${{ matrix.project }}
          ENV_NAME: ${{ matrix.env }}
        run: |
          set -euo pipefail
```

### 7. Коментар-обґрунтування
**Source:** `generated-views.yml:7-10, 21-23, 34-38`; `security.yml:25-26, 31-33, 39-40`;
`.pre-commit-config.yaml:1-9`
**Apply to:** кожен нетривіальний крок і job
Англійська, ідентифікатор рішення (`D-nn`), причина, інколи наслідок помилки.

### 8. Обмеження yamllint
**Source:** `.yamllint.yaml:1-19`; `.pre-commit-config.yaml:78-86` (hook `files` включає
`^\.github/workflows/`)
**Apply to:** обидва нові workflow
`line-length: {max: 120}`, тригер — текстове `on:`, `document-start` не потрібен. Нові файли
проходять `pre-commit run --all-files` у `meta` — тобто лінтуються тим самим хуком, який вони
ж і запускають.

---

## Немає аналога (планер бере з `08-RESEARCH.md`)

| Файл / частина | Role | Data Flow | Причина | Джерело патерну |
|---|---|---|---|---|
| `gate` job | workflow | fan-in aggregation | у репозиторії немає жодного агрегувального job-а | RESEARCH Pattern 1 |
| `simulate` job (guard, token, timeout, artifact) | workflow | event-driven + file-I/O | немає жодного job-а з секретом, `upload-artifact` чи Wokwi | RESEARCH Pattern 4, Code Examples |
| `nightly.yml` `schedule:` | workflow | batch | немає жодного scheduled workflow | RESEARCH Pattern 5 + GitHub syntax |
| `static-analysis` job | workflow | batch | clang-tidy живе лише в pre-push локально | RESEARCH Open Question 3, Code Examples |
| PR-title regex | workflow step | input validation | немає жодної bash-regex перевірки в CI | CONTEXT D-16 |
| `docs-build` job | workflow | file-I/O | **вхідні файли відсутні** (див. попередження вище) | — (потребує рішення) |
| `wokwi-cli` install із записаним SHA-256 | workflow step | file-I/O | KaTeX-ledger видалено разом із docs-сайтом; аналог залишився лише як inline-константа `GITLEAKS_SHA256` (`security.yml:24-27`) | RESEARCH Code Examples; inline-константа в workflow, без нового файлу-ledger |

**Рекомендація щодо digest `wokwi-cli`:** тримати його inline-константою в `ci.yml` за зразком
`GITLEAKS_SHA256` (`security.yml:24-27`) — окремий ledger-файл не має наразі аналога в дереві
(KaTeX ledger видалено), а новий файл розширив би scope фази.

---

## Metadata

**Analog search scope:** `.github/workflows/`, `scripts/`, `scripts/tests/`, `scripts/ci/`,
`AGENTS.md`, `.pre-commit-config.yaml`, `.yamllint.yaml`, `docs/decisions/`,
`homeworks/1_3-police-flasher/`, `tests/`
**Files scanned:** 18 (3 workflow, 6 scripts/test, 4 config/doc, 5 допоміжних)
**Tracked-source gate:** усі названі аналоги перевірені через `git ls-files` — усі tracked.
**Pattern extraction date:** 2026-10-26
**Known upstream drift:** `docs.yml`, `mkdocs.yml`, `requirements-docs.txt` видалено в `9d28f5d`;
кількість workflow у тесті — 3, не 4.
