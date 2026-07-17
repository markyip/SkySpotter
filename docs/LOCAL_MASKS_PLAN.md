# Local Masks: Brush / Gradient Masks with Per-Mask Adjustments (Design Draft)

Status: **draft / future development** — not implemented.
Scope: generalize the existing dodge & burn mask into a list of *local mask
groups* (brush, linear gradient, radial gradient), each carrying its own
subset of adjustment values applied as mask-weighted corrections.

This is the Lightroom-style "local corrections" model (tier 1 from the
feasibility review): locals are **weighted deltas inserted at one pipeline
point**, not a second full render. One pass, one extra stage-cache slot,
N masks cost N cheap weighted ops — never N pipeline runs.

---

## 1. Mask model

Extend the existing `raw_dodge_burn.DodgeBurnMask` concept into a typed mask:

```python
@dataclass
class LocalMask:
    mask_id: str                  # stable uuid4 hex, used in XMP + UI list
    mask_type: str                # "brush" | "linear" | "radial"
    invert: bool = False          # weight -> 1 - weight
    # brush: painted bitmap (reuses DodgeBurnMask storage + edge snap)
    bitmap: Optional[DodgeBurnMask] = None
    # linear: normalized image coords (0..1), feather in fraction of span
    p0: tuple[float, float] = (0.0, 0.0)   # weight = 1 side
    p1: tuple[float, float] = (0.0, 0.0)   # weight = 0 side
    # radial: normalized center / radii / rotation, feather 0..1
    center: tuple[float, float] = (0.5, 0.5)
    radius_x: float = 0.25
    radius_y: float = 0.25
    angle_deg: float = 0.0
    feather: float = 0.5
    adjustments: dict[str, float] = field(default_factory=dict)  # local keys only
```

- **Brush** masks keep the current base64-PNG bitmap serialization,
  `resize_mask_to` rescaling, edge-assist stamping, and release-time
  guided-filter snap — unchanged code paths.
- **Linear / radial** masks are *procedural*: rasterized on demand at the
  working resolution from their parameters (a few floats). Smoothstep
  falloff across the feather band; radial rasterizes an ellipse in a
  rotated frame. Rasterization is O(H×W) numpy, cached per
  (mask params, H, W) exactly like the current `_gain_cache`.
- `invert` gives inside/outside asymmetry for free (outside = global
  settings, inside = global + delta; inverting flips which side the
  delta lands on).

## 2. Local adjustment keys

Locals are a curated subset (matches Lightroom locals and keeps every
correction expressible as a cheap weighted op in linear RGB):

