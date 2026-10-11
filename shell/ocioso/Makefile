# hyprmac-ocioso: vigia de inatividade (ext-idle-notify-v1)
XML = /usr/share/wayland-protocols/staging/ext-idle-notify/ext-idle-notify-v1.xml

hyprmac-ocioso: hyprmac-ocioso.c ext-idle-notify-v1-protocol.c ext-idle-notify-v1-client-protocol.h
	$(CC) -O2 -Wall -o $@ hyprmac-ocioso.c ext-idle-notify-v1-protocol.c $(shell pkg-config --cflags --libs wayland-client)

ext-idle-notify-v1-client-protocol.h: $(XML)
	wayland-scanner client-header $< $@

ext-idle-notify-v1-protocol.c: $(XML)
	wayland-scanner private-code $< $@

clean:
	rm -f hyprmac-ocioso ext-idle-notify-v1-protocol.c ext-idle-notify-v1-client-protocol.h
