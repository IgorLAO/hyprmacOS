# Módulo "Tocando Agora" da barra: make -C ~/Projects/hyprmac/waybar/cffi
CFLAGS += -O2 -Wall -fPIC $(shell pkg-config --cflags gtk+-3.0 playerctl)
LDLIBS += $(shell pkg-config --libs gtk+-3.0 playerctl) -lm

nowplaying.so: nowplaying.c
	$(CC) $(CFLAGS) -shared -o $@ $< $(LDLIBS)

clean:
	rm -f nowplaying.so
