# ---------------------------------------------------------
# sat2sud.py
#
# converter for sat format into sudoku puzzle
# in a read friendly form.
#
# It works for both miniSAT, and gsat
#
# usage: python3 sat2sud.py <file_name> [-gsat | -minisat]
#
# Authors: Jordan Jay, Francisco Moon
# Last Modified: Mar.29, 2017
# ---------------------------------------------------------

import sys, re

file_name = ""
gsat = False

def read_input():
  global gsat, file_name

  if len(sys.argv) < 3:
    print_error("Incorrect argument number")

  if (sys.argv[2] == '-gsat'):
    gsat = True
  elif (sys.argv[2] == '-minisat'):
    gsat = False
  else:
    print_error("Incorrect argument")

  file_name = sys.argv[1]

def print_error(msg = ""):
  print(msg)
  exit(1)

# Reads and Parses the file
def read_file():
  f = open(file_name, 'r')

  result = []
  if not gsat:
    solution = f.read().split()

    satisfiable = solution.pop(0)  #getting rid of the first element

    if(satisfiable == 'UNSATISFIABLE'):
      print_error("The given puzzle is not satisfiable")

  else:
    solution = f.read().strip().replace("\n","")
    solution = re.search("(list\* ['][()])(.*)(;;;)", solution)
    solution = solution.group(2).split()[:-1]

  # Getting rid of all values that are not greater than zero
  solved_board = []
  for element in solution:
    if(int(element) > 0):
      solved_board.append(element)

  # final_solution now contains the specific values for the sudoku puzzle, format later to look like a solved puzzle
  final_solution = []
  for element in solved_board:
    i = (int(element)/81) +1
    j = (int(element)/9) +1
    k = (int(element)%9)
    if k == 0:
      k = 9
    final_solution.append(k)

  # Formatting the output to be printed as a Sudoku board
  col = 0
  row = 0
  result = []
  for cell in final_solution:
    col += 1
    result.append(str(cell) + " ")
    if (col == 3 or col == 6):
      result.append("| ")
    if (col == 9):
      print("".join(result))
      result = []
      col = 0
      row += 1
      if (row == 3 or row ==6):
        print("- - - - - - - - - - -")
  

def main():
  read_input()
  read_file()

if __name__ == '__main__':
  main()