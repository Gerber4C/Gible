from __future__ import annotations

import ast
import inspect
from pathlib import Path
from typing import Any, Callable

from .model import PolicyFunction, SourceInfo


class PolicyLoadError(ValueError):
    pass


SAFE_BUILTINS = {
    "abs": abs,
    "all": all,
    "any": any,
    "bool": bool,
    "dict": dict,
    "float": float,
    "int": int,
    "len": len,
    "list": list,
    "max": max,
    "min": min,
    "range": range,
    "round": round,
    "set": set,
    "sorted": sorted,
    "str": str,
    "sum": sum,
    "tuple": tuple,
}


def load_policy_functions(paths: list[Path] | tuple[Path, ...], source: SourceInfo) -> tuple[PolicyFunction, ...]:
    loaded: list[PolicyFunction] = []
    for path in paths:
        namespace = _execute_policy_module(path)
        procedures = _module_policy_procedures(namespace, path)
        for procedure in procedures:
            _validate_policy_signature(procedure, path)
            loaded.append(
                PolicyFunction(
                    id=procedure.__name__,
                    procedure=procedure,
                    source=source,
                    author=source.author,
                    source_path=str(path),
                )
            )
    return tuple(loaded)


def _execute_policy_module(path: Path) -> dict[str, Any]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    _validate_policy_ast(tree, path)
    namespace: dict[str, Any] = {"__builtins__": SAFE_BUILTINS}
    exec(compile(tree, str(path), "exec"), namespace)
    return namespace


def _validate_policy_ast(tree: ast.Module, path: Path) -> None:
    for statement in tree.body:
        if isinstance(statement, ast.Expr) and isinstance(statement.value, ast.Constant):
            continue
        if isinstance(statement, (ast.FunctionDef, ast.Assign, ast.AnnAssign)):
            continue
        raise PolicyLoadError(f"{path}: unsupported top-level policy syntax: {statement.__class__.__name__}")
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom, ast.Global, ast.Nonlocal)):
            raise PolicyLoadError(f"{path}: unsupported policy syntax: {node.__class__.__name__}")
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in {"eval", "exec", "open", "__import__"}:
            raise PolicyLoadError(f"{path}: unsupported policy helper call: {node.func.id}")


def _module_policy_procedures(namespace: dict[str, Any], path: Path) -> tuple[Callable[..., Any], ...]:
    declared = namespace.get("selection_policies")
    if declared is None:
        discovered = [
            value
            for name, value in namespace.items()
            if callable(value) and (name.startswith("policy_") or name.endswith("_policy"))
        ]
        return tuple(discovered)
    if not isinstance(declared, (list, tuple)):
        raise PolicyLoadError(f"{path}: selection_policies must be a list or tuple of functions")
    procedures = []
    for item in declared:
        if not callable(item):
            raise PolicyLoadError(f"{path}: selection_policies entries must be functions")
        procedures.append(item)
    return tuple(procedures)


def _validate_policy_signature(procedure: Callable[..., Any], path: Path) -> None:
    signature = inspect.signature(procedure)
    if len(signature.parameters) != 2:
        raise PolicyLoadError(f"{path}: policy function {procedure.__name__} must accept (ctx, candidates)")
