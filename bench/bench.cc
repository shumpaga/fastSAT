#include <iostream>
#include <stdexcept>
#include <cstring>
#include <cassert>
#include <chrono>

#include "bench.hh"

std::string test; // The test that will be run
int nbstates = -1;

#define bench(X)\
  BENCHMARK(X)->Unit(benchmark::kMicrosecond)->UseRealTime();

#define launch_bench(SATSOLVER)                                               \
  do {                                                                        \
    /* Prepare the cmd */                                                     \
    static std::string cmd = getCmd();                                        \
                                                                              \
    /* Switch to the correct sat solver */                                    \
    static int switched = switch_satsolver(SATSOLVER);                        \
    static bool timeout = false;                                              \
    static std::string res = "";                                              \
                                                                              \
    /* execution */                                                           \
    static auto start = std::chrono::high_resolution_clock::now();            \
    while(state.KeepRunning())                                                \
      res = exec(cmd);                                                        \
                                                                              \
    /* Check the result -- executed once */                                   \
    static int printed = print_res(__FUNCTION__, res, timeout);               \
  } while(0)                                                                  \

/**
**  Function to build the shell cmd that will be executed
*/
std::string getCmd()
{
  std::string cmd = "ltl2tgba -D -x ";

  if (nbstates != -1) {
    cmd.append("sat-states=");
    cmd.append(std::to_string(nbstates));
    cmd.append(" '");
  }
  else {
    cmd.append("sat-minimize '");
  }

  cmd.append(test); /* Global variable */
  cmd.append("' --stats='states=%s, det=%d'");
  return cmd;
}

/**
** Function to execute a shell process and get the output
**/
std::string exec(std::string cmd)
{
  char buffer[128];
  std::string result = "";
  FILE* pipe = popen(cmd.data(), "r");
  if (!pipe)
    throw std::runtime_error("popen() failed!");
  try
  {
    while(!feof(pipe))
    {
      if (fgets(buffer, 128, pipe) != NULL)
        result += buffer;
    }
  } catch(...)
  {
    pclose(pipe);
    throw;
  }
  pclose(pipe);
  return result;
}

/**
** Function to swith the sat solver used by spot.
** sat_cmd should be like this: "<sat_solver> <options> %I > %O"
**/
int switch_satsolver(const char *sat_cmd)
{
  if (setenv("SPOT_SATSOLVER", sat_cmd, 1) == -1)
    throw std::runtime_error(sat_cmd);

  assert(getenv("SPOT_SATSOLVER") == sat_cmd);
  return 0;
}

/**
** Print result to std::cout
*/
int print_res(const char* name, std::string& res, bool& timeout)
{
  if (!timeout)
    std::cout << name << ": " << res;
  return 0;
}

////////////////////////      SAT SOLVERS    /////////////////////////////////
static void cryptominisat5_bench(benchmark::State& state)
{
  launch_bench("cryptominisat5 %I > %O");
}

static void cryptominisat5_simple_bench(benchmark::State& state)
{
  launch_bench("cryptominisat5_simple %I > %O");
}

static void glucose_simp_bench(benchmark::State& state)
{
  launch_bench("glucose-simp %I > %O");
}

static void glucose_syrup_bench(benchmark::State& state)
{
  launch_bench("glucose-syrup %I > %O");
}

static void picosat_bench(benchmark::State& state)
{
  launch_bench("picosat %I > %O");
}
////////////////////////      SAT SOLVERS    /////////////////////////////////

int main(int argc, char** argv)
{
  // Check arguments, get the test and the expected result
  if (argc < 3 || argc > 4)
  {
    std::cerr << "./fastSAT <test> <function_to_bench> [<nbstate>]"
      << std::endl;
    return 1;
  }

  // Get the test and the number of states if given
  test = std::string(argv[1]);
  if (argc == 4)
    nbstates = std::stoi(argv[3]);

  // Mark the function that will be run
  if (!strcmp(argv[2], "cryptominisat5"))
    bench(cryptominisat5_bench);
  if (!strcmp(argv[2], "cryptominisat5_simple"))
    bench(cryptominisat5_simple_bench);
  if (!strcmp(argv[2], "glucose-simp"))
    bench(glucose_simp_bench);
  if (!strcmp(argv[2], "glucose-syrup"))
    bench(glucose_syrup_bench);
  if (!strcmp(argv[2], "picosat"))
    bench(picosat_bench);

  // Launch the bench
  ::benchmark::RunSpecifiedBenchmarks();
}
