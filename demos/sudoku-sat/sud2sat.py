# --------------------------------------------------------
# sud2say.py
# 
# Given Sudoku puzzle, generates DIMACs input format
# for SAT solver (either miniSAT or Gsat).
# 
# It dumps result out into the terminal; it is 
# recommended that you pipe it, or redirect into a 
# seperate file to run on SAT solver.
#
# usage: python3 sud2sat.py <file_name> [-gsat | -minisat] 
#            -extended=[true | false]
#
# Author: Jordan Jay, Francisco Moon
# Last Modified : Mar.28 2017
# --------------------------------------------------------

import sys

exceptions = ['0', '.', '*', '?', "\n"]
gsat = False
extended = False
file_name = ""
result_file = open('output', 'w')

# input argument check, 
def read_input():
  global gsat, file_name, extended

  if len(sys.argv) < 4:
    print_input_error("Incorrect argument number.")

  if (sys.argv[2] == '-gsat'):
    gsat = True
  elif (sys.argv[2] == '-minisat'):
    gsat = False
  else:
    print_input_error("Incorrect argument")

  if (sys.argv[3] == '-extended=true'):
    extended = True
  elif (sys.argv[3] == '-extended=false'):
    extended = False
  else:
    print_input_error("Incorrect argument")

  file_name = sys.argv[1]

# handles argument errors
def print_input_error(msg = ""):
  print("Error: {}".format(msg))
  print("usage: python3 sud2sat.py <file_name> [-gsat | -minisat] -extended=[true | false]")
  exit(1)

# attempt to read and convert puzzle into DIMACs
def read_puzzle():
  result = []
  f = open(file_name, 'r')

  count = 0
  row = 1
  col = 1

  puzzle = f.read().replace("\n", "")
  for symbol in puzzle:
    if col == 10:
      row += 1
      col = 1
    if symbol not in exceptions:
      input_num = 81*(int(row)-1) + 9*(int(col)-1) + (int(symbol)-1) + 1
      if gsat:
        result.append("( " + str(input_num) + " )")
      else:
        result.append(str(input_num) + " 0" + "\n")
      #result.append(str(row)+ str(col) + symbol + " 0")
      count += 1
    col += 1

  #This total clauses is dependent on using the minimal encoding
  total_clauses = 8829 + count
  if extended:
    total_clauses = 11988 + count
  if not gsat:  
    result_file.write("p cnf " + str(729) + " " + str(total_clauses) + "\n")

  for i in result:
      result_file.write(i)

# Each cell should contain at least one number
def cell_atleast_one():
  #if not gsat:
    #print("p cnf 729 81")
  result = []
  for i in range(1, 10):
    for j in range(1, 10):
      for k in range(1, 10):
        input_num = 81*(i-1) + 9*(j-1) + (k-1) + 1
        result.append("{} ".format(input_num))
      if gsat:
        result_file.write("( " + "".join(result) + ")")
      else:  
        result_file.write("".join(result) + "0" + "\n")
      result = []

# Each number appears at most once in every row
def row_atmost_once():
  #if not gsat:
    #print("p cnf 729 2916")
  for i in range(1, 10):
    for k in range(1, 10):
      for j in range(1, 9):
        for l in range(j+1, 10):
          first_num = 81*(i-1) + 9*(j-1) + (k-1) + 1
          second_num = 81*(i-1) + 9*(l-1) + (k-1) + 1
          #print("-{}{}{} -{}{}{} 0".format(i,j,k,i,l,k))
          if gsat:
            result_file.write("( -{} -{} )".format(first_num, second_num))
          else:
            result_file.write("-{} -{} 0".format(first_num, second_num) + "\n")

# Each number appears at most once in every column
def col_atmost_once():
  #if not gsat:
    #print("p cnf 729 2916")
  for j in range(1, 10):
    for k in range(1, 10):
      for i in range(1,9):
        for l in range(i+1, 10):
          first_num = 81*(i-1) + 9*(j-1) + (k-1) + 1
          second_num = 81*(l-1) + 9*(j-1) + (k-1) +1 
          #print("-{}{}{} -{}{}{} 0".format(i,j,k,l,j,k))
          if gsat:
            result_file.write("( -{} -{} )".format(first_num, second_num))
          else:
            result_file.write("-{} -{} 0".format(first_num, second_num) + "\n")

