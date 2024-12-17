#!/usr/bin/env python
#------------------------------------------
# Psyclone scripts to work on CASIM
#------------------------------------------
# Author: Wei Zhang, ORNL

from utils import (
    insert_explicit_loop_parallelism, normalise_loops, add_profiling,
    enhance_tree_information, NOT_PERFORMANT, inline_calls)
from psyclone.domain.common.transformations import KernelModuleInlineTrans
from psyclone.psyir.nodes import Routine, Loop, Directive, Call
from psyclone.transformations import (
    ACCParallelTrans, ACCLoopTrans, ACCRoutineTrans)

PROFILING_ENABLED = False

# Lists
list_of_subroutines_to_run_on_gpu = ["test_main_routine"]
list_of_subroutines_to_run_on_cpu = ["initial_test"]
list_of_subroutines_to_be_inlined = ["test_subroutine1", "test_subroutine2"]
list_of_subroutines_to_be_acc_routine_seq = ["test_subroutine1"]
list_of_subroutines_to_be_acc_routine_vector = ["test_subroutine2"]
list_of_loops_to_be_acc_parallel_loop = ["i"]
list_of_loops_to_be_acc_loop_vector = ["k"]

# Trans
def trans(psyir):
    ''' Walk over subroutine in list_of_subroutines_to_run_on_gpu, 
    find where it calls subroutine in list_of_subroutines_to_be_inlined,
    inline these called subrouitnes.

    Add 'acc parallel loop directives' to loops in list_of_loops_to_be_acc_parallel_loop,
    and add 'all loop vector' to loops in list_of_loops_to_be_acc_loop_vector.

    Add 'acc routine seq' to subroutines in list_of_subroutines_to_be_acc_routine_seq,
    and add 'acc routine vector' to subroutines in list_of_subrouitnes_to_be_acc_routine_vector.

    :param psyir: the PSyIR of the provided file
    :type psyir: :py:class`psyclone.psyir.nodes.FileContainer`
    '''

    acc_region_trans = ACCParallelTrans(default_present=False)
    acc_loop_trans = ACCLoopTrans()


    ## subroutines 
    for subroutine in psyir.walk(Routine):
        print(f"Transforming subroutine: {subroutine.name}")

        if subroutine.name in list_of_subroutines_to_run_on_cpu:
             print("Skipping", subroutine.name)
             continue

        if subroutine.name in list_of_subroutines_to_run_on_gpu:
             # Inline the calls in this subroutine
             inline_calls(subroutine)
             #continue

        if subroutine.name in list_of_subroutines_to_be_acc_routine_seq:
             # TODO: Now is "acc routine seq", how to make it "acc routine vector"?
             ACCRoutineTrans().apply(subroutine) 
             print(f"Marked {subroutine.name} as GPU-enabled")
             continue

        enhance_tree_information(subroutine)

        ## Loops
        normalise_loops(
                subroutine,
                hoist_local_arrays=True,
                convert_array_notation=True,
                convert_range_loops=True,
                hoist_expressions=True
        )

        # This gives loops "acc parallel loop"
        insert_explicit_loop_parallelism(
               subroutine,
               region_directive_trans=acc_region_trans,
               loop_directive_trans=acc_loop_trans,
               # Collapse is necessary to give GPUs enough parallel items
               collapse=True,
        )

        # This gives loops "acc loop vector"
        for loop in psyir.walk(Loop):
        
            if loop.ancestor(Directive) and loop.variable.name in list_of_loops_to_be_acc_loop_vector: 
               acc_loop_trans.apply(loop, options={"independent": False, "sequential":False,
               "gang": False, "vector": True})
