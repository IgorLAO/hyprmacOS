#!/usr/bin/python3
"""SNI de teste: ícones ARGB, atenção/overlay, estado, eventos e menu D-Bus.

Uso: status_notifier.py /tmp/events.jsonl
Controlar: gdbus call --session --dest dev.hyprmac.SNITest --object-path /StatusNotifierItem \
 --method dev.hyprmac.SNITest.Command 'attention'
Comandos: attention, normal, overlay, passive, active, menu, activate.
Não deve ser instalado/autoiniciado no desktop.
"""
import json
import sys
import gi
gi.require_version('Dbusmenu', '0.4')
from gi.repository import Gio, GLib, Dbusmenu

IFACE = 'org.kde.StatusNotifierItem'
PATH = '/StatusNotifierItem'
BUS = 'dev.hyprmac.SNITest'
SNI = '''<node><interface name="org.kde.StatusNotifierItem">
<method name="Activate"><arg type="i" direction="in"/><arg type="i" direction="in"/></method>
<method name="SecondaryActivate"><arg type="i" direction="in"/><arg type="i" direction="in"/></method>
<method name="ContextMenu"><arg type="i" direction="in"/><arg type="i" direction="in"/></method>
<method name="Scroll"><arg type="i" direction="in"/><arg type="s" direction="in"/></method>
<property name="Category" type="s" access="read"/><property name="Id" type="s" access="read"/>
<property name="Title" type="s" access="read"/><property name="Status" type="s" access="read"/>
<property name="IconName" type="s" access="read"/><property name="IconPixmap" type="a(iiay)" access="read"/>
<property name="AttentionIconName" type="s" access="read"/><property name="AttentionIconPixmap" type="a(iiay)" access="read"/>
<property name="OverlayIconName" type="s" access="read"/><property name="OverlayIconPixmap" type="a(iiay)" access="read"/>
<property name="ItemIsMenu" type="b" access="read"/><property name="Menu" type="o" access="read"/>
<signal name="NewIcon"/><signal name="NewAttentionIcon"/><signal name="NewOverlayIcon"/>
<signal name="NewStatus"><arg type="s"/></signal>
</interface><interface name="dev.hyprmac.SNITest"><method name="Command">
<arg type="s" direction="in"/></method></interface></node>'''


def pixmap(color, overlay=False):
    pixels = bytearray()
    for y in range(16):
        for x in range(16):
            pixels.extend(color if not overlay or x >= 10 and y >= 10 else (0, 0, 0, 0))
    return GLib.Variant('a(iiay)', [(16, 16, pixels)])


props = {name: GLib.Variant('s', value) for name, value in {
    'Category': 'ApplicationStatus', 'Id': 'hyprmac-sni-test', 'Title': 'HyprMac SNI Test',
    'Status': 'Active', 'IconName': '', 'AttentionIconName': '', 'OverlayIconName': ''}.items()}
props.update({'IconPixmap': pixmap((255, 0, 200, 255)),
              'AttentionIconPixmap': pixmap((255, 255, 80, 40)),
              'OverlayIconPixmap': GLib.Variant('a(iiay)', []),
              'Menu': GLib.Variant('o', '/MenuBarTest'), 'ItemIsMenu': GLib.Variant('b', False)})
bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)


def log(method, args):
    with open(sys.argv[1], 'a') as f:
        f.write(json.dumps({'method': method, 'args': args}) + '\n')


def emit(name, value=None):
    bus.emit_signal(None, PATH, IFACE, name, GLib.Variant('(s)', (value,)) if value else None)


def method(connection, sender, path, interface, name, args, invocation):
    log(name, args.unpack())
    if name == 'Command':
        command = args.unpack()[0]
        if command in ['attention', 'normal', 'passive', 'active']:
            status = {'attention': 'NeedsAttention', 'normal': 'Active', 'passive': 'Passive', 'active': 'Active'}[command]
            props['Status'] = GLib.Variant('s', status)
            emit('NewStatus', status)
        elif command == 'no-overlay':
            props['OverlayIconPixmap'] = GLib.Variant('a(iiay)', [])
            emit('NewOverlayIcon')
        elif command == 'overlay':
            props['OverlayIconPixmap'] = pixmap((255, 0, 255, 0), True)
            emit('NewOverlayIcon')
        elif command in ['menu', 'activate']:
            props['ItemIsMenu'] = GLib.Variant('b', command == 'menu')
            # Supported extension: refresh ItemIsMenu alongside icon properties.
            emit('NewIcon')
        elif command == 'attention-icon':
            props['AttentionIconPixmap'] = pixmap((255, 255, 0, 255))
            emit('NewAttentionIcon')
    invocation.return_value(None)


node = Gio.DBusNodeInfo.new_for_xml(SNI)
for interface in node.interfaces:
    bus.register_object(PATH, interface, method,
                        lambda conn, sender, path, iface, name: props.get(name), None)
server = Dbusmenu.Server.new('/MenuBarTest')
root = Dbusmenu.Menuitem.new()
entry = Dbusmenu.Menuitem.new()
entry.property_set('label', 'Test action')
entry.property_set_bool('enabled', True)
entry.property_set_bool('visible', True)
entry.connect('item-activated', lambda item, timestamp: log('MenuEvent', ['Test action']))
root.child_append(entry)
server.set_root(root)


def watcher_appeared(conn, name, owner):
    conn.call('org.kde.StatusNotifierWatcher', '/StatusNotifierWatcher',
              'org.kde.StatusNotifierWatcher', 'RegisterStatusNotifierItem',
              GLib.Variant('(s)', (BUS,)), None, Gio.DBusCallFlags.NONE, 2000, None, None, None)


if len(sys.argv) > 2 and sys.argv[2] == 'late-name':
    # Reproduce a publisher registering before its well-known name is owned.
    # The watch initially vanishes, later reappears, then survives a bar reload.
    def delayed_own():
        Gio.bus_own_name_on_connection(bus, BUS, Gio.BusNameOwnerFlags.NONE,
                                      lambda conn, name: watcher_appeared(conn, '', ''), None)
        return False
    GLib.timeout_add(250, delayed_own)
else:
    Gio.bus_own_name_on_connection(bus, BUS, Gio.BusNameOwnerFlags.NONE, None, None)
Gio.bus_watch_name_on_connection(bus, 'org.kde.StatusNotifierWatcher',
                                 Gio.BusNameWatcherFlags.NONE, watcher_appeared, None)
GLib.MainLoop().run()
