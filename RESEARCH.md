# Research — tar-link-boundary

Observed 13 October 2026 on live GitHub. Demand is inferred from documented workflows and public issues, not a verified request for this product. Only the first page of each star-sorted problem search was reviewed; this is not an exhaustive global ranking. Broad unrelated results were excluded. Stars are discovery signals, not technical performance evidence.

## User and acceptance

A developer reviewing a downloaded source/archive before choosing an extractor.

Pain: Trace ordered TAR symlink/hardlink boundary hazards without extracting files.

Smallest useful capability and acceptance: A symlink a→.. followed by a/secret produces two hazards and an explicit link chain; inward links resolve; parent segments are applied after link traversal; cycles terminate; hardlink forward references, duplicate names, non-directory parents and special/platform paths are flagged; malformed TAR fails without extracting.

## Observed alternatives

| Repository | Stars | Last push (UTC) | Status / detected license |
| --- | ---: | --- | --- |
| [peazip/PeaZip](https://github.com/peazip/PeaZip) | 7961 | 2026-10-07T14:06:49Z | active repository / LGPL-3.0 |
| [mholt/archiver](https://github.com/mholt/archiver) | 4374 | 2024-11-19T16:52:17Z | archived / MIT |
| [libarchive/libarchive](https://github.com/libarchive/libarchive) | 3636 | 2026-10-13T02:02:39Z | active repository / NOASSERTION |

Query: `tar archive`; [GitHub search, Most stars](https://github.com/search?q=tar%20archive&type=repositories&s=stars&o=desc). Exact observed queries, stars and push dates are recorded above. Highest-star relevant result on that page: peazip/PeaZip. Other established workflow alternatives were reviewed even if they were not on that first page.

PeaZip is a desktop archive manager; libarchive is a mature multi-format C library/CLI with secure symlink extraction flags visible in archive_write_disk_posix.c. mholt/archiver is archived and explicitly redirects users to mholt/archives. This tool has a narrow metadata-only ordered virtual path trace. Mature extractors have stronger actual filesystem handling; the model cannot certify any of them or replace secure extraction.

## Differentiation and discovery

Owned oci-whiteout-plan models container-layer deletion semantics; this models ordered link-boundary hazards in an actual uncompressed archive and never extracts. Discover through defensive source-archive review examples.

## Fair comparison boundary

Docs, relevant source and accessible issue collections were inspected. No comparator was installed or timed on equivalent workloads; therefore no install-speed, reliability or performance superiority is claimed. A passing example proves our documented behavior only. No external code was reused; comparator licenses above are API-detected labels, not a legal determination. Support and licensing follow each upstream repository; this alpha offers MIT source and best-effort issue support.
