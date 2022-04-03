# This code is part of Qiskit.
#
# (C) Copyright IBM 2017, 2018.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

"""Cancel out self inverting multi qubit gates, symmetric in their qargs"""

from typing import List

from qiskit.circuit.library import SwapGate
from qiskit.dagcircuit import DAGCircuit
from qiskit.circuit import Gate
from .inverse_cancellation import InverseCancellation


class SymmetricCancellation(InverseCancellation):
    """Cancel Symmetric Gates when they occur back-to-
    back."""

    def __init__(self):
        """Initialize the SwapCancellation pass"""
        gates_to_cancel = [SwapGate()]
        super().__init__(gates_to_cancel)

    def _run_on_self_inverse(self, dag: DAGCircuit, self_inverse_gates: List[Gate]):
        """
        Run self-inverse gates on `dag`. Note that qubit set matters not the ordering
        in case of symmetric gates.

        Args:
            dag: the directed acyclic graph to run on.
            self_inverse_gates: list of gates who cancel themeselves in pairs

        Returns:
            DAGCircuit: Transformed DAG.
        """
        # Sets of gate runs by name, for instance: [{(H 0, H 0), (H 1, H 1)}, {(X 0, X 0}]
        gate_runs_sets = [dag.collect_runs([gate.name]) for gate in self_inverse_gates]
        for gate_runs in gate_runs_sets:
            for gate_cancel_run in gate_runs:
                partitions = []
                chunk = []
                for i in range(len(gate_cancel_run) - 1):
                    chunk.append(gate_cancel_run[i])
                    if set(gate_cancel_run[i].qargs) != set(gate_cancel_run[i + 1].qargs):
                        partitions.append(chunk)
                        chunk = []
                chunk.append(gate_cancel_run[-1])
                partitions.append(chunk)
                # Remove an even number of gates from each chunk
                for chunk in partitions:
                    if len(chunk) % 2 == 0:
                        dag.remove_op_node(chunk[0])
                    for node in chunk[1:]:
                        dag.remove_op_node(node)
        return dag
