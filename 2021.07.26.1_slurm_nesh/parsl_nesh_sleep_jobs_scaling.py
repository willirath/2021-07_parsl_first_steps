#!/usr/bin/env python3

import parsl
import logging
import os
from parsl.app.app import python_app
from parsl.config import Config
from parsl.providers import SlurmProvider
from parsl.launchers import SrunLauncher
from parsl.executors import HighThroughputExecutor
from parsl.addresses import address_by_interface

# create config adapted from example configs
config = Config(
    executors=[
        HighThroughputExecutor(
            label='NESH_01',
            address=address_by_interface('ib0'),
            cores_per_worker=1,
            provider=SlurmProvider(
                'cluster',
                nodes_per_block=1,
                init_blocks=0,
                max_blocks=10,
                min_blocks=1,
                scheduler_options='',
                worker_init='',
                launcher=SrunLauncher(),  # (overrides="--ntasks=1 --exclusive"), ???
                walltime='00:10:00',
                cmd_timeout=120,
            ),
        )
    ],
    strategy='htex_auto_scale',
)
parsl.load(config)

# Set up logging according to parsl FAQ
parsl.set_stream_logger()
parsl.set_file_logger('parsl_nesh_sleep_jobs_scaling.log', level=logging.DEBUG)

logger = logging.getLogger("main script")


@python_app
def sleep_some_time(sleep_for=2):
    from time import sleep
    sleep(sleep_for)
    return f"slept for {sleep_for} seconds"


single_run = sleep_some_time()
print(single_run.result())


many_runs = list(map(lambda n: sleep_some_time(2 + n / 100), range(1024)))
gathered_results = list(map(lambda f: f.result(), many_runs))
logger.debug(gathered_results)

