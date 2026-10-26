---
phase: 08-fast-ci
reviewed: 2026-10-26T19:14:26Z
depth: standard
files_reviewed: 7
files_reviewed_list:
  - .github/pull_request_template.md
  - .github/workflows/ci.yml
  - .github/workflows/nightly.yml
  - .yamllint.yaml
  - AGENTS.md
  - docs/decisions/README.md
  - scripts/tests/test_ci_workflows.py
findings:
  critical: 1
  warning: 11
  info: 11
  total: 23
status: issues_found
---

# Phase 8: Code Review Report

**Reviewed:** 2026-10-26T19:14:26Z
**Depth:** standard
**Files Reviewed:** 7
**Status:** issues_found

## Summary

Перевірено сім змінених файлів фази: два робочі процеси GitHub Actions (`ci.yml`, `nightly.yml`), контрактний набір тестів `scripts/tests/test_ci_workflows.py`, політику yamllint, правило `AGENTS.md`, шаблон pull request і таблицю рішень. Структурний блок (`structural_findings`) не надавався, тому розділ структурних знахідок відсутній.

Позитивні результати перевірки, які варто зафіксувати як підтверджені факти:

- `uvx yamllint -c .yamllint.yaml .github/workflows/ci.yml .github/workflows/nightly.yml .yamllint.yaml` — без зауважень, попри `line-length: 120`.
- `uvx ruff@0.17.2 check scripts/tests/test_ci_workflows.py` — `All checks passed`.
- `npx markdownlint-cli2@0.24.0` на `AGENTS.md`, `.github/pull_request_template.md`, `docs/decisions/README.md` — 0 issues.
- `python3 -m unittest discover scripts/tests` — 332 тести, `OK`.
- Обидва закріплені дайджести збігаються з опублікованими артефактами: `wokwi-cli-linuxstatic-x64` v0.28.1 → `869f194e…bdd7`, `gitleaks_8.30.1_linux_x64.tar.gz` → `551f6fc8…70eb`.
- Усі чотири SHA екшенів існують у канонічних репозиторіях і відповідають заявленим тегам (`checkout v7.0.1`, `setup-python v7.1.0`, `cache v6.1.0`, `upload-artifact v7.0.2`); закріплені версії PyPI (`uv 0.13.5`, `pre-commit 4.7.0`, `platformio 6.2.0`, `cpp-linter-hooks 1.8.1`, `clang-tidy 23.1.3`) існують.
- Семантика шляхів `wokwi-cli` (`--scenario`/`--diagram-file` відносно позиційного каталогу проєкту) відповідає задокументованій команді та доказам Phase 7; регресії тут немає.

Головна проблема — крок сценарію симуляції не виконує власний контракт доказів (D-10 / T-8-23) на шляху помилки або таймауту: через успадкований `-e` скрипт завершується до запису `quota.json`. Решта знахідок — це переважно послаблення тестових гарантій (контрактні тести, які проходять на тексті з іншого job або на коментарях), дублювання закріплених блоків встановлення та кілька крайових випадків у workflow.

## Critical Issues

### CR-01: Крок сценарію втрачає `quota.json` і мапінг виходу на будь-якому ненульовому коді `wokwi-cli`

**File:** `.github/workflows/ci.yml:378-410`
**Класифікація:** BLOCKER
**Issue:** Крок `Run the scenario` починається з `set -uo pipefail` у припущенні, що це вимикає `-e`. Це не так: GitHub виконує `run:` під `bash -e` (або `bash -eo pipefail`), і `set -uo pipefail` лише додає `-u` та `pipefail`, не знімаючи `-e`. Оскільки крок сам вмикає `pipefail`, конвеєр `wokwi-cli … | tee …` повертає код `wokwi-cli`; за ненульового коду (1 — збій сценарію, 42 — таймаут) `-e` негайно завершує скрипт на рядку конвеєра. У результаті ніколи не виконуються `status=${PIPESTATUS[0]}`, `case`-мапінг `0/42/*`, `serial_bytes` і запис `quota.json`, а також `exit "$status"`. Це прямо суперечить коментарю в кроці («The exit status is recorded before it is returned, so a failed or timed-out run still produces its evidence»), D-10 і T-8-23, а також критерію приймання плану 08-03 («`quota.json` carries `exit_code` and `serial_log_bytes`»). Артефакт на шляху збою залишається неповним саме тоді, коли він потрібен для діагностики.

