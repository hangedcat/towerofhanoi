import random

class Stack:

    def __init__(self):
        self._items: list[int] = []

    def is_empty(self) -> bool:
        return len(self._items) == 0

    def pop(self) -> int:
        if self.is_empty():
            raise IndexError('Cannot pop from an empty stack.')
        return self._items.pop()

    def push(self, item: int) -> None:
        self._items.append(item)

    def peek(self) -> int:
        if self.is_empty():
            raise IndexError('Cannot peek at an empty stack.')
        return self._items[-1]
    
    def clear(self) -> None:
        self._items.clear()

    def __len__(self) -> int:
        return self.size()

    def __str__(self) -> str:
        return f'Stack({self._items})'
    
    def __repr__(self) -> str:
        return f'Stack({self._items})'
    
    def __lt__(self, other: Stack) -> bool:
        if not isinstance(other, Stack):
            return NotImplemented
        return self.size() < other.size()
    
    def __eq__(self, other: Stack) -> bool:
        if not isinstance(other, Stack):
            return NotImplemented
        return self.size() == other.size()
    
    def __getitem__(self, index: int) -> int:
        if not isinstance(index, int):
            raise TypeError("Stack indices must be integers")
        return self._items[index]

    def size(self) -> int:
        return len(self._items)

    def is_sorted(self):
        return all(self._items[i] > self._items[i+1] for i in range(len(self._items) - 1))

class TowerOfHanoi:

    def __init__(self, **kwargs: Stack) -> None:
        self._pegs: dict[str, Stack] = kwargs
        self.source: str|None = None

    def pegs(self) -> list[str]:
        return list(self._pegs.keys())

    def size(self) -> int:
        return len(self._pegs.keys())
    
    def count(self) -> int:
        disk_number = len(list(peg[i] for peg in self._pegs.values() for i in range(len(peg))))
        return disk_number
    
    def clear(self) -> None:
        for peg in self._pegs:
            self._pegs[peg].clear()

    def setup(self, n_disk: int, target = None) -> None:
        self.clear()
        disks = [i for i in range(n_disk, 0, -1)]
        self.source = target if (target in self.pegs()) else random.choice(self.pegs())
        for disk in disks:
            self._pegs[self.source].push(disk)
    
    def is_sorted(self, target) -> bool:
        max_disk = max(peg[i] for peg in self._pegs.values() for i in range(len(peg))) if self._pegs else 0
        if (len(self._pegs[target]) == max_disk) and self._pegs[target].is_sorted():
            return True
        return False

    def move(self, source: str, target: str) -> int:
        if source not in self._pegs or target not in self._pegs:
            raise ValueError(f"Invalid peg: {source} or {target}")
        if self._pegs[source].is_empty():
            raise ValueError(f"Cannot move from empty peg {source}")
        if not self._pegs[target].is_empty() and self._pegs[target].peek() < self._pegs[source].peek():
            raise ValueError("Cannot place larger disk on smaller disk")
        disk = self._pegs[source].pop()
        self._pegs[target].push(disk)
        return disk

    def __str__(self):
        max_height = max(peg[i] for peg in self._pegs.values() for i in range(len(peg))) if self._pegs else 0

        turned = {peg: [] for peg in self._pegs}
        for i in range(max_height - 1, -1, -1):
            for peg in self._pegs:
                try:
                    turned[peg].append([self._pegs[peg][i]])
                except IndexError:
                    turned[peg].append([0])  

        lines = []
        for level in range(max_height):
            line = ""
            for peg in sorted(self._pegs.keys()):
                disk = turned[peg][level]
                line += f"{disk}  "
            lines.append(line)
        return "\n".join(lines)
    
    def solve(self, source: str, target: str, aux: str, n: int | None = None):
        if n is None:
            n = self._pegs[source].size()
        logs = []
        self._solve_recursive(n, source, target, aux, logs)
        return logs

    def _solve_recursive(self, n, source, target, aux, logs):
        if n == 0: return
        self._solve_recursive(n - 1, source, aux, target, logs)
        disk = self.move(source, target)
        logs.append(f"{source}->{target}:{disk}")
        self._solve_recursive(n - 1, aux, target, source, logs)

for n in [1, 2, 3, 4, 5, 10]:
    tower = TowerOfHanoi(A=Stack(), B=Stack(), C=Stack())
    tower.setup(n_disk=n, target='A')
    logs = tower.solve(source='A', target='C', aux='B', n=n)
    print(f"n={n}: predicted={2**n - 1}, actual={len(logs)}, "f"match={'OK' if len(logs) == 2**n - 1 else 'FAIL'}")