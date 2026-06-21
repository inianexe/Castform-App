# Castform

Castform is a tiny Windows file-conversion utility designed for Explorer right-click workflows.

Double-click `Castform.exe` once to install it. After that, right-click a file, choose **Castform**, pick **PDF** or **JPG**, and get a converted file beside the original.

## Features

- Explorer context-menu workflow
- Optional system tray app
- No required background service
- Single-file EXE build with bundled Python dependencies
- Safe output naming: existing files are not overwritten
- Per-user context-menu registration, so admin is not required for the EXE self-install path
- Microsoft Office COM export for high-fidelity `.docx` and `.pptx` layout preservation
- Orange settings popup with output format, folder, suffix, resize, and compression controls
- JPG compression and image resize support
- PDF page selection and all-pages PDF-to-JPG export
- Settings are remembered between conversions
- Transparent images can be flattened against a white background

## Conversion Matrix

| Input | Output | Engine |
| --- | --- | --- |
| `.docx` | `.pdf` | Microsoft Word COM export |
| `.pptx` | `.pdf` | Microsoft PowerPoint COM export |
| `.txt` | `.pdf` | Native Pillow-based A4 renderer |
| `.jpg`, `.jpeg` | `.pdf` | Pillow |
| `.jpg`, `.jpeg` | `.jpg` | Pillow compression / resize |
| `.png`, `.bmp`, `.tif`, `.tiff` | `.pdf` | Pillow |
| `.png`, `.bmp`, `.tif`, `.tiff` | `.jpg` | Pillow |
| `.webp` | `.jpg` | Pillow |
| `.webp` | `.pdf` | Pillow |
| `.pdf` | `.jpg` | PDFium via pypdfium2 |

Office conversions require Microsoft Office to be installed on Windows.

## Download / Install

For normal users, use the packaged EXE:

```text
dist\Castform.exe
```

The EXE is self-contained. Users do **not** need to install Python packages or run `requirements.txt`.

When you build Castform, `packaging\build-exe.ps1` installs `requirements.txt` into the build environment and PyInstaller bundles those packages into `Castform.exe`. The installed app does not run `pip` on the user's machine.

Install:

1. Download or copy `Castform.exe`.
2. Double-click `Castform.exe`.
3. Castform automatically installs the Explorer right-click menu.
4. Castform automatically enables tray startup.
5. The tray icon appears in the Windows notification area.

No PowerShell is required for normal use.

The tray menu can remove the Explorer menu, disable startup, open the Castform folder, and quit.

When you right-click a supported file and select **Castform**, a popup asks whether to convert to **PDF** or **JPG**. Unsupported choices are disabled automatically. The popup also supports a custom output folder, filename suffixes, JPG compression quality, optional image resizing, PDF page selection, all-pages PDF export, transparency flattening, auto-oriented image PDFs, and opening the output folder after conversion.

## Command-Line Usage

Command-line usage is mainly for developers and testing.

Convert beside the original file:

```powershell
.\dist\Castform.exe "C:\Users\You\Desktop\sample.txt"
```

Skip the popup and choose the target directly:

```powershell
.\dist\Castform.exe "C:\Users\You\Desktop\sample.txt" --target pdf
.\dist\Castform.exe "C:\Users\You\Desktop\sample.webp" --target jpg
```

Resize/compress image output from the command line:

```powershell
.\dist\Castform.exe "C:\Users\You\Desktop\sample.webp" --target jpg --quality 80 --max-width 1600
```

Export every PDF page to JPG:

```powershell
.\dist\Castform.exe "C:\Users\You\Desktop\document.pdf" --target jpg --pdf-all-pages
```

Export one PDF page:

```powershell
.\dist\Castform.exe "C:\Users\You\Desktop\document.pdf" --target jpg --pdf-page 3
```

Add a filename suffix:

```powershell
.\dist\Castform.exe "C:\Users\You\Desktop\photo.png" --target jpg --suffix compressed
```

Convert into a custom folder:

```powershell
.\dist\Castform.exe "C:\Users\You\Desktop\sample.webp" --output-dir "C:\Users\You\Desktop\Converted"
```

If `sample.pdf` already exists, Castform writes `sample (1).pdf`, then `sample (2).pdf`, and so on.

## Build From Source

Create and activate a virtual environment:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install build/runtime dependencies:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pyinstaller
```

PDF-to-JPG support:

```powershell
python -m pip install -r requirements-optional.txt
```

Build the EXE with the project icon:

```powershell
powershell -ExecutionPolicy Bypass -File .\packaging\build-exe.ps1
```

The output is:

```text
dist\Castform.exe
```

## Build MSI

Install WiX Toolset v4:

```powershell
dotnet tool install --global wix
```

Build the MSI:

```powershell
powershell -ExecutionPolicy Bypass -File .\packaging\build-msi.ps1
```

The MSI installs Castform to:

```text
C:\Program Files\Castform\Castform.exe
```

and registers the Explorer context menu.

## Test

Run source smoke tests:

```powershell
python .\tests\smoke_test.py
```

Build and test the packaged EXE:

```powershell
powershell -ExecutionPolicy Bypass -File .\packaging\build-exe.ps1
powershell -ExecutionPolicy Bypass -File .\packaging\test-exe.ps1
```

The smoke suite checks `.txt -> .pdf`, `.jpeg -> .pdf`, `.webp -> .jpg`, `.png -> .pdf`, `.png -> .jpg`, `.pdf -> .jpg`, PDF page selection, all-pages PDF export, resize/compress, suffixes, measured text wrapping, packaged execution, and no-overwrite output naming.

Optional Office smoke test:

```powershell
powershell -ExecutionPolicy Bypass -File .\packaging\test-exe.ps1 -IncludeOffice
```

This creates temporary Word and PowerPoint files through Microsoft Office COM automation, then converts them through the packaged EXE. If Office is not licensed, is showing first-run prompts, or is blocked by policy, this optional test can fail even when the rest of Castform works.

## Layout Fidelity

`.docx` and `.pptx` conversions are delegated to Microsoft Office export APIs, which gives the best layout fidelity available on Windows for Office files.

Plain text has no source layout metadata, so Castform renders it into a clean A4 PDF with measured font wrapping, fixed margins, and 300 DPI output. JPEG and WebP conversions preserve the source image geometry.

## Repository Layout

```text
castform.py                  CLI entry point
castform/                    routing, pathing, tray, registry, and converter modules
packaging/                   PyInstaller and WiX build scripts
tests/smoke_test.py          source and EXE smoke tests
requirements.txt             dependencies bundled into the EXE
requirements-optional.txt    optional PDF rasterization dependency
pngwing.com (2).ico          application icon
```

## License

MIT