**Proof:**

```text
$ bash -e -c 'set -uo pipefail; (exit 42) | cat; echo REACHED'
$ echo "exit=$?"
exit=42            # REACHED не надруковано: -e перервав скрипт
```

**Fix:**

```bash
set -uo pipefail
out="$RUNNER_TEMP/simulation"
started=$(date +%s)
set +e                      # навмисно: код виходу збирається нижче
wokwi-cli "$PROJECT" \
  --timeout 15000 \
  --scenario scenario.yaml \
  --diagram-file assets/diagram.json \
  --serial-log-file "$out/serial.log" \
  2>&1 | tee "$out/stdout.log"
status=${PIPESTATUS[0]}
set -e
```

Додати контрактний тест, який перевіряє, що `set +e` стоїть між `set -uo pipefail` і викликом `wokwi-cli` у `simulate`, інакше регресія знову пройде зеленого.

## Warnings

### WR-01: `WOKWI_CLI_TOKEN` доступний кожному кроку job, включно з `pio run`, який виконує код з PR

**File:** `.github/workflows/ci.yml:306-307`, `.github/workflows/ci.yml:331-335`
**Класифікація:** WARNING
**Issue:** Токен оголошено на рівні job (`env: WOKWI_CLI_TOKEN: ${{ secrets.WOKWI_CLI_TOKEN }}`), тому він потрапляє в середовище всіх кроків, зокрема `Build the simulated firmware`. `pio run` виконує `extra_scripts`/SCons-скрипти з PR, тож гілка в тому самому репозиторії може прочитати токен під час збирання. Умова `head.repo.full_name == github.repository` звужує коло до гілок, які пушать колаборатори, але це ширше, ніж потрібно (T-8-11 вимагає лише «ніколи не друкувати», проте найменші привілеї тут дешеві).
**Fix:** прибрати job-level `env` і передати секрет лише двом крокам, які його потребують:

```yaml
      - name: Refuse to run without a token
        if: env.WOKWI_CLI_TOKEN == ''
        env:
          WOKWI_CLI_TOKEN: ${{ secrets.WOKWI_CLI_TOKEN }}
        run: |
          echo "::error::WOKWI_CLI_TOKEN is not configured; …"
          exit 1
```

```yaml
      - name: Run the scenario
        env:
          PROJECT: ${{ matrix.project }}
          ENV_NAME: ${{ matrix.env }}
          WOKWI_CLI_TOKEN: ${{ secrets.WOKWI_CLI_TOKEN }}
```

### WR-02: Крок завантаження артефакту запускається з порожнім `ARTIFACT_NAME`, якщо попередній крок упав

**File:** `.github/workflows/ci.yml:324-328`, `.github/workflows/ci.yml:357-370`, `.github/workflows/ci.yml:411-417`
**Класифікація:** WARNING
**Issue:** `ARTIFACT_NAME` записується лише в кроці `Prepare the evidence directory`, який стоїть після перевірки токена. Якщо токена немає (або підготовка каталогу падає), крок `upload-artifact` з `if: always()` все одно запускається, `name: ${{ env.ARTIFACT_NAME }}` розгортається в порожній рядок, і користувач бачить другу, оманливу помилку замість первинної причини.
**Fix:** дати безпечне значення за замовчуванням, наприклад `name: ${{ env.ARTIFACT_NAME || format('simulation-{0}', github.run_id) }}`, або обчислювати `ARTIFACT_NAME` до перевірки токена й додати тест на цей шлях.

### WR-03: Матриця `simulate` містить усі інструменти, крім `none`, а job завжди запускає `wokwi-cli`

**File:** `.github/workflows/ci.yml:302-303`; джерело даних — `scripts/affected.py` (`SIMULATE_OFF = ("none",)`), enum у `schema/homework.schema.json:62`
**Класифікація:** WARNING
**Issue:** Mapper додає до `simulate` кожен проєкт, у якого `simulation.tool != "none"`, тобто також `velxio`, `renode` і `fritzing`. Job `simulate` не бачить поля `tool` (у записі є лише `project`/`env`/`framework`) і безумовно викликає `wokwi-cli`. Щойно з'явиться homework із `tool: renode` або ілюстративним `fritzing`, помічена симуляція впаде на чужому емуляторі. Наразі єдиний homework має `tool: wokwi`, тому дефект латентний.
**Fix:** звузити `simulate` у mapper до `tool == "wokwi"` (найпростіше) або додати `tool` у кожен запис матриці й пропускати не-wokwi на рівні job; додати тест на mapper-рівні.

