## ADDED Requirements

### Requirement: Skill Source Structure
The skill bundle SHALL contain one canonical source directory for each shipped skill and SHALL exclude generated examples, backups, duplicate nested skills, empty placeholder directories, and platform metadata files from the maintained source set.

#### Scenario: Maintained source tree is inspected
- **WHEN** the skill bundle is scanned
- **THEN** each shipped skill has exactly one source directory containing `SKILL.md`
- **AND** no duplicate nested skill directories, `.DS_Store`, `.bak`, ABCL example data, ABCL example reports, or empty placeholder directories remain.

### Requirement: Trigger Metadata
Each `SKILL.md` SHALL keep its existing `name` and use a concise `description` that starts with `Use when`, describes trigger conditions only, and stays below 1024 bytes.

#### Scenario: Frontmatter is validated
- **WHEN** all `SKILL.md` files are parsed
- **THEN** each frontmatter has `name` and `description`
- **AND** the `name` values match the existing skill names
- **AND** every `description` starts with `Use when`
- **AND** no `description` exceeds 1024 bytes.

### Requirement: Reference And Template Integrity
The skill bundle SHALL keep all local Markdown references and template links resolvable from the files that mention them.

#### Scenario: Markdown links are checked
- **WHEN** local Markdown links are extracted from all maintained Markdown files
- **THEN** each relative link resolves to an existing file or directory
- **AND** the valuation and dividend skills include their referenced report templates.

### Requirement: Packaged Skill Consistency
Each `.skill` package SHALL be regenerated from its canonical source directory and SHALL contain only files for that skill.

#### Scenario: Packages are inspected
- **WHEN** each `.skill` archive is listed
- **THEN** the archive contains exactly one top-level skill directory
- **AND** no removed examples, backups, duplicate nested sources, or platform metadata files are included
- **AND** the packaged `SKILL.md` matches the canonical source `SKILL.md`.

### Requirement: Data Integrity Guardrails
The skill text SHALL keep explicit guardrails against fabricated market, financial, quote, source, or date data.

#### Scenario: Skills guide investment analysis
- **WHEN** an agent uses any shipped skill to produce investment analysis
- **THEN** the skill requires sources and dates for factual data
- **AND** requires unavailable data to be marked as unavailable rather than estimated
- **AND** requires assumptions and forward-looking statements to be explicitly labeled.
