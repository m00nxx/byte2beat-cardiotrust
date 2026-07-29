# Data Provenance and Publication Gate

Acquisition date: 2026-07-27

Host resource folder:
`https://drive.google.com/drive/folders/1oTqMR3AM3FGjnAXPZZuqDLH7D4rcOhNb`

Dataset subfolder:
`https://drive.google.com/drive/folders/11Zg88-KbQO1xbTSAuCnqqMps6Qyuscf4`

## Local files

| Host file | Drive file ID | Bytes | SHA-256 |
|---|---|---:|---|
| `cardio_base.csv` | `1_pcIRUWpHoUNkiHcDK01HlLkOOMXi9hn` | 2,941,524 | `21A705D23381B0DFD6A6416DA701B490744F1FC3B47E9FF3DB3968C420FFA10C` |
| `cardiac_failure_processed.csv` | `1NBL96uw95T5nhH2_bncc-jvVEOp6_Mjn` | 4,258,225 | `75A4992191C8B8E59D62526501A30355FE0172B430E75939266F1A2967C9B6EB` |
| `heart_processed.csv` | `1mopCa200spbeFRFpkr_ppuLbqsdl0BaR` | 67,363 | `9C33F2F81E1DE3087F13B6757AC7834B53C709238948C089FC433C0DFABE116E` |

The host also supplies `ecg_timeseries.csv` (approximately 627 MB, Drive ID
`1MFOoFkk_ypdbH2jvPXU7YWiNDlvPd-en`). It was not downloaded.

## Primary dataset mapping

`cardio_base.csv` has 70,000 rows and the same 13-column schema, category
encodings, target, size class, and visible preview records as:

`https://www.kaggle.com/datasets/sulianova/cardiovascular-disease-dataset`

This is strong evidence that the host file is derived from that dataset, but it
is not a byte-level upstream identity proof. The host Drive does not state the
original collector, collection sites, dates, consent basis, or license.

On 2026-07-27, the upstream Kaggle Data Card displayed:

- author: Svetlana Ulianova
- 70,000 patient records, 11 features plus target
- license: `Unknown`
- expected update frequency: not specified

## Publication decision

**NO-GO for dataset redistribution.**

The source license is not established. A third-party cleaned derivative marked
CC0 is not sufficient evidence that the upstream source or the host copy is
CC0. Until the owner or host provides a valid license:

- do not commit raw or transformed row-level data
- do not attach the data to a public notebook or repository
- do not claim permission based on availability alone
- review trained-model publication separately

Aggregated metrics and plots are retained locally for research and competition
preparation. This note is provenance documentation, not legal advice.
