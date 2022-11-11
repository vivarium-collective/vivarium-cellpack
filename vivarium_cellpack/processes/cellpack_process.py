import os
import numpy as np

from pathlib import Path

from vivarium.core.process import Process
from vivarium.core.engine import Engine

import cellpack
from cellpack.bin.pack import initialize_environment

NAME = 'CELLPACK'

RELATIVE_MICRON = 0.001
BOUNDARY_BUFFER = 0.95


class CellpackProcess(Process):
    defaults = {
        'config': {
            'name': 'sparse-packing',
            'format': 'simularium',
            'inner_grid_method': 'trimesh',
            'live_packing': False,
            'ordered_packing': False,
            'out': 'out/',
            'overwrite_place_method': False,
            'place_method': 'spheresSST',
            'save_analyze_result': False,
            'show_grid_plot': False,
            'spacing': 4,
            'use_periodicity': False,
            'show_sphere_trees': False,
            'load_from_grid_file': True},

        # initial recipe
        'recipe': {
            'version': '1.0.0',
            'format_version': '2.0',
            'name': 'cellpack',
            'bounding_box': [[-1, -1, -1], [1, 1, 1]],
            'objects': {},
            'composition': {}}}

    def __init__(self, parameters=None):
        super().__init__(parameters)

        self.environment = initialize_environment(
            self.parameters['config'],
            self.parameters['recipe'])

        # self.environment.buildGrid(rebuild=True)
        self.environment.buildGrid(rebuild=False)
        self.environment.pack_grid(verbose=0, usePP=False)

    def ports_schema(self):
        ports = {}

        return ports

    def initial_state(self, config):
        return {}

    def next_update(self, timestep, state):
        print('in cellpack process next update')

        import ipdb; ipdb.set_trace()


        peroxisome_count = state[
            'composition']['membrane']['regions']['interior'][1]['count']
        peroxisome_leak = int(peroxisome_count * -0.1)

        update = {
            'composition': {
                'membrane': {
                    'regions': {
                        'interior': [
                            'nucleus',
                            {
                                'object': 'peroxisome',
                                'count': peroxisome_leak}]}}}}


def main():
    initial_config = {}

    initial_recipe = {
        'name': 'peroxisomes_vivarium',
        'bounding_box': [
            [-110, -45, -62],
            [110, 45, 62]],

        'objects': {
            'mean_membrane': {
                'type': 'mesh',
                'color': [
                    0.5,
                    0.5,
                    0.5
                ],
                'representations': {
                    'mesh': {
                        'path': 'https://www.dl.dropboxusercontent.com/s/4d7rys8uwqz72xy/',
                        'name': 'mean-membrane.obj',
                        'format': 'obj'
                    }
                }
            },
            'mean_nucleus': {
                'type': 'mesh',
                'color': [
                    0.25,
                    0.25,
                    0.25
                ],
                'representations': {
                    'mesh': {
                        'path': 'https://www.dl.dropboxusercontent.com/s/3194r3t40ewypxh/',
                        'name': 'mean-nuc.obj',
                        'format': 'obj'
                    }
                }
            },
            'peroxisome': {
                'jitter_attempts': 300,
                'type': 'single_sphere',
                'color': [
                    0.20,
                    0.70,
                    0.10
                ],
                'radius': 2.30
            }
        },

        'composition': {
            'bounding_area': {
                'regions': {
                    'interior': [
                        'membrane'
                    ]
                }
            },
            'membrane': {
                'object': 'mean_membrane',
                'count': 1,
                'regions': {
                    'interior': [
                        'nucleus',
                        {
                            'object': 'peroxisome',
                            'count': 121
                        }
                    ]
                }
            },
            'nucleus': {
                'object': 'mean_nucleus',
                'count': 1,
                'regions': {
                    'interior': []
                }
            }
        }
    }

    cellpack = CellpackProcess({
        'config': initial_config,
        'recipe': initial_recipe})

    processes = {'cellpack': cellpack}
    initial_state = {}

    engine = Engine(
        processes=processes,
        topology={
            'cellpack': {}
        },
        initial_state=initial_state)

    engine.update(10.0)
    engine.emitter.get_data()


if __name__ == '__main__':
    main()