### WR-04: Nightly-запуск може бути зеленим із порожньою матрицею, не доводячи нічого

**File:** `.github/workflows/nightly.yml:42-53`, `.github/workflows/nightly.yml:65`
**Класифікація:** WARNING
**Issue:** Для PR-гейту умова `needs.changes.outputs.build != '[]'` коректна: PR із документацією нічого не збирає. Але той самий guard стоїть і в nightly, де порожня матриця означає, що «доказати все дерево» не вдалося. Якщо `affected.py` регресує й поверне `{"build": []}` для `platformio.shared.ini` (шлях widen-all), nightly завершиться зеленим, нічого не зібравши. Тест `test_nightly_computes_the_full_matrix` цього не ловить, бо перевіряє лише текст.
**Fix:** у кроці `Compute the full matrix` у `nightly.yml` явно вимагати непорожній масив:

```bash
printf '%s' "$payload" | jq -e '.build | length > 0' > /dev/null \
  || { echo "::error::the full-matrix mapper returned no build entries"; exit 1; }
```

### WR-05: `test_ci_grants_no_write_permission` обходиться формулюваннями `write-all` і `"write"`

**File:** `scripts/tests/test_ci_workflows.py:216-219`
**Класифікація:** WARNING
**Issue:** Перевірка `assertNotIn(": write", text)` не бачить `permissions: write-all` і `contents: "write"` (лапки розривають підрядок `: write`). `assertIn("contents: read", text)` не доводить відсутність інших дозволів. Це тест-гарантія для безпекового інваріанта, тому прогалина важлива.
**Fix:**

```python
self.assertNotIn("write-all", text)
self.assertNotIn('"write"', text)
self.assertNotIn(": write", text)
```

Краще — перевіряти кожен блок `permissions:` і дозволяти лише `contents: read` (без job-level `permissions:`).

### WR-06: `test_only_simulate_receives_a_secret` перевіряє лише текст до job `simulate`

**File:** `scripts/tests/test_ci_workflows.py:438-445`
**Класифікація:** WARNING
**Issue:** `before, marker, _ = self.text.partition("\n  simulate:\n")` і `assertNotIn("secrets.", before)` не бачить job, розташовані після `simulate` (зокрема `gate`), і взагалі не читає `nightly.yml`. Секрет, доданий у `gate` або в nightly, пройде тест.
**Fix:** пройтися по всіх `job_ids(self.text)` і вимагати відсутність `secrets.` у кожному блоці, крім `simulate`; окремо перевірити `NIGHTLY` (де секретів бути не повинно взагалі).

### WR-07: Блоки встановлення `gitleaks` і `wokwi-cli` продубльовані, а копії не перевіряються на однаковість

**File:** `.github/workflows/ci.yml:42-63`, `.github/workflows/ci.yml:100-114`, `.github/workflows/ci.yml:338-351`, `.github/workflows/nightly.yml:123-141`
**Класифікація:** WARNING
**Issue:** Блок `gitleaks` існує у двох файлах, блок `wokwi-cli` — у двох job одного файлу. Оновлення версії чи дайджесту в одній копії залишить іншу застарілою; `test_meta_pins_the_scanner_and_linter_versions` перевіряє лише копію в `meta`, а `test_nightly_carries_the_full_history_scan` не перевіряє версію/дайджест nightly взагалі. Оскільки це fail-closed перевірки цілісності артефактів, дрейф копій — реальний ризик.
**Fix:** винести встановлення у складену дію (`.github/actions/install-gitleaks`, `install-wokwi-cli`) або в `scripts/ci/install-*.sh` і додати тест, що обидва входження несуть однакові `VERSION`/`SHA256`; принаймні додати assertions для nightly-копії.

### WR-08: Два «контрактні» тести перевіряють весь файл, тому рядки `meta` задовольняють їх

**File:** `scripts/tests/test_ci_workflows.py:237-246`, `scripts/tests/test_ci_workflows.py:272-278`
**Класифікація:** WARNING
**Issue:** `test_static_analysis_restores_the_pre_commit_cache` шукає `path: ~/.cache/pre-commit` і ключ кешу в усьому `ci.yml`; ті самі рядки є в `meta`. Якщо `static-analysis` втратить кеш (регресія, яку тест мав ловити), тест лишиться зеленим. Аналогічно `test_simulation_pins_the_cli_and_maps_exit_codes` шукає `"0.28.1"` і `WOKWI_CLI_SHA256` в усьому файлі — їх задовольняє блок `meta`, навіть якщо `simulate` втратить власне встановлення CLI.
**Fix:** звузити обидва тести до відповідного job через `job_block(self.text, "static-analysis")` / `job_block(self.text, "simulate")`.

