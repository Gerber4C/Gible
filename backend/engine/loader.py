from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from .bsl import load_bsl_files
from .model import Author, EvaluatorSpec, Gadget, PartnershipProfile
from .policy_runtime import load_policy_functions


def load_profile(profile_id: str, base_dir: Path | None = None) -> PartnershipProfile:
    base_dir = base_dir or Path(__file__).resolve().parents[1]
    profile_dir, profile_bsl_path = _profile_paths(base_dir, profile_id)
    data = _read_profile_data(profile_bsl_path)
    gadgets = tuple(_load_gadget(base_dir / "gadgets" / Path(*gadget_id.split("."))) for gadget_id in data.get("gadgets", []))

    profile_source = PartnershipProfile(
        id=data["id"],
        name=data.get("name", data["id"]),
        version=data.get("version", "0.1.0"),
        author=Author.from_dict(data.get("author")),
        gadgets=gadgets,
        description=data.get("description"),
        system_notes=data.get("system_notes"),
    ).source_info

    profile_bsl_files = [
        path
        for path in sorted(profile_dir.rglob("*.bsl.py"))
        if path.resolve() != profile_bsl_path.resolve()
    ]
    profile_bsl_data = load_bsl_files(profile_bsl_files) if profile_bsl_files else None
    profile_evaluators = (
        tuple(EvaluatorSpec.from_dict(item, profile_source, profile_source.author) for item in profile_bsl_data.evaluator_specs)
        if profile_bsl_data
        else ()
    )
    policy_functions = load_policy_functions(sorted(profile_dir.rglob("*.policy.py")), profile_source)

    return PartnershipProfile(
        id=data["id"],
        name=data.get("name", data["id"]),
        version=data.get("version", "0.1.0"),
        author=Author.from_dict(data.get("author")),
        gadgets=gadgets,
        policy_functions=policy_functions,
        evaluator_specs=profile_evaluators,
        description=data.get("description"),
        system_notes=data.get("system_notes"),
    )


def _profile_paths(base_dir: Path, profile_id: str) -> tuple[Path, Path]:
    profile_dir = base_dir / "profiles" / profile_id
    profile_bsl_path = profile_dir / "profile.bsl.py"
    if profile_bsl_path.exists():
        return profile_dir, profile_bsl_path
    flat_path = base_dir / "profiles" / f"{profile_id}.bsl.py"
    if flat_path.exists():
        return flat_path.parent, flat_path
    raise FileNotFoundError(f"Profile has no BSL source file: {profile_bsl_path}")


def _load_gadget(gadget_path: Path) -> Gadget:
    bsl_paths = sorted(gadget_path.glob("*.bsl.py"))
    if not bsl_paths:
        raise FileNotFoundError(f"Gadget directory has no BSL source files: {gadget_path}")
    gadget = _load_bsl_gadget(bsl_paths)
    policy_paths = sorted(gadget_path.glob("*.policy.py"))
    if not policy_paths:
        return gadget
    return replace(gadget, policy_functions=load_policy_functions(policy_paths, gadget.source_info))


def _read_profile_data(bsl_path: Path) -> dict:
    if not bsl_path.exists():
        raise FileNotFoundError(f"Profile has no BSL source file: {bsl_path}")
    module_data = load_bsl_files([bsl_path])
    if module_data.profile is None:
        raise ValueError(f"BSL profile file must contain Profile(...): {bsl_path}")
    return module_data.profile


def _load_bsl_gadget(paths: list[Path]) -> Gadget:
    module_data = load_bsl_files(paths)
    if module_data.gadget_metadata is None:
        raise ValueError(f"BSL gadget directory must contain Gadget(...): {paths[0].parent}")
    return Gadget.from_parts(
        module_data.gadget_metadata,
        module_data.call_specs,
        frame_data=module_data.frame_specs,
        private_route_data=module_data.private_route_specs,
        evaluator_data=module_data.evaluator_specs,
        relay_data=module_data.relay_specs,
    )
