import sys
import json
import argparse

def bisect_left(a, x):
    '''
    Binary search to find leftmost position for x in sorted list a
    '''
    lo, hi = 0, len(a)
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] < x:
            lo = mid + 1
        else:
            hi = mid
    return lo

def insort(a, x):
    '''
    Insert x into sorted list a at correct position
    '''
    idx = bisect_left(a, x)
    a.insert(idx, x)

# Global variables for table state and parameters
nn = []        # List of thresholds per stage
mm = []        # List of multipliers per stage
k_stage = 0    # Current stage (1-based)
n_auth = 0     # Number of real elements in array
m_cap = 0      # Current capacity of array
y = []         # The array values (keys+ dummies)
mask = []      # True if position holds a real key, False for dummy
head = 0       # Starting index for circular layout
auth_list = [] # Sorted list of real keys

def recalc_head():
    '''
    Update head to point to minimal real key in array 
    '''
    global head
    min_val = None
    for i in range(m_cap):
        if mask[i]:
            if min_val is None or y[i] < min_val:
                min_val = y[i]
    if min_val is None:
        head = 0
        return
    for i in range(m_cap):
        if mask[i] and y[i] == min_val:
            head = i
            return
 
def init_table(thresholds, multipliers, stage, initial_key):
    '''
    Initialize the sparse array table for stage and initial key
    '''
    global nn, mm, k_stage, n_auth, m_cap, y, mask, auth_list
    nn = thresholds
    mm = multipliers
    k_stage = stage
    n_auth = 1
    m_cap = int(nn[k_stage - 1] * mm[k_stage - 1])
    y[:] = [initial_key] * m_cap
    mask[:] = [False] * m_cap
    mask[0] = True
    auth_list[:] = [initial_key]
    recalc_head()

def print_create(initial_key):
    print(f"CREATE with k={k_stage}, n_k={nn}, m_k={mm}, key={initial_key}")
    print_table()

def print_table():
    '''
    Print the table, marking the head position using > <.
    '''
    parts = []
    for i, val in enumerate(y):
        s = repr(val)
        if i == head:
            s = f">{s}<"
        parts.append(s)
    print("[" + ", ".join(parts) + "]")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('test')
    args = parser.parse_args()
    with open(args.test) as f:
        data = json.load(f)
    y.clear()
    mask.clear()
    init_table(data['nn'], data['mm'], data['k'], data['x'])
    print_create(data['x'])

if __name__ == '__main__':
    main()