### WR-09: `test_nightly_computes_the_full_matrix` проходить на коментарях і ключі кешу

**File:** `scripts/tests/test_ci_workflows.py:280-285`
**Класифікація:** WARNING
**Issue:** Тест перевіряє `"uv run scripts/affected.py --paths-from"` і `"platformio.shared.ini"` у всьому файлі. `platformio.shared.ini` зустрічається в nightly у коментарі (рядки 46-48) і в ключі кешу (рядок 87), тому навіть якщо крок `Compute the full matrix` втратить файл `--paths-from`, тест може залишитися зеленим.
**Fix:** відкинути коментарі (як це вже роблять інші тести), взяти `job_block(NIGHTLY, "changes")` і перевірити точний рядок `printf 'platformio.shared.ini\n' > "$RUNNER_TEMP/all-paths.txt"` та `--paths-from "$RUNNER_TEMP/all-paths.txt"`.

### WR-10: Тест пінів перевіряє лише перші 8 символів SHA-256

**File:** `scripts/tests/test_ci_workflows.py:349-353`
**Класифікація:** WARNING
**Issue:** `for pin in (…, "551f6fc8", …, "869f194e")` перевіряє префікси, тому зміна будь-якого з решти 56 hex-символів у дайджесті не буде помічена. Для fail-closed перевірки цілісності бінарника це слабка гарантія.
**Fix:** перевіряти повні 64-символьні дайджести і обидва входження `WOKWI_CLI_SHA256` (див. WR-07).

### WR-11: Контракт `gate` не забороняє `continue-on-error`

**File:** `scripts/tests/test_ci_workflows.py:380-399`
**Класифікація:** WARNING
**Issue:** Клас `CiWorkflowContractTests` заявлений як захист від «тихого розблокування merge», але не перевіряє відсутність `continue-on-error: true` на job або кроці `gate`. З цим ключем крок `gate` може впасти на `jq`-перевірці, а job усе одно завершиться успішно, і єдина обов'язкова перевірка стане зеленою.
**Fix:** додати `self.assertNotIn("continue-on-error", job_block(self.text, "gate"))`.

## Info

### IN-01: `step_block` не відповідає власному docstring і не знаходить крок без `name:`

**File:** `scripts/tests/test_ci_workflows.py:42-64`
**Issue:** Docstring обіцяє пошук за `- name:` **або** `- uses:`, реалізація шукає лише `- name: {name}`; повідомлення про помилку жорстко згадує `ci.yml`, хоча хелпер міг би працювати з будь-яким workflow.
**Fix:** або реалізувати пошук `- uses:`, або виправити docstring; параметризувати назву файлу.

### IN-02: `test_every_workflow_declares_a_textual_trigger_key` жорстко фіксує кількість workflow

**File:** `scripts/tests/test_ci_workflows.py:476-482`
**Issue:** Назва говорить «every workflow», а тіло вимагає рівно два файли (`assertEqual(2, len(files))`). Додавання легітимного третього workflow зламає тест із повідомленням, не пов'язаним з інваріантом `on:`.
**Fix:** прибрати перевірку кількості або замінити її на явний список очікуваних імен із зрозумілим повідомленням.

### IN-03: Docstring модуля описує неповний склад `ci.yml`

**File:** `scripts/tests/test_ci_workflows.py:1-13`
**Issue:** Перелічено `meta`, `changes`, `build` і `gate`, але пропущено `python-tests`, `static-analysis` і `simulate`.
**Fix:** оновити опис, щоб він відповідав семи job-ам, які реально існують.

### IN-04: Магічне число 15 дублює `--timeout 15000`

**File:** `.github/workflows/ci.yml:381`, `.github/workflows/ci.yml:399`
**Issue:** Таймаут сценарію задано в мілісекундах, а верхня межа в `quota.json` — окремою константою `15`; при зміні одного значення інше мовчки розійдеться.
**Fix:** задати `SCENARIO_TIMEOUT_MS: 15000` у `env:` кроку, використати `--timeout "$SCENARIO_TIMEOUT_MS"` і `--argjson simulated_seconds_upper_bound "$((SCENARIO_TIMEOUT_MS / 1000))"`.

