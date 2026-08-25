# Contract versioning and migration

Machine contracts use explicit identifiers such as `team-dev-flow/work-item/v1`. A stable released schema is immutable: an incompatible required field, removed value, changed meaning, or narrowed constraint requires a new major contract identifier.

Additive optional fields may remain in the same contract version when older consumers can safely ignore them. Pre-release package schemas may still change before stable promotion, but the changelog must call this out and fixtures must be regenerated.

Readers should accept the current version and the immediately preceding stable version where a compatibility adapter exists. Writers emit only the current version. Migrations are pure and previewable: validate the input, preserve stable refs and native metadata, produce a new artifact, record source/target versions and hashes, validate the output, then replace only under the selected TaskStore authority.

Unknown versions fail closed with a message that names the supported versions. Silent field dropping, in-place semantic reinterpretation, and unversioned fallback are forbidden. Package rollback restores the prior runtime and schemas; it does not reverse already applied external mutations.
