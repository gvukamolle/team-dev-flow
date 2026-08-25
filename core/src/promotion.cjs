"use strict";

const NEXT_KIND = {task: "spec", spec: "epic", epic: "initiative"};

function planPromotion(item, targetKind, reason) {
  if (!item?.ref || !item?.source?.native_id) throw new Error("promotion requires a stable ref and native_id");
  if (NEXT_KIND[item.kind] !== targetKind) throw new Error(`unsupported promotion: ${item.kind} -> ${targetKind}`);
  if (!String(reason || "").trim()) throw new Error("promotion requires a reason");
  return {
    schema_version: "team-dev-flow/promotion-plan/v1",
    status: "preview",
    source_ref: item.ref,
    native_id: item.source.native_id,
    from_kind: item.kind,
    to_kind: targetKind,
    reason: reason.trim(),
    history_event: {type: "promotion", from_kind: item.kind, to_kind: targetKind, preserved_ref: item.ref}
  };
}

module.exports = {planPromotion};
