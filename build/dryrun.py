"""Linux dry-run: instantiate MainWindow with Xvfb to catch import + signature errors."""
import os, sys, traceback
os.environ["QT_QPA_PLATFORM"] = "offscreen"  # headless Qt
os.environ["VEO_BYPASS_LICENSE"] = "1"

# Add tool path
sys.path.insert(0, "/root/veo-pipeline/tool")

errors = []

print("[1] Import launcher_pro module symbols...")
try:
    from qt_ui_modern.styles import GLOBAL_QSS
    from qt_ui_modern import theme as t
    from qt_ui_modern.license_dialog import is_licensed, LicenseDialog
    from qt_ui_modern.onboarding import needs_onboarding, mark_onboarded, OnboardingWizard
    from qt_ui_modern.tray import install_tray
    from qt_ui_modern.bulk_login import BulkLoginDialog
    from qt_ui_modern.splash import show_splash
    from qt_ui_modern.auto_update import check_and_prompt
    from qt_ui_modern.drive_sync import start_background
    print("  ✓ qt_ui_modern OK")
except Exception as e:
    errors.append(f"qt_ui_modern: {e}")
    traceback.print_exc()

print("[2] Import legacy MainWindow + AppConfig...")
try:
    from ui import MainWindow, AppConfig
    print("  ✓ qt_ui.ui OK")
except Exception as e:
    errors.append(f"qt_ui.ui: {e}")
    traceback.print_exc()

print("[3] Instantiate QApplication...")
try:
    from PyQt6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication(sys.argv)
    print("  ✓ QApplication OK")
except Exception as e:
    errors.append(f"QApplication: {e}")
    traceback.print_exc()

print("[4] Load AppConfig...")
try:
    cfg = AppConfig.load()
    print(f"  ✓ AppConfig loaded: {type(cfg).__name__}")
except Exception as e:
    errors.append(f"AppConfig.load: {e}")
    traceback.print_exc()

print("[5] Instantiate MainWindow(cfg)...")
try:
    win = MainWindow(cfg)
    print(f"  ✓ MainWindow created")
    print(f"     Window title: {win.windowTitle()}")
    print(f"     Tabs: {win.tabs.count() if hasattr(win,'tabs') else 'n/a'}")
except Exception as e:
    errors.append(f"MainWindow: {e}")
    traceback.print_exc()

print("[6] Instantiate LicenseDialog + OnboardingWizard + BulkLoginDialog...")
for cls_name, cls in [("LicenseDialog", LicenseDialog), ("OnboardingWizard", OnboardingWizard), ("BulkLoginDialog", BulkLoginDialog)]:
    try:
        d = cls()
        print(f"  ✓ {cls_name} OK")
    except Exception as e:
        errors.append(f"{cls_name}: {e}")
        traceback.print_exc()

print()
print("=" * 50)
if errors:
    print(f"❌ FAIL: {len(errors)} errors")
    for e in errors: print(f"  - {e}")
    sys.exit(1)
else:
    print("✅ ALL OK — safe to push")
    sys.exit(0)
