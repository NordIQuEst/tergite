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

from qiskit.providers import BaseJob, JobStatus
from qiskit.result import Result
from collections import Counter
import requests
from .config import MSS_URL, REST_API_MAP
from pathlib import Path


class Job(BaseJob):
    def __init__(self, backend, job_id: str, qobj):
        super().__init__(backend, job_id)
        self._qobj = qobj
        self._backend = backend
        self._status = JobStatus.INITIALIZING
        self._result = None
        self._download_url = None

    def qobj(self):
        return self._qobj

    def backend(self):
        return self._backend

    def status(self):
        print("Tergite: Job status() not implemented yet")
        return self._status

    def cancel(self):
        print("Tergite: Job cancel() not implemented yet")
        return None

    def result(self):
        if not self._result:
            JOBS_URL = MSS_URL + REST_API_MAP["jobs"]
            job_id = self.job_id()
            response = requests.get(JOBS_URL + "/" + job_id + REST_API_MAP["result"])

            if response:
                self._response = response  # for debugging
                memory = response.json()["memory"]
            else:
                return self._result

            # We currently measure all qubits and ignore classical registers.
            # Also, only 1 experiment per qobj is supported at the moment.
            data = {"counts": dict(Counter(memory)), "memory": memory}

            qobj = self.qobj()

            experiment_results = []
            experiment_results.append(
                {
                    "name": qobj.experiments[0].header.name,
                    "success": True,
                    "shots": qobj.config.shots,
                    "data": data,
                    "header": qobj.experiments[0].header.to_dict(),
                }
            )

            experiment_results[0]["header"][
                "memory_slots"
            ] = self._backend.configuration().n_qubits

            self._result = Result.from_dict(
                {
                    "results": experiment_results,
                    "backend_name": self._backend.name(),
                    "backend_version": self._backend.version(),
                    "qobj_id": 0,
                    "job_id": self.job_id(),
                    "success": True,
                }
            )

        return self._result

    # NOTE: This API is WIP
    def download_logfile(self, save_location: str):
        # TODO: improve error handling
        if not self._download_url:
            JOBS_URL = MSS_URL + REST_API_MAP["jobs"]
            job_id = self.job_id()
            response = requests.get(
                JOBS_URL + "/" + job_id + REST_API_MAP["download_url"]
            )
            print(response.json())

            if response:
                self._response = response  # for debugging
                self._download_url = response.json()
            else:
                return None

        response = requests.get(self._download_url)
        if response:
            file = Path(save_location) / (self.job_id() + ".hdf5")
            with file.open("wb") as destination:
                destination.write(response.content)

        return None

    def submit(self):
        print("Tergite: Job submit() is deprecated")
        return None
