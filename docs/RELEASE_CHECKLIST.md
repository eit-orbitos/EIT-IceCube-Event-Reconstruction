# Release and scientific promotion gates

**Package identity:** EIT_ICECUBE_EVENT_RECONSTRUCTION_V0.1.2 / version 0.1.2.

**Immediate predecessor:** V0.1.1 exact unchanged SHA-256
`8dc859001db30a6298090c6d3f8f6a5233061babfda1808eed4b01e65d7f977f`.
Original V0.1 `e89c2b211044392457edb50682e8b65391b3c3dbdc9692d91b6785abac93c935`
is also preserved. This candidate changes license/metadata/version only.

**Before any approval:** `ENGINEERING_CANDIDATE` / `NOT_FROZEN` / `NOT_SCIENTIFICALLY_VALIDATED` / `GITHUB_HOLD` / `ZENODO_BLOCKED`. Local verification is *not* independent review. Author approval must be explicit and recorded outside the immutable ZIP. This new package cannot change RC3 status or hashes.

## Required engineering checks

- [ ] All local tests pass (count comes from external verification evidence).
- [ ] Current benchmark JSON exactly matches `examples/reference_results.json`.
- [ ] Source file SHA256SUMS complete and passes, with exact count.
- [ ] Manifest file count, content sizes and SHA-256 hashes match.
- [ ] ZIP central directory CRC, safe paths and fixed metadata validated.
- [ ] Two independently generated local archives are BYTE_IDENTICAL (within same runtime).
- [ ] ZIP SHA-256 stored outside ZIP, unambiguously tied to the candidate version.
- [ ] Confirm F-1 near-coplanar rejection and strict F-2 bool rejection remain functional in V0.1.2.
- [ ] Verify post-hoc negative-control output byte-for-byte and document residual risks.
- [ ] Independent code, packaging and license-metadata audit of the unmodified
  exact **V0.1.2** ZIP (V0.1.1 audits are NOT transferable to new bytes).

## Additional gates before publishing

- [x] Author selected **PolyForm-Noncommercial-1.0.0** for this candidate
      in conversation on 2026-11-03; this is not consent to freeze/publish.
- [ ] Independently verify LICENSE, CITATION.cff, .zenodo.json and source
      package consistently name PolyForm Noncommercial 1.0.0 (not MIT).
- [ ] Confirm no attempt to revoke previously granted MIT rights for old copies.
- [ ] Verify affiliation before adding EIT Networks LLC to any publication metadata.
- [ ] Conceptual author separately authorizes public release.
- [ ] Verify whether GitHub org/repo already exists and correct permissions; do not overwrite RC3 or other artifacts.
- [ ] Decide to freeze **this exact ZIP** by author statement; store SHA and decision **out of band**.
- [ ] Only then tag a release, link Zenodo GitHub integration, publish an archive/DOI.
- [ ] Any changes after release create a *new version*, with no silent editing of frozen archive.

## Separate scientific gates (NOT met by V0.1.2)

- [ ] Validate on appropriately licensed, suitable real or physics-simulated pulse-level data (not only IceTracks-DR2 event summaries).
- [ ] Detector calibration, physically relevant observation model and proven evaluation labels.
- [ ] Compare to appropriate real reconstruction methods and test multiple seeds/domain shifts.
- [ ] Independently review estimates, uncertainty coverage and failure modes.

**Rule:** `BYTE_IDENTICAL` means matching bytes. It does not mean that a reconstruction is scientifically correct, novel or independently accepted.

**Licensing gate:** Publicly accessible source is not the same as OSI open source. PolyForm Noncommercial restricts commercial use; check Zenodo record license metadata before DOI creation.
