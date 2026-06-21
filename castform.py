from __future__ import annotations

import argparse
import multiprocessing
import subprocess
import sys
from pathlib import Path

from castform.config import AppConfig
from castform.pipeline import convert
from castform.registry import (
    install_context_menu,
    install_startup_tray,
    remove_context_menu,
    remove_startup_tray,
)
from castform.routing import output_kind_from_text
from castform.tray import run_tray
from castform.ui import ask_conversion_choice, show_conversion_error, show_conversion_success


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="castform",
        description="Small Windows shell file conversion utility.",
    )
    parser.add_argument("file", nargs="?", help="File path passed by Explorer.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Write converted file to this directory instead of beside the source.",
    )
    parser.add_argument(
        "--target",
        choices=("pdf", "jpg", "jpeg"),
        help="Output format. If omitted for a file, Castform asks with a popup.",
    )
    parser.add_argument("--quality", type=int, default=92, help="JPG quality from 1 to 100.")
    parser.add_argument("--max-width", type=int, help="Resize image output to this max width.")
    parser.add_argument("--max-height", type=int, help="Resize image output to this max height.")
    parser.add_argument("--suffix", default="", help="Suffix to append before the output extension.")
    parser.add_argument("--open-output-folder", action="store_true", help="Open the output folder.")
    parser.add_argument("--pdf-all-pages", action="store_true", help="Export every PDF page to JPG.")
    parser.add_argument("--pdf-page", type=int, default=1, help="PDF page number to export to JPG.")
    parser.add_argument(
        "--transparent-background",
        action="store_true",
        help="Use black instead of white when flattening transparent images.",
    )
    parser.add_argument(
        "--install-context-menu",
        action="store_true",
        help="Register Castform in the Explorer right-click menu.",
    )
    parser.add_argument(
        "--remove-context-menu",
        action="store_true",
        help="Remove Castform from the Explorer right-click menu.",
    )
    parser.add_argument(
        "--tray",
        action="store_true",
        help="Run Castform as a system tray app.",
    )
    parser.add_argument(
        "--install-startup-tray",
        action="store_true",
        help="Start Castform tray mode when Windows starts.",
    )
    parser.add_argument(
        "--remove-startup-tray",
        action="store_true",
        help="Remove Castform tray mode from Windows startup.",
    )

    args = parser.parse_args()

    try:
        if args.install_context_menu:
            install_context_menu(Path(__file__).resolve())
            print("Castform context menu installed.")
            return 0

        if args.remove_context_menu:
            remove_context_menu()
            print("Castform context menu removed.")
            return 0

        if args.install_startup_tray:
            install_startup_tray(Path(__file__).resolve())
            print("Castform tray startup installed.")
            return 0

        if args.remove_startup_tray:
            remove_startup_tray()
            print("Castform tray startup removed.")
            return 0

        if args.tray:
            run_tray(Path(__file__).resolve())
            return 0

        if not args.file:
            install_context_menu(Path(__file__).resolve())
            install_startup_tray(Path(__file__).resolve())
            run_tray(Path(__file__).resolve())
            return 0

        source = Path(args.file)
        interactive = args.target is None

        if interactive:
            choice = ask_conversion_choice(source)
            if choice is None:
                return 0
            target = choice.target
            config = choice.config
        else:
            target = output_kind_from_text(args.target)
            config = AppConfig(
                save_to_original_location=args.output_dir is None,
                custom_output_path=args.output_dir,
                jpeg_quality=max(1, min(100, args.quality)),
                max_width=args.max_width,
                max_height=args.max_height,
                output_suffix=args.suffix,
                open_output_folder=args.open_output_folder,
                pdf_all_pages=args.pdf_all_pages,
                pdf_page_number=max(1, args.pdf_page),
                white_background=not args.transparent_background,
            )

        if target is None:
            return 0

        outputs = convert(source, config, target)
        if config.open_output_folder and outputs:
            _open_output_folder(outputs[0])
        if interactive:
            show_conversion_success(outputs)
        for output in outputs:
            print(f"Created: {output}")
        return 0
    except Exception as exc:
        if "args" in locals() and getattr(args, "file", None) and not getattr(args, "target", None):
            show_conversion_error(str(exc))
        print(f"Castform error: {exc}", file=sys.stderr)
        return 1


def _open_output_folder(output: Path) -> None:
    if sys.platform == "win32":
        subprocess.Popen(["explorer", "/select,", str(output)])


if __name__ == "__main__":
    multiprocessing.freeze_support()
    raise SystemExit(main())
