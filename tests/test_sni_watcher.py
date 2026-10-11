"""Teste opt-in da build real: execute dentro de dbus-run-session.

HYPRMAC_TEST_SNI_WATCHER=1 dbus-run-session -- python -m unittest discover -s tests -p test_sni_watcher.py
Requer desktop Wayland ativo; cria/fecha uma barra transparente não exclusiva.
"""
import json
import os
import signal
from pathlib import Path
import subprocess
import tempfile
import time
import unittest


@unittest.skipUnless(os.environ.get('HYPRMAC_TEST_SNI_WATCHER') == '1', 'requer bus isolado e desktop Wayland')
class ExternalWatcher(unittest.TestCase):
    def test_existing_watcher_is_not_replaced_and_host_registers(self):
        import gi
        from gi.repository import Gio, GLib
        bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
        xml = '''<node><interface name="org.kde.StatusNotifierWatcher">
        <method name="RegisterStatusNotifierHost"><arg type="s" direction="in"/></method>
        <method name="RegisterStatusNotifierItem"><arg type="s" direction="in"/></method>
        <property name="RegisteredStatusNotifierItems" type="as" access="read"/>
        <property name="IsStatusNotifierHostRegistered" type="b" access="read"/>
        <property name="ProtocolVersion" type="i" access="read"/>
        <signal name="StatusNotifierItemRegistered"><arg type="s"/></signal>
        <signal name="StatusNotifierItemUnregistered"><arg type="s"/></signal>
        </interface></node>'''
        calls = []

        def method(conn, sender, path, iface, name, args, invocation):
            calls.append(name)
            invocation.return_value(None)

        properties = {'RegisteredStatusNotifierItems': GLib.Variant('as', []),
                      'IsStatusNotifierHostRegistered': GLib.Variant('b', True),
                      'ProtocolVersion': GLib.Variant('i', 0)}
        registration = bus.register_object('/StatusNotifierWatcher', Gio.DBusNodeInfo.new_for_xml(xml).interfaces[0],
                                           method, lambda *args: properties[args[-1]], None)
        name = Gio.bus_own_name_on_connection(bus, 'org.kde.StatusNotifierWatcher',
                                            Gio.BusNameOwnerFlags.ALLOW_REPLACEMENT, None, None)
        self.addCleanup(Gio.bus_unown_name, name)
        self.addCleanup(bus.unregister_object, registration)
        context = GLib.MainContext.default()
        for _ in range(20):
            while context.pending():
                context.iteration(False)
            time.sleep(.01)
        binary = Path(os.environ.get('XDG_CACHE_HOME', str(Path.home() / '.cache'))) / 'hyprmac/waybar-tahoe/waybar'
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / 'config.json'
            config.write_text(json.dumps({'height': 1, 'position': 'bottom', 'exclusive': False,
                                          'modules-left': [], 'modules-right': ['tray']}))
            style = Path(directory) / 'style.css'
            style.write_text('window#waybar { background: transparent; }')
            process = subprocess.Popen([str(binary), '-c', str(config), '-s', str(style)],
                                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.addCleanup(lambda: process.kill() if process.poll() is None else None)
            try:
                deadline = time.monotonic() + 5
                while time.monotonic() < deadline and not calls and process.poll() is None:
                    while context.pending():
                        context.iteration(False)
                    time.sleep(.02)
                self.assertIn('RegisterStatusNotifierHost', calls)
                owner = bus.call_sync('org.freedesktop.DBus', '/org/freedesktop/DBus',
                                      'org.freedesktop.DBus', 'GetNameOwner',
                                      GLib.Variant('(s)', ('org.kde.StatusNotifierWatcher',)), None,
                                      Gio.DBusCallFlags.NONE, 2000, None).unpack()[0]
                self.assertEqual(owner, bus.get_unique_name())
            finally:
                process.terminate()
                process.wait(timeout=5)

    def test_item_exit_after_three_reloads_keeps_bar_alive(self):
        from gi.repository import Gio, GLib
        bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
        context = GLib.MainContext.default()
        binary = Path(os.environ.get('XDG_CACHE_HOME', str(Path.home() / '.cache'))) / 'hyprmac/waybar-tahoe/waybar'

        def items():
            try:
                return bus.call_sync('org.kde.StatusNotifierWatcher', '/StatusNotifierWatcher',
                                     'org.freedesktop.DBus.Properties', 'Get',
                                     GLib.Variant('(ss)', ('org.kde.StatusNotifierWatcher', 'RegisteredStatusNotifierItems')),
                                     None, Gio.DBusCallFlags.NONE, 1000, None).unpack()[0]
            except GLib.Error:
                return None

        def wait_for(predicate):
            deadline = time.monotonic() + 6
            while time.monotonic() < deadline:
                while context.pending():
                    context.iteration(False)
                if predicate():
                    return True
                time.sleep(.03)
            return False

        # Drain the unown/unregister callbacks from the preceding test.
        for _ in range(10):
            while context.pending():
                context.iteration(False)
            time.sleep(.02)
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / 'config.json'
            config.write_text(json.dumps({'height': 1, 'position': 'bottom', 'exclusive': False,
                                          'modules-left': [], 'modules-right': ['tray']}))
            style = Path(directory) / 'style.css'
            style.write_text('window#waybar { background: transparent; }')
            process = subprocess.Popen([str(binary), '-c', str(config), '-s', str(style)],
                                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            fixture = None
            try:
                self.assertTrue(wait_for(lambda: items() == []))
                fixture = subprocess.Popen(['/usr/bin/python3', str(Path(__file__).parent / 'fixtures/status_notifier.py'),
                                            str(Path(directory) / 'events.jsonl'), 'late-name'],
                                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                time.sleep(.6)
                self.assertTrue(wait_for(lambda: bool(items())))
                for _ in range(3):
                    process.send_signal(signal.SIGUSR2)
                    time.sleep(.3)
                    self.assertTrue(wait_for(lambda: items() and len(items()) == 1))
                    self.assertIsNone(process.poll())
                fixture.terminate()
                fixture.wait(timeout=5)
                self.assertTrue(wait_for(lambda: items() == []))
                time.sleep(.2)
                self.assertIsNone(process.poll(), 'app exit after reload crashed Waybar')
            finally:
                if fixture and fixture.poll() is None:
                    fixture.terminate()
                    fixture.wait(timeout=5)
                if process.poll() is None:
                    process.terminate()
                process.wait(timeout=5)


if __name__ == '__main__':
    unittest.main()
