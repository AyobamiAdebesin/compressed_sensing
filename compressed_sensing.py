# -*- coding: utf-8 -*-
"""compressed_sensing.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1k-LyQ1J-9DiNqzFCCtFlhs4WA6wl94n9
"""

# Compressed Sensing
import numpy as np
import scipy
import time
from scipy.optimize import minimize

def initialize_vector(m: int, n: int, p: int):
  """
  Initialize an n-dimensional vector and m by n dimensional matrix
  """
  if not m or not isinstance(m, int):
    raise ValueError("Input a size for your matrix and vector")
  x = np.zeros(shape=(n, 1))
  for i in range(p):
    random_number = np.random.uniform(1, 100)
    random_idx = np.random.randint(low=0, high=1000)
    x[random_idx] = random_number
  A = np.random.normal(0, 1, size=(m, n))
  assert x.shape == (n, 1), "x must have a shape of (n, 1)"
  assert A.shape == (m, n), "A must have a shape of (m, n)"
  return x, A

def normalize_matrix(A):
  """ Normalize each column of the matrix with L2 norm """
  if not isinstance(A, np.ndarray):
    raise TypeError("A must be a numpy array")
  A_new = scipy.linalg.norm(A, axis=0, keepdims=True)
  return A_new

def transform_x(A, x):
  """
  Apply a transformation to x: m*n x n*1 = m*1
  b = Ax
  """
  if not isinstance(A, np.ndarray) or not isinstance(x, np.ndarray):
    raise TypeError("A and x must be a numpy arrays")
  if A.ndim != 2 or x.ndim != 2:
    raise TypeError("A and x must be 2-dimensional arrays")
  b = np.dot(A, x)
  return b

# Define the L1 norm function
def l1_norm(x):
  """ Define the first component of the objective function; phi(x)"""
  if not isinstance(x, np.ndarray):
    raise TypeError("x must be a numpy array")
  if x.ndim != 2:
    x = x.reshape((x.shape[0], 1))
  phi_x = scipy.linalg.norm(x, ord=1)
  #assert (phi_x != np.ndarray), "phi_x must be a real number"
  return phi_x


# Define f(x)
def f_x(A, x, b, lambd):
  """ Define the second component of the objective function; f(x) """
  print("Inside f(x).........About to compute the second component of the objective function; f(x)")
  if not isinstance(A, np.ndarray) or not isinstance(x, np.ndarray) or not isinstance(b, np.ndarray):
    raise TypeError("A, x, and b must be numpy arrays")
  if A.ndim != 2 or x.ndim != 2 or b.ndim != 2:
    raise TypeError("A, x and b must be 2-dimensional arrays")
  fx = 0.5 * lambd * scipy.linalg.norm(np.dot(A, x) - b, ord=2)**2
  #assert (fx != np.ndarray), "f(x) must be a real number"
  print("Done calculating f(x)................")
  return fx


# Define the gradient of f(x)
def grad_f(A, x, b, lambd):
  """ Return the gradient of f(x) """
  if not isinstance(A, np.ndarray) or not isinstance(x, np.ndarray) or not isinstance(b, np.ndarray):
    raise TypeError("A, x, and b must be numpy arrays")
  if A.ndim != 2 or x.ndim != 2 or b.ndim != 2:
    raise TypeError("A, x and b must be 2-dimensional arrays")
  gradf = lambd * np.dot(A.T, (np.dot(A, x) - b))
  return gradf

# Define the objective function
def objective_function(A, x, b, lambd):
  """
  Define the objective function: phi(x) + f(x)
  """
  print("Inside objective function......About to calculate objective function")
  if not isinstance(A, np.ndarray) or not isinstance(x, np.ndarray) or not isinstance(b, np.ndarray):
    raise TypeError("A, x, and b must be numpy arrays")
  if A.ndim != 2 or x.ndim != 2 or b.ndim != 2:
    raise TypeError("A, x and b must be 2-dimensional arrays")
  obj_func = l1_norm(x) + f_x(A, x, b, lambd)
  print("Done computing objective function..........")
  return obj_func

#Define function to minimize
def func_minimize(x, z):
  return l1_norm(x) + (0.5 * (scipy.linalg.norm(x-z, ord=2)**2))

# Define the proximal operator
def proximal_operator(z, initial_guess):
  """ Define the proximal operator function

  Args:
    z - the input vector; phi(x) + 0.5 ||x-z||**2
    z will be the vector we obtain from computing x_k - tau_k*grad_f(x_k)

  Returns:
    The value of x that minimizes phi(x) + 0.5 * ||x-z||**2
  """
  print("About to compute proximal operator..........")

  result = minimize(lambda x: func_minimize(x, z), x0 = initial_guess, method='L-BFGS-B')
  print("Done computing proximal operator..........")
  print(f"Shape of output returned by proximal operator: {result.x.shape}")
  return result.x

# Define the learning rate
def learning_rate(lambd, A):
  """
  Define the learning rate; tau_k

  learning_rate - a real number between 0 and 2/L
  where L = lambd * ||A.T * A||
  """
  L = lambd * scipy.linalg.norm(np.dot(A.T, A))
  return np.random.uniform(0, 2/L)

def proximal_gradient(lambd, A, b):
  """
  Solve the optimization problem by proximal gradient

  min_x [phi(x) + f(x)]

  phi(x) = ||x||_1 => L1 norm of x
  f(x) = lambda/2 (||Ax-b||^2) => L2 norm of Ax-b

  lambda - user chosen parameter
  """
  if not isinstance(A, np.ndarray) or not isinstance(b, np.ndarray):
    raise TypeError("A, x, and b must be numpy arrays")
  if A.ndim != 2 or b.ndim != 2:
    raise TypeError("A, x and b must be 2-dimensional arrays")

  # Initialize the learning rate
  learn_rate = learning_rate(lambd, A)

  # Initialize random x_0 as the starting point
  x_i = np.random.randn(1000, 1)
  # Initialize the number of iteration steps
  ITER_STEPS = 50
  for i in range(ITER_STEPS):
    f_xi = f_x(A, x_i, b, lambd)
    gradf = grad_f(A, x_i, b, lambd)
    z = x_i - (learn_rate*gradf)
    x_i = proximal_operator(z, initial_guess=x_i.flatten())

  return x_i

# Testing our implementation

#Initialize vector and matrix
x_old, A = initialize_vector(m=100, n=1000, p=10)

# Transform x into b
b = transform_x(A, x_old)
LAMBDA = 0.1

x_star = proximal_gradient(lambd=LAMBDA, A=A, b=b)

