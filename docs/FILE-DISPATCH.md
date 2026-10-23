# File dispatch

Status: **GPT-6.1 Sol FAIL** on candidate `afec19e`; this table is a local draft,
not a verified production dispatcher.

## 0. The rule

> The mapping from a file to its editor is **configuration**, on both sides, and it
> must be the **same table**.

Seafile's hook is keyed by extension (`THIRDPARTY_EDITOR_ACTION_URL_DICT`); the
gateway has its own table (`integration/config/dispatch.json`). If they disagree,
the user gets the wrong editor — or an editor that cannot open the file.

## 1. How Seafile computes the extension

```python
# seahub/utils/__init__.py
def get_file_type_and_ext(filename):
    fileExt = os.path.splitext(filename)[1][1:].lower()
    ...
```

Three rules follow:

* the extension is the one **after the last dot** — `report.final.docx` -> `docx`,
  `archive.tar.gz` -> `gz`;
* it is **lowercase** — `REPORT.DOCX` -> `docx`;
* a file with **no dot** has no extension and is never dispatched.

The gateway uses the same rule (`server.py`: `filename.rsplit(".", 1)[-1].lower()`).

## 2. The table

The local prototype table, in `integration/config/dispatch.json`:

| Extension | Craft application | The host URL |
| --- | --- | --- |
| `pdf` | PdfCraft | `/artcraft/pdfcraft/?host=parent` |
| `xlsx` | GridCraft | `/artcraft/gridcraft/?host=parent` |
| `docx` | WordCraft | `/artcraft/wordcraft/?host=parent` |

The live Seafile side is currently **not configured for ArtCraft**. A former
global `.xlsx` mapping was removed, and ONLYOFFICE is unchanged. Per-library
settings are only in the GR-015 patch.

```python
ARTCRAFT_REPO_IDS = ("<synthetic-library-id>",)
ARTCRAFT_FILE_EXTENSIONS = ("docx",)
```

Only the extensions that **exist in the Craft app's own web build** and that
**have a `?host=parent` bridge** belong in the table. An extension without a
bridge would load the application and then never receive the document.

| Application | Has a bridge? | In the table? |
| --- | --- | --- |
| PdfCraft | **yes** | yes (`pdf`) |
| GridCraft | yes, but no durable save-result handling | draft entry only; not ready to route |
| WordCraft | **yes, with our patch** (GR-014) | yes (`docx`) |
| CADCraft | **yes** | not yet — the formats it owns are not in the table |
| DeckCraft | no | no |
| VectorCraft | no (`window.vectorcraft` instead) | no |
| PhotoCraft, FigCraft, DesignCraft, FilmCraft, LightCraft, EffectCraft, SoundCraft | no | no |

**A table entry is a promise.** Every row must name an application that can
actually open the file and hand it back. The gateway refuses an unknown
extension with *"no Craft editor is registered for '&lt;name&gt;'"* rather than
serving an editor that would fail silently.

## 3. The formats each application really handles

From the applications' own extension lists (`crates/doc/src`, `crates/formats`,
`crates/xlsx`, `crates/pptx`, `crates/svg`), **not** assumed:

| Application | Formats it opens and saves | Notes |
| --- | --- | --- |
| WordCraft | `docx`, `docm`, `dotx`, `dotm`, `doc`, `dot`, `odt`, `rtf`, `txt`, `md`, `html`, `htm`, `tex`, `json`, `xml` | `DOC_EXTS` in `apps/wordcraft-web/src/web.rs` |
| GridCraft | `xlsx`, `xlsm`, `xlsb`, `xlt`, `xltm`, `xltx`, `ods`, `ots`, `fods`, `csv`, `et`, `ett`, `numbers` | plus the OOXML encryption formats |
| DeckCraft | `pptx`, `pptm`, `ppt`, `potx`, `potm`, `pot`, `ppsx`, `ppsm`, `pps`, `odp`, `otp`, `fodp` | `crates/pptx` |
| PdfCraft | `pdf`, plus the PDF forms / XFA / annotations it supports | `crates/pdf` |
| VectorCraft | `svg`, `eps`, `pdf` (import), and the app's own formats | `crates/svg`, `crates/eps` |
| CADCraft | `dxf`, `dwg` (read), and its own drawing format | `crates/cad` |

The table in §2 is a **subset**: only the formats that are (a) really supported,
(b) have a bridge today, and (c) are not already claimed by the ONLYOFFICE
integration on the instance.

## 4. The ONLYOFFICE collision

The third-party-editor hook **wins over ONLYOFFICE** for any extension it
claims: its branch is before the ONLYOFFICE branch in `view_lib_file`
(`docs/SEAFILE-INTEGRATION-POINTS.md` §4).

So the table is a **negotiation with the existing integration**:

| Extension | Claimed by the deployed ONLYOFFICE configuration? | Consequence |
| --- | --- | --- |
| `xlsx` | **yes** (`ONLYOFFICE_FILE_EXTENSION`) | claiming it takes `.xlsx` away from ONLYOFFICE |
| `docx` | **yes** | same |
| `pdf` | **no** (the deployed configuration does not list it) | free |

**The rule this project follows: never take an extension from ONLYOFFICE.**

The first proof therefore used `.xlsx` **on a library where no `.xlsx` file
exists**, so no existing file changed behaviour, and the deployed ONLYOFFICE
configuration was not touched. The production answer is the per-library
`artcraft` office-suite id upstream (`docs/UPSTREAM-PLAN.md`).

The required `.docx` Seafile file-list click → WordCraft save/version/reopen
workflow is **NOT VERIFIED**. The earlier direct-open/browser harness did not
go through Seahub's file-list hook and is not an MVP proof.

## 5. What the dispatcher must never do

* **never** guess: an unmapped extension falls back to Seafile's own behaviour
  (download or preview), unchanged;
* **never** send a file to an editor that cannot open it;
* **never** let the two tables disagree;
* **never** be a hardcoded list in the code: the gateway reads it from a file, and
  the file is the thing that changes.

## 6. Open items

| # | Item |
| --- | --- |
| 1 | the Seafile side and the gateway side are two files that must agree; a **single** source of truth is better — the gateway could publish its table, or the Seafile dict could be generated from it. Not done yet. |
| 2 | the per-library choice (which editor a library uses) is the ONLYOFFICE multi-office-suite mechanism, which hardcodes the suite ids. Upstream work. |
| 3 | the formats each Craft app really supports are read from the applications' own lists; they should be checked against the **built** applications, not only their source, when the other apps are added. |
