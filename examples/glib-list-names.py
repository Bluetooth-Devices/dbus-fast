#!/usr/bin/env python3
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import json
import signal

from gi.repository import GLib

from dbus_fast import Message
from dbus_fast.glib import MessageBus

main = GLib.MainLoop()
bus = MessageBus().connect_sync()


def reply_handler(reply, err):
    main.quit()

    if err:
        raise err

    print(json.dumps(reply.body[0], indent=2))


bus.call(
    Message(
        "org.freedesktop.DBus",
        "/org/freedesktop/DBus",
        "org.freedesktop.DBus",
        "ListNames",
    ),
    reply_handler,
)

signal.signal(signal.SIGINT, signal.SIG_DFL)
main.run()
