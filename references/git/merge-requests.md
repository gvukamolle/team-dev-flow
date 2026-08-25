# Pull request / merge request handoff

Bind every handoff to the exact full source SHA and include:

- accepted TaskStore ref and source revision;
- Spec and Task Contract versions/hashes;
- concise scope and non-goals;
- validation commands and results;
- unresolved risks or explicitly unverified surfaces;
- review findings and dispositions at the same SHA;
- rollout and rollback notes when relevant.

A new commit invalidates prior exact-SHA verification/review. Creating or merging
a PR/MR, changing branch protection, releasing, or deploying requires separate
target-specific authority.
