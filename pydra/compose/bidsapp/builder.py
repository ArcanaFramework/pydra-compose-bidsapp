import logging
import typing as ty
import inspect
from typing import dataclass_transform
from pydra.compose.base import (
    ensure_field_objects,
    build_task_class,
    check_explicit_fields_are_none,
    extract_fields_from_class,
)

from .fields import arg, out
from .task import BidsAppTask as Task
from .task import BidsAppOutputs as Outputs


logger = logging.getLogger("pydra.compose.bidsapp")


@dataclass_transform(
    kw_only_default=True,
    field_specifiers=(arg,),
)
def define(
    wrapped: type | str | None = None,
    /,
    inputs: list[str | arg] | dict[str, arg | type] | None = None,
    outputs: list[str | out] | dict[str, out | type] | type | None = None,
    executable: str | None = None,
    bases: ty.Sequence[type] = (),
    outputs_bases: ty.Sequence[type] = (),
    auto_attribs: bool = True,
    name: str | None = None,
    xor: ty.Sequence[str | None] | ty.Sequence[ty.Sequence[str | None]] = (),
) -> Task | ty.Callable[[str | type], Task[ty.Any]]:
    """
    Create an interface for a function or a class.

    Parameters
    ----------
    wrapped : type | callable | None
        The function or class to create an interface for.
    inputs : list[str | Arg] | dict[str, Arg | type] | None
        The inputs to the function or class.
    outputs : list[str | base.Out] | dict[str, base.Out | type] | type | None
        The outputs of the function or class.
    auto_attribs : bool
        Whether to use auto_attribs mode when creating the class.
    name: str | None
        The name of the returned class
    xor: Sequence[str | None] | Sequence[Sequence[str | None]], optional
        Names of args that are exclusive mutually exclusive, which must include
        the name of the current field. If this list includes None, then none of the
        fields need to be set.

    Returns
    -------
    Task
        The task class for the Python function
    """

    def make(wrapped: str | type) -> Task:
        if inspect.isclass(wrapped):
            if executable is not None:
                raise ValueError(
                    "`exectuable` should be set as a class attribute if using canonical "
                    "form of BidsAppTask definitions, not in define decorator "
                    f"({executable!r})"
                )
            klass = wrapped
            image_tag = klass.image_tag
            extracted_executable = klass.executable
            class_name = klass.__name__
            check_explicit_fields_are_none(klass, inputs, outputs)
            parsed_inputs, parsed_outputs = extract_fields_from_class(
                Task,
                Outputs,
                klass,
                arg,
                out,
                auto_attribs,
                skip_fields=["function"],
            )
        else:
            if not isinstance(wrapped, str):
                raise ValueError(
                    "wrapped must be a class or a str representing either the name of a "
                    "Docker image if executing the app as a Docker container, or the "
                    "name of the executable to run if extending the Docker image , not "
                    f"{wrapped!r}"
                )
            klass = None
            image_tag = wrapped
            extracted_executable = executable
            class_name = image_tag.split("/")[-1].split(":")[0]

            parsed_inputs, parsed_outputs = ensure_field_objects(
                arg_type=arg,
                out_type=out,
                inputs=inputs,
                outputs=outputs,
            )
        if clashing := set(parsed_inputs) & set(["exectuable", "image_tag"]):
            raise ValueError(f"{list(clashing)} are reserved input names")

        parsed_inputs["image_tag"] = arg(name="image_tag", type=str, default=image_tag)
        parsed_inputs["executable"] = arg(
            name="executable", type=str, default=extracted_executable
        )

        defn = build_task_class(
            Task,
            Outputs,
            parsed_inputs,
            parsed_outputs,
            name=class_name,
            klass=klass,
            bases=bases,
            outputs_bases=outputs_bases,
            xor=xor,
        )

        return defn

    if wrapped is not None:
        if not isinstance(wrapped, (ty.Callable, type)):
            raise ValueError(f"wrapped must be a class or a callable, not {wrapped!r}")
        return make(wrapped)
    return make