# Each number appears at most once in every 3x3 subgrid
def three_square_atmost_once():
  #if not gsat:
    #print("p cnf 729 2916")
  for k in range(1, 10):
    for a in range(0, 3):
      for b in range(0, 3):
        for u in range(1, 4):
          for v in range(1, 3):
            for w in range(v+1, 4):
              first_num = 81*((3*a+u)-1) + 9*((3*b+v)-1) + (k-1) +1 
              second_num = 81*((3*a+u)-1) + 9*((3*b+w) -1) + (k-1) + 1
              #print("-{}{}{} -{}{}{} 0".format((3*a+u), (3*b+v), k, (3*a+u), (3*b+w), k))
              if gsat:
                result_file.write("( -{} -{} )".format(first_num, second_num))
              else:
                result_file.write("-{} -{} 0".format(first_num, second_num) + "\n")

  for k in range(1, 10):
    for a in range(0, 3):
      for b in range(0, 3):
        for u in range(1, 3):
          for v in range(1, 4):
            for w in range(u+1, 4):
              for t in range(1, 4):
                first_num = 81*((3*a+u)-1) + 9*((3*b+v)-1) + (k-1) +1 
                second_num = 81*((3*a+w)-1) + 9*((3*b+t) -1) + (k-1) + 1
                #print("-{}{}{} -{}{}{} 0".format((3*a+u), (3*b+v), k, (3*a+w), (3*b+t), k))
                if gsat:
                  result_file.write("( -{} -{} )".format(first_num, second_num))
                else:
                  result_file.write("-{} -{} 0".format(first_num, second_num) + "\n")

# *************************************************
# The functions below are for the extended encoding
# The extended encoding explicity asserts that each 
# entry in the grid has exactly one number
# *************************************************

# There is at most one number in each entry
def cell_atmost_once():
  #if not gsat:
    #print("p cnf 729 2916")
  for x in range(1, 10):
    for y in range(1,10):
      for z in range(1,9):
        for i in range(z+1, 10):
          first_num = 81*(x-1) + 9*(y-1) + (z-1) + 1
          second_num = 81*(x-1) + 9*(y-1) + (i-1) + 1
          result_file.write("-{} -{} 0".format(first_num, second_num) + "\n")

# Each number appears at least once in each row
def row_atleast_once():
  #if not gsat:
    #print("p cnf 729 81")
  result = []
  for y in range(1,10):
    for z in range(1,10):
      for x in range(1,10):
        input_num = 81*(x-1) + 9*(y-1) + (z-1) + 1
        result.append("{} ".format(input_num))
      result_file.write("".join(result) + "0" + "\n")
      result = []

# Each number appears at least once in each column
def col_atleast_once():
  #if not gsat:
    #print("p cnf 729 81")
  result = []
  for x in range(1, 10):
    for z in range(1, 10):
      for y in range(1, 10):
        input_num = 81*(x-1) + 9*(y-1) + (z-1) + 1
        result.append("{} ".format(input_num))
      result_file.write("".join(result) + "0" + "\n")
      result = []        

# Each number appears at last once in each 3x3 sub-grid
def three_square_atleast_once():
  #if not gsat:
    #print("p cnf 729 81")
  result = []
  for z in range(1, 10):
    for i in range(0, 3):
      for j in range(0, 3):
        for x in range(1, 4):
          for y in range(1, 4):
            input_num = 81*((3*i+x)-1) + 9*((3*j+y)-1) + (z-1) + 1
            result.append("{} ".format(input_num))
        # here it doesn't seem to follow the pdf, but only way to make nine-ary clauses
        result_file.write("".join(result) + "0" + "\n")
        result = []

def main():

  read_input()
  read_puzzle()

  cell_atleast_one()
  row_atmost_once()
  col_atmost_once()
  three_square_atmost_once()

  # The functions below are called for the extended encoding
  # They are unnecessary for solving sudoku problems, as the minimal encoding works
  if extended:
    cell_atmost_once()
    row_atleast_once()
    col_atleast_once()
    three_square_atleast_once()

  if gsat:
    result_file.write("%\n0")

if __name__ == '__main__':
  main()