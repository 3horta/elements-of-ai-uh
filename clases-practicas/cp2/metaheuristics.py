import sys
import threading
import time
import types
from abc import ABC, abstractmethod
from typing import Any, Callable, List, Optional
import numpy as np

class Evaluation:

    def __init__(
        self,
        mh_name: str,
        solutions: List[Any],
        values: List[float],
        total_evals: int,
        total_time: float,
        fail_msg: Optional[str] = None
    ):
        self.mh_name = mh_name
        self.solutions = solutions
        self.values = values
        self.iters = len(solutions)
        self.total_evals = total_evals
        self.total_time = total_time
        self.fail_msg = fail_msg
        self.success = fail_msg is None

        if len(values) > 0:
            indice = int(np.argmin(values))
            self.best_result = solutions[indice]
            self.best_value = values[indice]
        else:
            self.best_result = None
            self.best_value = None

    def __repr__(self):

        return (
            f"Evaluación: {self.mh_name}\n"
            f"Mejor solución: {self.best_result}\n"
            f"Mejor valor: {self.best_value}\n"
            f"Evaluaciones: {self.total_evals}\n"
            f"Soluciones registradas: {self.iters}\n"
            f"Tiempo total: {self.total_time:.4f} segundos\n"
            f"Ejecución completada: {self.success}"
        )

    def __str__(self):
        return repr(self)


class MetaHeuristic(ABC):

    @abstractmethod
    def solve(
        self,
        obj_func: Callable,
        *args,
        **kwargs
    ):
        """
        Ejecuta la metaheurística.

        Debe producir pares:
            (solución, valor_objetivo)
        """
        raise NotImplementedError

    def on_new_solution(self, sol, val):
        """
        Permite añadir acciones cuando se registra
        una nueva solución.
        """
        pass

    def evaluate(
        self,
        obj_func: Callable,
        max_evals: Optional[int] = None,
        verbose: bool = True,
        *args,
        **kwargs
    ) -> Evaluation:

        if verbose:
            print(
                f"Evaluando {self.__class__.__name__}"
            )

        evals = 0
        solutions = []
        values = []
        fail_msg = None
        t0 = time.perf_counter()

        class BudgetExceeded(Exception):
            pass

        def obj_func_controlada(*f_args, **f_kwargs):
            nonlocal evals

            if (
                max_evals is not None
                and evals >= max_evals
            ):
                raise BudgetExceeded

            evals += 1

            return obj_func(*f_args, **f_kwargs)

        try:
            resultado = self.solve(
                obj_func_controlada,
                *args,
                **kwargs
            )

            if isinstance(resultado, tuple):
                if len(resultado) != 2:
                    raise ValueError(
                        "La solución debe ser un par "
                        "(solución, valor)."
                    )

                sol, val = resultado

                solutions.append(sol)
                values.append(val)

                self.on_new_solution(sol, val)

            else:
                for sol, val in resultado:
                    solutions.append(sol)
                    values.append(val)

                    self.on_new_solution(sol, val)

        except BudgetExceeded:
            fail_msg = (
                "Se alcanzó el presupuesto máximo "
                "de evaluaciones."
            )

        total_time = time.perf_counter() - t0

        return Evaluation(
            mh_name=self.__class__.__name__,
            solutions=solutions,
            values=values,
            total_evals=evals,
            total_time=total_time,
            fail_msg=fail_msg
        )