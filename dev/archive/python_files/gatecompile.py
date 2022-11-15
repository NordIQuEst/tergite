#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import numpy as np
import qiskit.circuit as circuit
import qiskit.compiler as compiler
import qiskit.pulse as pulse
from qiskit.visualization.pulse_v2.stylesheet import IQXDebugging, IQXSimple

from qiskit.providers.tergite import Tergite

# In[ ]:


chalmers = Tergite.get_provider()
backend = chalmers.get_backend("PinguOpenPulse_characterized")
backend.set_options(shots=1024)


# In[ ]:


backend.calibration_table


# In[ ]:


import rich

rich.print(backend.target.instruction_schedule_map())


# In[ ]:


# this chip has 5 qubits, but we will only use 4, meaning the last one will be used as ancilla
qc = circuit.QuantumCircuit(4, 4)
qc.barrier([0, 1, 2, 3])
qc.reset(1)
qc.reset(2)
qc.reset(3)
qc.h(2)
qc.h(2)  # note that this is optimized away, since HH = I
qc.h(3)  # this will transpile to ZXZ
qc.rx(np.pi / 4, 1)  # we can also do arbitrary rotations around x-axis
qc.measure([1, 2, 3], [1, 2, 3])
qc.draw()


# In[ ]:


tc = compiler.transpile(qc, backend=backend)
tc.draw()


# In[ ]:


sched = compiler.schedule(tc, backend=backend)
sched.draw()


# In[ ]:


rich.print(backend.make_qobj(sched, meas_level=1))
