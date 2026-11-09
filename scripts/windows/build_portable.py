"""Build/package a Windows portable without running Inno or registering the app.

Run with a Windows Python that has the project's dependencies and PyInstaller
installed. VLC_DIR is an extracted official VLC Windows x64 distribution or a
local VLC install; it is read only. No administrator access is needed.
"""

import argparse
import ast
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[2]
PORTABLE_NAME = "GridPlayer-Alabaster-portable"


def run(*args, **kwargs):
    return subprocess.run(args, cwd=ROOT, check=True, **kwargs)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vlc-dir", required=True, type=Path)
    parser.add_argument("--output", type=Path, default=ROOT / "dist")
    parser.add_argument("--package-only", action="store_true")
    args = parser.parse_args()
    if sys.platform != "win32":
        parser.error("Use Windows Python to produce a Windows executable.")
    vlc_dir = args.vlc_dir.resolve()
    for name in ("libvlc.dll", "libvlccore.dll", "plugins", "COPYING.txt"):
        if not (vlc_dir / name).exists():
            parser.error(f"VLC distribution is missing {name}")
    version_vars = {}
    tree = ast.parse((ROOT / "gridplayer/version.py").read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    version_vars[target.id] = node.value.value
    version = version_vars["__version__"]
    app_name = version_vars["__app_name__"]
    build = ROOT / "build"
    build.mkdir(exist_ok=True)
    if not args.package_only:
        shutil.copyfile(ROOT / "resources/icons/main/sys/windows.ico", build / "main.ico")
        shutil.copyfile(ROOT / "resources/icons/playlist/sys/windows.ico", build / "mime.ico")
        replacements = {
            "APP_NAME": app_name,
            "APP_DISP_NAME": version_vars["__display_name__"],
            "APP_MODULE": "gridplayer",
            "APP_VERSION_NUMERIC": version,
            "APP_AUTHOR": version_vars["__author_name__"],
        }
        for source, target in (("pyinstaller_win.spec", "GridPlayer.spec"),
                               ("version_info.py", "version_info.py")):
            text = (ROOT / "scripts/pyinstaller" / source).read_text(encoding="utf-8")
            for key, value in replacements.items():
                text = text.replace("{" + key + "}", value)
            (build / target).write_text(text, encoding="utf-8")
        run(sys.executable, "-m", "PyInstaller", "--clean", "--noconfirm", str(build / "GridPlayer.spec"))
    dist = ROOT / "dist" / app_name
    if not (dist / f"{app_name}.exe").is_file():
        parser.error("PyInstaller executable is missing")
    stage = ROOT / "build" / "portable-stage" / PORTABLE_NAME
    if stage.exists():
        shutil.rmtree(stage)
    shutil.copytree(dist, stage)
    # Copy VLC without its installer, uninstaller, preferences or media files.
    embedded = stage / "libVLC"
    if embedded.exists():
        shutil.rmtree(embedded)
    embedded.mkdir()
    for name in ("libvlc.dll", "libvlccore.dll", "COPYING.txt", "AUTHORS.txt", "THANKS.txt"):
        if (vlc_dir / name).is_file():
            shutil.copyfile(vlc_dir / name, embedded / name)
    shutil.copytree(vlc_dir / "plugins", embedded / "plugins")
    cache = embedded / "plugins/plugins.dat"
    cache.unlink(missing_ok=True)
    if (vlc_dir / "vlc-cache-gen.exe").is_file():
        run(str(vlc_dir / "vlc-cache-gen.exe"), str(embedded / "plugins"))
    portable_data = stage / "portable_data"
    if portable_data.exists():
        shutil.rmtree(portable_data)
    portable_data.mkdir()
    (portable_data / "README.txt").write_text(
        "Settings, logs and cache are stored here. Keep this folder next to GridPlayer.exe.\n",
        encoding="utf-8",
    )
    shutil.copyfile(ROOT / "scripts/windows/PORTABLE-README.txt", stage / "README.txt")
    for name in ("LICENSE", "NOTICE"):
        shutil.copyfile(ROOT / name, stage / name)
    docs = stage / "docs"
    docs.mkdir(exist_ok=True)
    for name in ("USER-GUIDE.md", "KNOWN-LIMITATIONS.md"):
        shutil.copyfile(ROOT / "docs" / name, docs / name)
    commit = run("git", "rev-parse", "HEAD", stdout=subprocess.PIPE, text=True).stdout.strip()
    packages = run(sys.executable, "-m", "pip", "list", "--format=json", stdout=subprocess.PIPE, text=True).stdout
    # Record versions, never pip freeze's local source path or machine details.
    (stage / "BUILD.json").write_text(json.dumps({
        "product": "GridPlayer Alabaster",
        "source_commit": commit,
        "source_repository": version_vars["__app_url__"],
        "python": sys.version.split()[0],
        "packages": json.loads(packages),
    }, indent=2), encoding="utf-8")
    source = stage / "source"
    source.mkdir()
    run("git", "archive", "--format=zip", "--output=" + str(source / "Alabaster-source.zip"), "HEAD")
    (source / "README.txt").write_text(
        "Alabaster-source.zip is the exact tracked application/build source.\n"
        "Third-party source and license information:\n"
        "VLC 3.0.24: https://download.videolan.org/pub/videolan/vlc/3.0.24/\n"
        "Python: https://www.python.org/downloads/source/\n"
        "Qt: https://download.qt.io/archive/qt/5.15/5.15.2/single/\n"
        "PyQt5: https://pypi.org/project/PyQt5/#files\n"
        "Other dependency versions are recorded in BUILD.json; source distributions\n"
        "and licenses are available from the matching projects on https://pypi.org/.\n",
        encoding="utf-8",
    )
    args.output.mkdir(parents=True, exist_ok=True)
    archive = args.output.resolve() / f"GridPlayer-Alabaster-{commit[:7]}-win64-portable.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for path in sorted(stage.rglob("*")):
            if path.is_file():
                zf.write(path, path.relative_to(stage.parent))
    with archive.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    archive.with_suffix(".zip.sha256").write_text(f"{digest}  {archive.name}\n", encoding="ascii")
    print(f"Portable: {archive}\nSHA256: {digest}")


if __name__ == "__main__":
    main()
