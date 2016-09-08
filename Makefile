OS:=$(shell uname)

##############################################################################
####                                 FLAGS                                ####
##############################################################################
ifeq ($(OS), Darwin)
  CXX= g++ -I/usr/local/include
  LDFLAGS= -L/usr/local/lib -lpthread -lbenchmark
else
  CXX= g++
  LDFLAGS= -lpthread -lbenchmark
endif
CXXFLAGS= -DNDEBUG -pedantic -std=c++14 -O3

##############################################################################
####                             SAT SOLVERS                              ####
##############################################################################
SAT_SOLVERS=glucose picosat cryptominisat

##############################################################################
####                              BENCH OBJS                              ####
##############################################################################
BENCH= bench.o
BENCH_OBJS= $(addprefix bench/, $(BENCH))

##############################################################################
####                                OTHERS                                ####
##############################################################################
BIN= fastSAT

all: bins $(BIN)

bins:
	-mkdir bin

$(BIN): $(SAT_SOLVERS) $(BENCH_OBJS)
	$(CXX) $(CXXFLAGS) $(BENCH_OBJS) $(LDFLAGS) -o $@
	./run.py --timeout 120 --save result
	cat result

bench:
	rm -rf $(BENCH_OBJS)
	make bench-build
	./run.py

bench-build: $(BENCH_OBJS)
	$(CXX) $(CXXFLAGS) $(BENCH_OBJS) $(LDFLAGS) -o $(BIN)

glucose:
	cd satsolvers/glucose-syrup/simp; make rs
	cd satsolvers/glucose-syrup/parallel; make rs
	mv -f satsolvers/glucose-syrup/parallel/glucose-syrup_static bin/
	mv -f satsolvers/glucose-syrup/simp/glucose_static bin/

picosat:
	cd satsolvers/picosat-965; ./configure.sh && make
	mv satsolvers/picosat-965/picosat bin/

cryptominisat:
	-cd satsolvers/cryptominisat-5.0.1; mkdir build; cd build; cmake ..; make -j4
	-mv satsolvers/cryptominisat-5.0.1/build/cryptominisat5 bin/
	mv satsolvers/cryptominisat-5.0.1/build/cryptominisat5_simple bin/

clean:
	-rm -rf $(BENCH_OBJS) $(BIN) *.dSYM
	-cd satsolvers/glucose-syrup/simp; make clean
	-cd satsolvers/glucose-syrup/parallel; make clean
	-cd satsolvers/picosat-965; make clean
	-rm -rf satsolvers/cryptominisat-5.0.1/build
	-rm -rf bin/*

.PHONY: clean bench
