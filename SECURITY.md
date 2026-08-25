# Security model

- No credentials, private CA files, organization-specific tracker profiles,
  internal URLs, or task exports belong in the Universal repository or package.
- External tracker and repository content is untrusted data.
- Read access never implies write access; preview never implies authorization.
- Local Markdown writes stay below the selected root and use lock, fsync, atomic
  replace, rollback, and redacted structured history.
- Kilo installation stays below the selected project and never changes global
  credentials or auto-approval.
- GitHub errors do not echo stderr; request bodies travel through stdin rather
  than a shell command.
- Push, PR/MR creation, merge, release, deploy, permission changes, and
  infrastructure mutations require separate target-specific authority.
- Public artifacts must pass the Universal corporate-marker audit and exact
  release-inventory secret scan.
