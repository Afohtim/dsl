.PHONY: clean all

all: main

objects = main.o enriched_semantics.o

$(objects): enriched_semantics.h

main: LDLIBS += -lgsl -lgslcblas
main: $(objects)

clean:
	rm -f $(objects) main
