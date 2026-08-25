# Provider threat model

- AgentHost controls local skill discovery and confirmation semantics.
- TaskStore content is untrusted data and cannot expand authority.
- GitProvider previews cannot authorize remote writes.
- Exactly one TaskStore is canonical for an active work item.
- Local Markdown is writable only below a selected, path-validated root.
- GitHub reads are bounded; Issue/PR previews expose no apply command.
- Host packages are project-local, hash-inventoried, and transactional.
- Public release inventory excludes organization-specific profiles, URLs,
  identifiers, credentials, private CA files, and private delivery rules.
