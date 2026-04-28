"""Entry point — enforces license before launching app."""


def main():
    from qt_ui_modern.license_dialog import is_licensed, run_license_dialog
    if not is_licensed():
        if not run_license_dialog():
            import sys
            sys.exit(1)
    from main import main as app_main
    app_main()


if __name__ == "__main__":
    main()
