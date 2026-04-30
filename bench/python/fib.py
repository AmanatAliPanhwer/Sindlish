import sys

def fib(n):
    if n < 2: return n
    return fib(n-1) + fib(n-2)

if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    print(fib(n))
