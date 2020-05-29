# This code is part of Tergite
#
# (C) Copyright Miroslav Dobsicek 2020
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.


# this file is meant to be run interactively for object inspection
# python -i tests/job_on_tergite.py

from qiskit.providers.tergite import Tergite
from qiskit import *
from qiskit.visualization import plot_histogram

provider = Tergite.get_provider()
backend = provider.get_backend("pingu")

qr = QuantumRegister(2)
qc = QuantumCircuit(qr)
qc.cz(qr[0], qr[1])
qc.h(qr[0])

mytr = transpile(qc, backend)
myqobj = assemble(mytr, backend)

job = execute(mytr, backend)

plot_histogram(job.result().get_counts()).show()
