from Problem import Problem
from GreedSearch import GreedSearch
from GRASP import GRASP

import pandas as pd
import time
import multiprocessing
import sys

seed = 0
max_exec_time_per_run_in_minutes = 1
max_exec_time_per_run_in_seconds = 60.0 * max_exec_time_per_run_in_minutes
n_cores = 1
result_file_name = "grasp_results.csv"


  ## Define a function to run GRASP


def simple_grasp_run(args):
  global seed
  problem, alpha, k, max_it, no_upt, start_incr, max_time, solve = args
  print('GRASP Started: Problem: ', problem.instance_name)  
  grasp = GRASP(problem, None, seed)
  start_time = time.time()
  grasp_tour, step, last_update = grasp.run(alpha, k, max_it, no_upt, start_incr, max_time, solve)
  end_time = time.time()
  grasp_cost = problem.evaluate(grasp_tour)
  print('GRASP Done: Problem: ', problem.instance_name)  
  return grasp_cost, end_time-start_time, grasp_tour, step, last_update


  ### Start the main problem ###


if __name__== '__main__' :

  if len(sys.argv) != 6:
    print("É necessario informar:")
    print("A quantidade de instancias a serem avaliadas")
    print("A seed para gerar os números aleatorios")
    print("O tempo máximo de execução de cada algoritmo em uma instancia, em minutos")
    print("O número máximo de execuções que podem rodar em paralelo")
    print("O nome do arquivo de saida com os resultados dos algoritmos")
    sys.exit(1)

  ### Set the seed to the random number generator ###
  ### Set the max time per run of algorithm ###
  ### Get the number of available cores ###

  qtd_instancias = int(sys.argv[1])
  seed = int(sys.argv[2])
  max_exec_time_per_run_in_minutes = float(sys.argv[3])
  max_exec_time_per_run_in_seconds = 60.0 * max_exec_time_per_run_in_minutes
  n_cores = int(sys.argv[4])
  result_file_name = sys.argv[5]


  ### Load instance list ###


  table_problems = pd.read_csv('TSP - PCV Instancias TSPLIB.csv')

  # select only some of the instances (brazil58 == 17)
  selected = table_problems.iloc[:17, :].copy()

  # set the path to the instance files
  Problem.files_path = '30 selected instances/'

  # get the start time of loading the instances
  start_time = time.time()
  # load the instances
  problems = [Problem(name) for name in selected['Nome']]
  # get the end time of loading the instances
  end_time = time.time()
  # get the name of the last instance
  print(problems[-1].instance_name)
  # print the time to load the instances
  print('Total time to load the instances: ', end_time-start_time, 'seconds')


  ### Generate a greed search ###


  greeds = []
  greeds_tours = []
  for problem in problems:
    start_time = time.time()
    greed_tour = GreedSearch.search(problem)
    end_time = time.time()
    greed_cost = problem.evaluate(greed_tour)
    greeds.append(greed_cost)
    greeds_tours.append(greed_tour)
  selected['Greed Cost'] = greeds
  selected['Greed Tour'] = [vals for vals in greeds_tours]


  ### Run GRASP on the instances in parallel ###


  reversed_problems = list(reversed(problems))
  reversed_greed_solves = list(reversed(greeds_tours))
  grasp_inputs = [(problem, 0.0, 3, 1000, 500, 10, max_exec_time_per_run_in_seconds, reversed_greed_solves[i]) for i, problem in enumerate(reversed_problems)]
  grasp = []

  start_time = time.time()
  with multiprocessing.Pool(n_cores) as p:
    grasp = p.map(simple_grasp_run, grasp_inputs)
  end_time = time.time()

  print('Total time to run grasp: ', end_time-start_time, 'seconds')
  selected['GRASP Cost'] = [vals[0] for vals in reversed(grasp)]
  selected['GRASP Time'] = [vals[1] for vals in reversed(grasp)]
  selected['GRASP Tour'] = [vals[2] for vals in reversed(grasp)]
  selected['GRASP Iters'] = [vals[3] for vals in reversed(grasp)]
  selected['GRASP No_Upt'] = [vals[4] for vals in reversed(grasp)]

  selected.to_csv(result_file_name, index=False)
  sys.exit(0)