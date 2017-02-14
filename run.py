#!/usr/bin/env python3

from ueberwachungspaket import init_db, app

if __name__ == "__main__":
    init_db()
    app.run()
