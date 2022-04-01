import random as random
from qiskit.circuit.random import random_circuit
from qiskit import QuantumCircuit, transpile
from qiskit.test.mock import FakeCasablanca
from qiskit.converters import dagdependency_to_circuit, circuit_to_dagdependency
import matplotlib.pyplot as plt
from qiskit.quantum_info import Operator


import os

os.makedirs("../DepthReductionPass", exist_ok=True)
os.makedirs("../DepthReductionPass/Errors", exist_ok=True)
# construct random circuits

normal, conv = [], []
hits = 0
change = 0
err = 0
errors = 0
casb = FakeCasablanca()

largest_change = 0
substantial = 0
trials = 200
for i in range(trials):

    qc = random_circuit(num_qubits=5, depth=10)
    qc = transpile(qc, optimization_level=3, backend=casb)

    # now make a dependency
    dd = circuit_to_dagdependency(qc)
    qc_conv = dagdependency_to_circuit(dd)

    d1 = qc.depth()
    d2 = qc_conv.depth()

    conv.append(d2)
    normal.append(d1)

    if d2 < d1:
        hits += 1
        change += d1 - d2
        largest_change = max(largest_change, d1 - d2)

        # if > 5% change in the depth
        if d1 - d2 >= int(0.04 * qc.depth()):
            substantial += 1

    if d2 > d1:
        change -= d2 - d1
        err += 1

    if Operator(qc) != Operator(qc_conv):
        print("Miss :(")
        qc.draw("mpl", filename=f"../DepthReductionPass/Errors/original_{errors}.png")
        qc_conv.draw("mpl", filename=f"../DepthReductionPass/Errors/converted_{errors}.png")
        errors += 1

print("Percentage better :", round(hits / trials, 3) * 100)
print("Percentage worse :", round(err / trials, 3) * 100)
print("Avg. depth change :", round(change / trials, 4))
print("Largest change :", largest_change)
print("Wrong re-construction :", errors)
print("Circuits with > 4% change ", substantial)


plt.figure(figsize=(14, 8))
plt.title("Depth of the circuits", fontsize=17)
plt.xlabel("Circuit index")
plt.ylabel("Circuit depth")
plt.plot(range(trials), normal, marker="o", alpha=0.7, label="Normal circuits")
plt.plot(range(trials), conv, marker="o", alpha=0.7, label="Converted circuits")

plt.grid()
plt.legend()

plt.savefig(fname="../DepthReductionPass/stats_circs.png", dpi=200)
