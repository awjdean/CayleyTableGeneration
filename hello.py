import itertools
import time

# Example data
all_states = range(1000)
minimum_actions = range(100)

# Using itertools.product
start = time.time()
for state, action in itertools.product(all_states, minimum_actions):
    pass
end = time.time()
print("itertools.product:", end - start)

# Using nested loops
start = time.time()
for state in all_states:
    for action in minimum_actions:
        pass
end = time.time()
print("Nested loops:", end - start)
