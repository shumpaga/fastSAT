# fastSAT
This project was born to help choose a sat solver to distribute with Spot(https://spot.lrde.epita.fr/).<br/>
These sat solvers had to be compatible with its GPL v3 licence.<br/>
At the end, picoSAT was finally chosen for its simplicity of integration and its performances.<br/>

# Requirements:<br/>
Please, make sure those libraries are installed:<br/>
-lbenchmark (https://github.com/google/benchmark)<br/>
-lpthread (http://packages.ubuntu.com/yakkety/libpthread-stubs0-dev ubuntu).

# Makefile rules:
* make or make all:<br/>
  -compile all satsolvers<br/>
  -gather binaries in "bin" folder at the root directory<br/>
  -compile bench program<br/>
  -run bench with python script
  
* make bench:<br/>
  -delete bench program, recompile it<br/>
  -run bench with python script

* make clean:<br/>
  -delete all building files.
