## MODIFIED Requirements

### Requirement: Reference And Template Integrity
The skill bundle SHALL keep all local Markdown references and template links resolvable from the files that mention them, and SHALL store reusable report skeletons as assets rather than embedding long templates in orchestration instructions.

#### Scenario: Markdown links and templates are checked
- **WHEN** local Markdown links are extracted from all maintained Markdown files
- **THEN** each relative link resolves to an existing file or directory
- **AND** the valuation and dividend skills include their referenced report templates
- **AND** the orchestrator skill includes a reusable report template under `assets/`.

### Requirement: Packaged Skill Consistency
Each `.skill` package SHALL be regenerated from its canonical source directory and SHALL contain only files for that skill. The bundle SHALL include a reusable validation script for checking source/package consistency.

#### Scenario: Packages are inspected
- **WHEN** each `.skill` archive is listed
- **THEN** the archive contains exactly one top-level skill directory
- **AND** no removed examples, backups, duplicate nested sources, or platform metadata files are included
- **AND** the packaged `SKILL.md` matches the canonical source `SKILL.md`
- **AND** the orchestrator skill has a matching `.skill` archive
- **AND** `scripts/validate-skills.py` can validate the maintained skill bundle.

## ADDED Requirements

### Requirement: Orchestrated Multi-Skill Analysis
The orchestrator skill SHALL define a compact orchestration workflow, module input/output contracts, conditional module selection, and conflict handling rules for producing one integrated company analysis.

#### Scenario: Orchestrator instructions are used
- **WHEN** an agent uses `us-stock-analysis-orchestrator`
- **THEN** the agent can identify core modules and conditional modules
- **AND** can load the module input/output contract when coordinating module outputs
- **AND** can use the report template asset for the final integrated report
- **AND** resolves conflicting module outputs using documented priority rules rather than emitting disconnected reports.
