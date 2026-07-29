from app.config.settings import Settings


def main() -> None:
    Settings.validate()

    print("Nombre:", Settings.APP_NAME)
    print("Versión:", Settings.APP_VERSION)
    print("Debug:", Settings.DEBUG)
    print("DATABASE_URL configurada:", bool(Settings.DATABASE_URL))


if __name__ == "__main__":
    main()