#include <benchmark/benchmark.h>

#pragma once

static void cryptominisat5_bench(benchmark::State& state);
static void cryptominisat5_simple_bench(benchmark::State& state);
static void glucose_simp_bench(benchmark::State& state);
static void glucose_syrup_bench(benchmark::State& state);
static void picosat_bench(benchmark::State& state);