| Key (per mask)        | Applied as                                              |
|-----------------------|---------------------------------------------------------|
| `LocalExposure`       | `img *= 2 ** (w * stops)` (exactly today's dodge/burn)  |
| `LocalContrast`       | mask-weighted pivot contrast around mid-gray            |
| `LocalTemperature` / `LocalTint` | mask-weighted WB channel gains (lerp of 3×1 gain vector) |
| `LocalSaturation`     | mask-weighted lerp toward per-pixel luma                |
| `LocalClarity`        | mask-weighted unsharp on the luma midtones              |
| `LocalDehaze`         | mask-weighted blend of `raw_effects.apply_dehaze` delta |
| `LocalShadows` / `LocalHighlights` | mask-weighted tone-range lift/recovery     |

Per-region tone curves / LUTs are explicitly **out of scope** (they would
force the dual-pipeline tier 2 model).

## 3. Pipeline insertion

One new stage in `raw_edit_pipeline._process_linear_edit_tail`, at the
point where dodge & burn is applied today (after global Exposure, before
denoise/tone — local brightness must see the same noise/tone response as
global exposure):

```
pre_tone  ->  [ local_corrections ]  ->  tone  ->  tonemap  ->  color  ->  detail
```

- `local_corrections(img, masks, h, w)` iterates the mask list; for each
  mask: get (cached) weight map at (h, w), apply that mask's non-zero
  local keys as weighted ops. Empty list = exact no-op (guaranteed
  byte-identical output when no masks exist — protects all existing
  golden-parity tests).
- Dodge & burn migrates to become the first citizen: a `brush` mask whose
  only key is `LocalExposure` (its Strength slider). Legacy
  `_dodge_burn_mask_v1` XMP is read and converted on load; writing keeps
  the legacy element for one release for backward compatibility.

### Stage-cache integration

`_EditStageCache` gains one slot:

- `local_key = tuple(sorted((m.mask_id, m.fingerprint(), tuple(sorted(m.adjustments.items()))) for m in masks))`
  where `fingerprint()` is the bitmap PNG hash (brush) or the rounded
  param tuple (gradients).
- Cache chain: `pre_tone -> local -> tone -> ...`; editing a local slider
  invalidates from `local` down but keeps the (expensive) `pre_tone`
  demosaic/geometry output. Editing a global pre-tone slider invalidates
  `local` implicitly via the chained key, as today.
- Live drag of a local slider uses the existing preview-lite downsampled
  base; per-mask weight maps at preview size are tiny (float32, ~2–8 MB).

## 4. XMP schema

Nested under the existing `rdf:Description` (namespace `crs`, same file,
same atomic-write path). Modeled after Adobe's
`crs:MaskGroupBasedCorrections` but kept minimal and app-owned:

```xml
<crs:LocalMaskGroups>
  <rdf:Seq>
    <rdf:li>
      <rdf:Description
          crs:MaskID="9f2c1a…"
          crs:MaskType="radial"           <!-- brush | linear | radial -->
          crs:MaskInvert="False"
          crs:CenterX="0.46" crs:CenterY="0.31"
          crs:RadiusX="0.22" crs:RadiusY="0.14"
          crs:Angle="12.0" crs:Feather="0.55"
          crs:LocalExposure="0.65"
          crs:LocalTemperature="-350.0"
          crs:LocalSaturation="12.0"/>
    </rdf:li>
    <rdf:li>
      <rdf:Description
          crs:MaskID="c81d0b…"
          crs:MaskType="brush"
          crs:MaskInvert="False"
          crs:LocalExposure="-0.40">
        <crs:MaskBitmap>base64-PNG…</crs:MaskBitmap>  <!-- same encoding as DodgeBurnMask -->
      </rdf:Description>
    </rdf:li>
  </rdf:Seq>
</crs:LocalMaskGroups>
```

Rules:

- Gradient masks persist **parameters only** (resolution-independent,
  ~200 bytes); brush masks persist the PNG blob as a child element,
  mirroring `crs:DodgeBurnMask` handling in `_write_xmp_adjustments_locked`.
- Numeric local keys are attributes; only bitmaps are child elements.
- Unknown attributes are ignored on read (forward compatibility).
- `prepare_adj_for_export` treatment mirrors the existing mask
  fingerprint substitution: workers/sidecars see fingerprints, never
  re-serialize blobs per keystroke.
- `is_default_adjustments` returns False when any mask group has a
  non-empty local key; `adjustments_equal` compares the group list.

## 5. UI plan

- **Panel**: new "Masking" `CollapsibleSection` with a mask list
  (pattern: the Creative LUT `QListWidget`) + "Add Brush / Linear /
  Radial" buttons. Selecting a mask expands its local sliders
  (reuse `SLIDER_SPECS`-style rows scoped to the selected mask).
- **On-image gizmos** (pattern: `crop_overlay.CropOverlayItem`):
  - Linear: two draggable endpoints + feather band lines.
  - Radial: center + two radius handles + rotation handle.
  - Brush: existing D&B brush path (size/flow/edge-assist controls move
    under the selected brush mask).
- Mask overlay visualization: reuse the red D&B mask overlay
  (`set_dodge_burn_mask_overlay`) generalized to "show selected mask".
- Mutual exclusion with crop mode via the existing
  `set_crop_mode` / `set_dodge_burn_mode` interlocks.

## 6. Delivery phases

1. **Phase 1 — plumbing**: `LocalMask` model, XMP read/write, pipeline
   stage + cache slot, D&B migrated onto it. No new UI. Golden-parity
   test: zero masks ⇒ byte-identical output.
2. **Phase 2 — radial + linear gizmos**: procedural rasterizer, overlay
   items, panel list with `LocalExposure`/`LocalTemperature`/
   `LocalSaturation` only.
3. **Phase 3 — full local key set + invert + multiple masks**, perf
   marks (`local_apply` in `perf_metrics`), docs.

Out of scope (would require tier-2 dual pipeline): per-mask tone curves,
per-mask LUTs, luminance/color-range auto-masks (AI subject masks could
later rasterize into a `brush` bitmap without schema changes).

## 7. Test plan

- `testplan/auto/t_local_masks.py`: rasterizer correctness (gradient
  values at endpoints/feather midpoint), invert, XMP round-trip
  (params + bitmap), no-mask parity vs current pipeline output,
  cache-key invalidation on param change.
- Extend `t_dodge_burn.py` to run through the migrated path.
