import sys
import json
import argparse

''' Global variables for table state and parameters '''
nn = []        # List of thresholds per stage
mm = []        # List of multipliers per stage
k_stage = 0    # Current stage (1-based)
n_auth = 0     # Number of real elements in array
m_cap = 0      # Current capacity of array
y = []         # The array values (keys+ dummies)
mask = []      # True if position holds a real key, False for dummy
head = 0       # Starting index for circular layout
auth_list = [] # Sorted list of real keys

def bisect_left(a, x):
    ''' Binary search to find leftmost position for x in sorted list a  '''
    lo, hi = 0, len(a)
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] < x:
            lo = mid + 1
        else:
            hi = mid
    return lo

def insort(a, x):
    ''' Insert x into sorted list a at correct position '''
    idx = bisect_left(a, x)
    a.insert(idx, x)


def recalc_head():
    ''' Update head to point to minimal real key in array '''
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
    ''' Initialize the sparse array table for stage and initial key '''
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
    ''' Print the table, marking the head position using > <.'''
    parts = []
    for i, val in enumerate(y):
        s = repr(val)
        if i == head:
            s = f">{s}<"
        parts.append(s)
    print("[" + ", ".join(parts) + "]")

def rotated():
    ''' Return array and mask rotated so head is first '''
    rot_y = [y[(head + i) % m_cap] for i in range(m_cap)]
    rot_mask = [mask[(head + i) % m_cap] for i in range(m_cap)]
    return rot_y, rot_mask

def lookup(key):
    ''' Look up key: returns (found, position to find or insert) '''
    rot_y, rot_mask = rotated()
    idx = bisect_left(rot_y, key)
    found = False
    pos = None
    # Scan for key among possibly multiple duplicates
    for j in range(idx, idx + m_cap):
        j_mod = j % m_cap
        if rot_y[j_mod] != key:
            break
        if rot_mask[j_mod]:
            found = True
            pos = (head + j_mod) % m_cap
            break
    if not found:
        insert_idx = idx if idx <= m_cap else m_cap
        pos = (head + insert_idx) % m_cap
    return found, pos

def rebuild(new_stage):
    ''' Rebuild the array for new stage (resize and redistribute keys) '''
    global k_stage, m_cap, y, mask
    old_auth = sorted(auth_list)
    old_n = n_auth
    k_stage = new_stage
    m_cap = int(nn[k_stage - 1] * mm[k_stage - 1])
    new_y = [None] * m_cap
    new_mask = [False] * m_cap
    positions = []
    
    # Place real keys at proportional positions
    for t in range(old_n):
        idx = (t * m_cap) // old_n
        positions.append(idx)
        new_y[idx] = old_auth[t]
        new_mask[idx] = True

    # Fill dummy regions between real keys
    for t in range(old_n):
        start = positions[t]
        end = positions[(t + 1) % old_n] + (m_cap if (t + 1) == old_n else 0)
        for pos in range(start + 1, end):
            new_y[pos % m_cap] = new_y[start]
    y[:] = new_y
    mask[:] = new_mask
    recalc_head()

def insert_key(key):
    ''' Insert key into the array (with shifting if collision, triggers rebuild if needed) '''
    global n_auth
    if n_auth == nn[k_stage]:
        rebuild(k_stage + 1)
    found, pos = lookup(key)
    
    if found:
        recalc_head()
        return
        
    if not mask[pos]:
        y[pos] = key
        mask[pos] = True
        insort(auth_list, key)
        n_auth += 1
    else:
        shift_pos = pos
        while mask[shift_pos]:
            shift_pos = (shift_pos + 1) % m_cap
        idx = shift_pos
        while idx != pos:
            prev_idx = (idx - 1) % m_cap
            y[idx] = y[prev_idx]
            mask[idx] = True
            idx = prev_idx
        y[pos] = key
        mask[pos] = True
        insort(auth_list, key)
        n_auth += 1
    recalc_head()
    
def main():
    ''' main(): reads actions from JSON, applies them, and prints state '''
    parser = argparse.ArgumentParser()
    parser.add_argument('test')
    args = parser.parse_args()
    with open(args.test) as f:
        data = json.load(f)
    y.clear()
    mask.clear()
    init_table(data['nn'], data['mm'], data['k'], data['x'])
    print_create(data['x'])
    for act in data['actions']:
        cmd = act['action']
        key = act['key']
        print(f"{cmd.upper()} {key}")
        if cmd == 'insert':
            insert_key(key)
        elif cmd == 'lookup':
            found, pos = lookup(key)
            if found:
                print(f"Key {key} found at position {pos}.")
            else:
                print(f"Key {key} not found. It should be at position {pos}.")
        print_table()

if __name__ == '__main__':
    main()
