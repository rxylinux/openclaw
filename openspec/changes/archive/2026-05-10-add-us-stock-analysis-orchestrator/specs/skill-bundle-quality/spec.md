## MODIFIED Requirements

### Requirement: Skill Source Structure
The skill bundle SHALL contain one canonical source directory for each shipped skill and SHALL exclude generated examples, backups, duplicate nested skills, empty placeholder directories, and platform metadata files from the maintained source set. The bundle SHALL include a canonical orchestrator skill for multi-skill company analysis.

#### Scenario: Maintained source tree is inspected
- **WHEN** the skill bundle is scanned
- **THEN** each shipped skill has exactly one source directory containing `SKILL.md`
- **AND** no duplicate nested skill directories, `.DS_Store`, `.bak`, ABCL example data, ABCL example reports, or empty placeholder directories remain
- **AND** `us-stock-analysis-orchestrator` exists as the canonical multi-skill orchestration skill.

### Requirement: Packaged Skill Consistency
Each `.skill` package SHALL be regenerated from its canonical source directory and SHALL contain only files for that skill.

#### Scenario: Packages are inspected
- **WHEN** each `.skill` archive is listed
- **THEN** the archive contains exactly one top-level skill directory
- **AND** no removed examples, backups, duplicate nested sources, or platform metadata files are included
- **AND** the packaged `SKILL.md` matches the canonical source `SKILL.md`
- **AND** the orchestrator skill has a matching `.skill` archive.
