import pytest
from typing import NamedTuple
import numpy as np

from pyvmcon import solve
from pyvmcon.exceptions import VMCONConvergenceException
from pyvmcon.problem import Problem


class VMCONTestAsset(NamedTuple):
    problem: Problem

    initial_x: np.ndarray
    max_iter: int
    epsilon: float

    expected_x: np.ndarray
    expected_lamda_equality: np.ndarray
    expected_lamda_inequality: np.ndarray


@pytest.mark.parametrize(
    "vmcon_example",
    [
        # Test 1 detailed in ANL-80-64 page 25
        VMCONTestAsset(
            Problem(
                lambda x: (x[0] - 2) ** 2 + (x[1] - 1) ** 2,
                lambda x: np.array([2 * (x[0] - 2), 2 * (x[1] - 1)]),
                [lambda x: x[0] - (2 * x[1]) + 1],
                [lambda x: -((x[0] ** 2) / 4) - (x[1] ** 2) + 1],
                [lambda _: np.array([1, -2])],
                [lambda x: np.array([-0.5 * x[0], -2 * x[1]])],
            ),
            initial_x=np.array([2.0, 2.0]),
            max_iter=10,
            epsilon=1e-8,
            expected_x=[8.228756e-1, 9.114378e-1],
            expected_lamda_equality=[-1.594491],
            expected_lamda_inequality=[1.846591],
        ),
        # Test 2 detailed in ANL-80-64 page 28
        VMCONTestAsset(
            Problem(
                lambda x: (x[0] - 2) ** 2 + (x[1] - 1) ** 2,
                lambda x: np.array([2 * (x[0] - 2), 2 * (x[1] - 1)]),
                [],
                [
                    lambda x: x[0] - (2 * x[1]) + 1,
                    lambda x: -((x[0] ** 2) / 4) - (x[1] ** 2) + 1,
                ],
                [],
                [
                    lambda _: np.array([1, -2]),
                    lambda x: np.array([-0.5 * x[0], -2 * x[1]]),
                ],
            ),
            initial_x=np.array([2.0, 2.0]),
            max_iter=10,
            epsilon=1e-8,
            expected_x=[1.6649685472365443, 0.55404867491788852],
            expected_lamda_equality=[],
            expected_lamda_inequality=[0, 0.80489557193146243],
        ),
        # Example 1a of https://en.wikipedia.org/wiki/Lagrange_multiplier
        VMCONTestAsset(
            Problem(
                lambda x: x[0] + x[1],
                lambda _: np.array([1, 1]),
                [lambda x: (x[0] ** 2) + (x[1] ** 2) - 1],
                [],
                [lambda x: np.array([2 * x[0], 2 * x[1]])],
                [],
            ),
            initial_x=np.array([1.0, 1.0]),
            max_iter=10,
            epsilon=2e-8,
            expected_x=[0.5 * 2**0.5, 0.5 * 2**0.5],  # Shouldn't these be negative?
            expected_lamda_equality=[2 ** (-0.5)],
            expected_lamda_inequality=[],
        ),
    ],
)
def test_vmcon_paper_feasible_examples(vmcon_example: VMCONTestAsset):
    x, lamda_equality, lamda_inequality, _ = solve(
        vmcon_example.problem,
        vmcon_example.initial_x,
        max_iter=vmcon_example.max_iter,
        epsilon=vmcon_example.epsilon,
    )

    assert x == pytest.approx(vmcon_example.expected_x)
    assert lamda_equality == pytest.approx(vmcon_example.expected_lamda_equality)
    assert lamda_inequality == pytest.approx(vmcon_example.expected_lamda_inequality)


@pytest.mark.parametrize(
    "vmcon_example",
    [
        VMCONTestAsset(
            Problem(
                lambda x: (x[0] - 2) ** 2 + (x[1] - 1) ** 2,
                lambda x: np.array([2 * (x[0] - 2), 2 * (x[1] - 1)]),
                [lambda x: x[0] + x[1] - 3],
                [lambda x: -((x[0] ** 2) / 4) - (x[1] ** 2) + 1],
                [lambda _: np.array([1.0, 1.0])],
                [lambda x: np.array([-0.5 * x[0], -2 * x[1]])],
            ),
            initial_x=np.array([2.0, 2.0]),
            max_iter=5,
            epsilon=1e-8,
            expected_x=[2.3999994310874733, 0.6],
            expected_lamda_equality=[0.0],
            expected_lamda_inequality=[0.0],
        ),
    ],
)
def test_vmcon_paper_infeasible_examples(vmcon_example: VMCONTestAsset):
    with pytest.raises(VMCONConvergenceException) as e:
        solve(
            vmcon_example.problem,
            vmcon_example.initial_x,
            max_iter=vmcon_example.max_iter,
            epsilon=vmcon_example.epsilon,
        )

    assert e.value.x == pytest.approx(vmcon_example.expected_x)
    # assert e.value.lamda_equality == pytest.approx(
    #     vmcon_example.expected_lamda_equality
    # )
    # assert e.value.lamda_inequality == pytest.approx(
    #     vmcon_example.expected_lamda_inequality
    # )
