import os
import subprocess
import tarfile
import json
import platform
import ast

DOWNLOAD_DIR = "put-pacs-here"
LOG_FILE = os.path.join(DOWNLOAD_DIR, "failed_packages.log")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

downloaded = set()
failed = set()


def parse_package_name(pkg):
    """Return (name, version) tuple"""
    if "@" in pkg and not pkg.startswith("@"):
        name, version = pkg.split("@", 1)
    elif pkg.startswith("@") and "@" in pkg[1:]:
        scope_pkg, version = pkg.rsplit("@", 1)
        name = scope_pkg
    else:
        name = pkg
        version = None
    return name, version


def get_npm_command():
    """Return the correct npm command based on OS"""
    if platform.system() == "Windows":
        return r"C:\Program Files\nodejs\npm.cmd"
    return "npm"


def resolve_version(pkg):
    """Resolve version ranges to exact version using npm view"""
    try:
        result = subprocess.run(
            [get_npm_command(), "view", pkg, "version", "--json"],
            capture_output=True, text=True, check=True
        )
        # החזרה של הפלט הנקי. ast.literal_eval יטפל בפענוח
        ver = result.stdout.strip()
        return ver
    except subprocess.CalledProcessError:
        return None


def normalize_version(version):
    """Convert JSON array, list, list string, or quoted string to a single version"""
    if isinstance(version, list):
        # כבר רשימה (כנראה מ-json.load)
        return version[-1]

    if isinstance(version, str):
        v = version.strip()
        try:
            # נסה לפענח את הפלט כ-JSON
            # זה יטפל ב: '"1.2.3"' (מחרוזת JSON)
            # וגם ב: '["1.2.2", "1.2.3"]' (מערך JSON)
            parsed = ast.literal_eval(v)
            if isinstance(parsed, list):
                # אם זה מערך, קח את הגרסה האחרונה (העדכנית ביותר)
                return parsed[-1]
            if isinstance(parsed, str):
                # אם זו מחרוזת, החזר אותה (כבר ללא מרכאות)
                return parsed
        except Exception:
            # נכשל בפענוח - כנראה שזה טווח גרסאות רגיל (כמו "^1.0.0")
            # או מחרוזת פשוטה. נחזיר את המקור.
            pass
    return version  # החזר את המחרוזת המקורית


def download_package(pkg):
    name, version = parse_package_name(pkg)
    id_key = f"{name}@{version}" if version else name

    if id_key in downloaded:
        return

    # נרמול ראשוני (במקרה ש-version הגיע כרשימה מ-package.json)
    version = normalize_version(version)
    if version and any(c in version for c in "*^~<>"):
        resolved = resolve_version(f"{name}@{version}")
        if resolved:
            # --- זה התיקון העיקרי ---
            # נרמל את הפלט שחזר מ-resolve_version
            # זה יהפוך את '["1.0", "2.0"]' ל-"2.0"
            version = normalize_version(resolved)
        else:
            print(f"[WARN] Could not resolve version for {pkg}")
            failed.add(pkg)
            return

    if version:
        pkg_to_download = f"{name}@{version}"
    else:
        pkg_to_download = name

    print(f"[INFO] Downloading {pkg_to_download}")
    npm_cmd = get_npm_command()
    try:
        subprocess.run([npm_cmd, "pack", pkg_to_download], cwd=DOWNLOAD_DIR, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to download {id_key}: {e}")
        failed.add(id_key)
        return
    except FileNotFoundError:
        print(f"[ERROR] npm not found. Make sure Node.js is installed and npm is in PATH.")
        failed.add(id_key)
        return

    # Find the tgz file
    tgz_file = None
    prefix = name[1:].replace("/", "-") if name.startswith("@") else name
    for f in os.listdir(DOWNLOAD_DIR):
        if f.startswith(prefix) and f.endswith(".tgz"):
            tgz_file = os.path.join(DOWNLOAD_DIR, f)
            break
    if not tgz_file:
        print(f"[ERROR] Could not find tgz for {id_key}")
        failed.add(id_key)
        return

    downloaded.add(id_key)

    # Read dependencies from package.json inside tgz
    try:
        with tarfile.open(tgz_file, "r:gz") as tar:
            pkg_json_file = None
            for member in tar.getmembers():
                # הבטחת התאמה רק לקובץ package.json ברמה העליונה של התיקייה
                if member.name.count('/') == 1 and member.name.endswith("package.json"):
                    pkg_json_file = tar.extractfile(member)
                    break
            if pkg_json_file:
                pkg_info = json.load(pkg_json_file)
                dependencies = pkg_info.get("dependencies", {})
                for dep_name, dep_version in dependencies.items():
                    # אין צורך לקרוא ל-normalize_version כאן, כי הקריאה הבאה
                    # ל-download_package תטפל בזה בתחילת הפונקציה.
                    download_package(f"{dep_name}@{dep_version}")
            else:
                print(f"[WARN] package.json not found in {tgz_file}")
                failed.add(id_key)
    except Exception as e:
        print(f"[WARN] Could not read package.json in {tgz_file}: {e}")
        failed.add(id_key)


def main():
    print("Enter the package you want to download (with optional version, e.g., express@5.1.0):")
    package_name = input("> ").strip()
    if not package_name:
        print("No package entered. Exiting.")
        return

    download_package(package_name)

    if failed:
        print("\nSome packages failed to download. See log for details.")
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            for pkg in sorted(failed):
                f.write(pkg + "\n")
    else:
        print("\nAll packages downloaded successfully!")

    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()