### IN-05: Тести LFS-охоронця покривають скрипт, який більше ніхто не викликає

**File:** `scripts/tests/test_ci_workflows.py:31`, `scripts/tests/test_ci_workflows.py:143-189`; `scripts/ci/check_lfs_pointers.sh`
**Issue:** Після вилучення сайту єдиний виклик `check_lfs_pointers.sh site` зник; файл лишився сиротою (це вже зафіксовано в `08-PATTERNS.md:33`), але його тести в контрактному наборі створюють враження, що LFS-захист сторінки все ще діє. Дефект не внесений цією фазою, але тестовий файл у межах рев'ю.
**Fix:** або видалити скрипт і його тести, або додати короткий коментар у тесті/документації, що охоронець збережений для майбутнього повернення сайту і зараз не підключений.

### IN-06: `AGENTS.md` називає команду quick-start «точною» командою CI, хоча CI додає прапорець

**File:** `AGENTS.md:23`, `.github/workflows/ci.yml:95`
**Issue:** Локально задокументовано `pre-commit run --all-files`, а `meta` виконує `pre-commit run --all-files --show-diff-on-failure`.
**Fix:** додати прапорець у `AGENTS.md` або прибрати слово «exact».

### IN-07: Definition of Done у шаблоні PR не згадує Python-набір, який тепер блокує merge

**File:** `.github/pull_request_template.md:12-19`
**Issue:** Новий job `python-tests` входить у `gate`, але чекліст не містить `python -m unittest discover scripts/tests`; пункт «required gate check is green» покриває це лише опосередковано.
**Fix:** додати пункт `- [ ] \`python -m unittest discover scripts/tests\` passes` (або еквівалент) для узгодженості з `AGENTS.md` quick-start.

### IN-08: Збій `jq` у `changes` може тихо записати порожній вихід і пропустити збірку

**File:** `.github/workflows/ci.yml:157-158`, `.github/workflows/nightly.yml:53`
**Issue:** `printf 'build=%s\n' "$(printf '%s' "$payload" | jq -c .build)"` не перериває крок, якщо падає саме `jq`: під `set -e` статус команди визначає `printf` (0), тому у `$GITHUB_OUTPUT` потрапляє `build=`, а guard `!= ''` тихо пропускає job. Перевірено: `bash -e -c 'printf "build=%s\n" "$(false)"; echo after'` друкує `build=` і продовжує. Зараз `affected.py` завжди віддає валідний JSON, тому ймовірність низька, але це шлях до хибно-зеленого результату.
**Fix:** спершу присвоїти й перевірити статус:

```bash
build="$(printf '%s' "$payload" | jq -c .build)" \
  || { echo "::error::affected.py produced no build array"; exit 1; }
printf 'build=%s\n' "$build" >> "$GITHUB_OUTPUT"
```

### IN-09: Job id `secrets` у nightly збігається з назвою контексту

**File:** `.github/workflows/nightly.yml:107-112`
**Issue:** `secrets:` як ідентифікатор job легальний, але читається як контекст `secrets` і ускладнює `needs.*`-навігацію та майбутній fan-in.
**Fix:** перейменувати на `secret-scan` (або `gitleaks`) і оновити `test_nightly_declares_the_full_matrix_job_set`.

### IN-10: Зняття мітки `simulate` не перезапускає workflow

**File:** `.github/workflows/ci.yml:11`, `.github/workflows/ci.yml:292`
**Issue:** `labeled` додано, а `unlabeled` — ні. Якщо мітку зняти під час запуску, попередній запуск (з конкуренцією за той самий `ref`) не скасовується новим запуском, і симуляція може витратити квоту попри те, що мітку знято.
**Fix:** додати `unlabeled` до `types:` (тоді новий запуск скасує попередній) або задокументувати, що зняття мітки не впливає на вже запущений job.

### IN-11: Регулярний вираз заголовка приймає subject із самих пробілів

**File:** `.github/workflows/ci.yml:74`
**Issue:** `: .+$` пропускає `feat(08): ` (пробіл як subject), хоча перевірка має гарантувати змістовний опис.
**Fix:** `: [^[:space:]].*$` (або `\S`).

---

_Reviewed: 2026-10-26T19:14:26Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
