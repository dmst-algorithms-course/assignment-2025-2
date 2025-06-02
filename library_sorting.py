import sys
import json
import argparse

# Global variables
nn = []
mm = []
k_stage = 0
n_auth = 0
m_cap = 0
y = []
mask = []
head = 0
auth_list = []

def init_table(thresholds, multipliers, stage, initial_key):
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
