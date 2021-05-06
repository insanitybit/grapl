from __future__ import annotations
from typing import *
import grapl_analyzerlib
import grapl_analyzerlib.node_types
import grapl_analyzerlib.nodes.entity
import grapl_analyzerlib.queryable
def default_file_properties() -> Dict[str, grapl_analyzerlib.node_types.PropType]:
    return {
        "file_path": grapl_analyzerlib.node_types.PropType(grapl_analyzerlib.node_types.PropPrimitive.Str, False),
        "created_at": grapl_analyzerlib.node_types.PropType(grapl_analyzerlib.node_types.PropPrimitive.Int, False),
        "last_seen_at": grapl_analyzerlib.node_types.PropType(grapl_analyzerlib.node_types.PropPrimitive.Int, False),
        "terminated_at": grapl_analyzerlib.node_types.PropType(grapl_analyzerlib.node_types.PropPrimitive.Int, False),
    }
def default_file_edges() -> Dict[str, Tuple[grapl_analyzerlib.node_types.EdgeT, str]]:
    return {
    }

class FileSchema(grapl_analyzerlib.nodes.entity.EntitySchema):
    def __init__(self):
        super(FileSchema, self).__init__(
            default_file_properties(), default_file_edges(), lambda: FileView
        );

    @staticmethod
    def self_type() -> str:
        return "File"



class FileQuery(grapl_analyzerlib.nodes.entity.EntityQuery['FileView', 'FileQuery']):
    def with_file_path(
        self,
        *,
        eq: Optional[grapl_analyzerlib.comparators.StrOrNot] = None,
        contains: Optional["grapl_analyzerlib.comparators.OneOrMany[grapl_analyzerlib.comparators.StrOrNot]"] = None,
        starts_with: Optional["grapl_analyzerlib.comparators.StrOrNot"] = None,
        ends_with: Optional["grapl_analyzerlib.comparators.StrOrNot"] = None,
        regexp: Optional["grapl_analyzerlib.comparators.OneOrMany[grapl_analyzerlib.comparators.StrOrNot]"] = None,
        distance_lt: Optional[Tuple[str, int]] = None,
    ):
        (
            self.with_str_property(
                "file_path",
                eq=eq,
                contains=contains,
                starts_with=starts_with,
                ends_with=ends_with,
                regexp=regexp,
                distance_lt=distance_lt
            )
        )
        return self

    def with_created_at(
        self,
        *,
        eq: Optional["grapl_analyzerlib.comparators.IntOrNot"] = None,
        gt: Optional["grapl_analyzerlib.comparators.IntOrNot"] = None,
        ge: Optional["grapl_analyzerlib.comparators.IntOrNot"] = None,
        lt: Optional["grapl_analyzerlib.comparators.IntOrNot"] = None,
        le: Optional["grapl_analyzerlib.comparators.IntOrNot"] = None,

    ):
        (
            self.with_int_property(
                "created_at",
                eq=eq,
                gt=gt,
                ge=ge,
                lt=lt,
                le=le,
            )
        )
        return self

    def with_last_seen_at(
        self,
        *,
        eq: Optional["grapl_analyzerlib.comparators.IntOrNot"] = None,
        gt: Optional["grapl_analyzerlib.comparators.IntOrNot"] = None,
        ge: Optional["grapl_analyzerlib.comparators.IntOrNot"] = None,
        lt: Optional["grapl_analyzerlib.comparators.IntOrNot"] = None,
        le: Optional["grapl_analyzerlib.comparators.IntOrNot"] = None,

    ):
        (
            self.with_int_property(
                "last_seen_at",
                eq=eq,
                gt=gt,
                ge=ge,
                lt=lt,
                le=le,
            )
        )
        return self

    def with_terminated_at(
        self,
        *,
        eq: Optional["grapl_analyzerlib.comparators.IntOrNot"] = None,
        gt: Optional["grapl_analyzerlib.comparators.IntOrNot"] = None,
        ge: Optional["grapl_analyzerlib.comparators.IntOrNot"] = None,
        lt: Optional["grapl_analyzerlib.comparators.IntOrNot"] = None,
        le: Optional["grapl_analyzerlib.comparators.IntOrNot"] = None,

    ):
        (
            self.with_int_property(
                "terminated_at",
                eq=eq,
                gt=gt,
                ge=ge,
                lt=lt,
                le=le,
            )
        )
        return self

    @classmethod
    def node_schema(cls) -> "grapl_analyzerlib.schema.Schema":
        return FileSchema()


class FileView(grapl_analyzerlib.nodes.entity.EntityView['FileView', 'FileQuery']):
    queryable = FileQuery

    def __init__(
        self,
        uid: int,
        node_key: str,
        graph_client: Any,
        node_types: Set[str],
        file_path: Optional["str"] = None,
        created_at: Optional["int"] = None,
        last_seen_at: Optional["int"] = None,
        terminated_at: Optional["int"] = None,
        **kwargs,
    ) -> None:
        super().__init__(uid, node_key, graph_client, node_types, **kwargs)
        if file_path: self.set_predicate("file_path", file_path)
        if created_at: self.set_predicate("created_at", created_at)
        if last_seen_at: self.set_predicate("last_seen_at", last_seen_at)
        if terminated_at: self.set_predicate("terminated_at", terminated_at)

    def get_file_path(self, cached: bool = True) -> Optional[str]:
        return self.get_str("file_path", cached=cached)

    def get_created_at(self, cached: bool = True) -> Optional[int]:
        return self.get_int("created_at", cached=cached)

    def get_last_seen_at(self, cached: bool = False) -> Optional[int]:
        return self.get_int("last_seen_at", cached=cached)

    def get_terminated_at(self, cached: bool = True) -> Optional[int]:
        return self.get_int("terminated_at", cached=cached)


def default_process_properties() -> Dict[str, grapl_analyzerlib.node_types.PropType]:
    return {
        "process_name": grapl_analyzerlib.node_types.PropType(grapl_analyzerlib.node_types.PropPrimitive.Str, False),
        "process_id": grapl_analyzerlib.node_types.PropType(grapl_analyzerlib.node_types.PropPrimitive.Int, False),
        "created_at": grapl_analyzerlib.node_types.PropType(grapl_analyzerlib.node_types.PropPrimitive.Int, False),
        "last_seen_at": grapl_analyzerlib.node_types.PropType(grapl_analyzerlib.node_types.PropPrimitive.Int, False),
        "terminated_at": grapl_analyzerlib.node_types.PropType(grapl_analyzerlib.node_types.PropPrimitive.Int, False),
    }
def default_process_edges() -> Dict[str, Tuple[grapl_analyzerlib.node_types.EdgeT, str]]:
    return {
        "binary_file": (
            grapl_analyzerlib.node_types.EdgeT(ProcessSchema, FileSchema, grapl_analyzerlib.node_types.EdgeRelationship.OneToOne),
            "executed_as_processes"
        ),
        "created_file": (
            grapl_analyzerlib.node_types.EdgeT(ProcessSchema, FileSchema, grapl_analyzerlib.node_types.EdgeRelationship.OneToMany),
            "created_by_process"
        ),
    }

class ProcessSchema(grapl_analyzerlib.nodes.entity.EntitySchema):
    def __init__(self):
        super(ProcessSchema, self).__init__(
            default_process_properties(), default_process_edges(), lambda: ProcessView
        );

    @staticmethod
    def self_type() -> str:
        return "Process"



class ProcessQuery(grapl_analyzerlib.nodes.entity.EntityQuery['ProcessView', 'ProcessQuery']):
    def with_process_name(
        self,
        *,
        eq: Optional[grapl_analyzerlib.comparators.StrOrNot] = None,
        contains: Optional["grapl_analyzerlib.comparators.OneOrMany[grapl_analyzerlib.comparators.StrOrNot]"] = None,
        starts_with: Optional["grapl_analyzerlib.comparators.StrOrNot"] = None,
        ends_with: Optional["grapl_analyzerlib.comparators.StrOrNot"] = None,
        regexp: Optional["grapl_analyzerlib.comparators.OneOrMany[grapl_analyzerlib.comparators.StrOrNot]"] = None,
        distance_lt: Optional[Tuple[str, int]] = None,
    ):
        (
            self.with_str_property(
                "process_name",
                eq=eq,
                contains=contains,
                starts_with=starts_with,
                ends_with=ends_with,
                regexp=regexp,
                distance_lt=distance_lt
            )
        )
        return self

    def with_process_id(
        self,
        *,
        eq: Optional["grapl_analyzerlib.comparators.IntOrNot"] = None,
        gt: Optional["grapl_analyzerlib.comparators.IntOrNot"] = None,
        ge: Optional["grapl_analyzerlib.comparators.IntOrNot"] = None,
        lt: Optional["grapl_analyzerlib.comparators.IntOrNot"] = None,
        le: Optional["grapl_analyzerlib.comparators.IntOrNot"] = None,

    ):
        (
            self.with_int_property(
                "process_id",
                eq=eq,
                gt=gt,
                ge=ge,
                lt=lt,
                le=le,
            )
        )
        return self

    def with_created_at(
        self,
        *,
        eq: Optional["grapl_analyzerlib.comparators.IntOrNot"] = None,
        gt: Optional["grapl_analyzerlib.comparators.IntOrNot"] = None,
        ge: Optional["grapl_analyzerlib.comparators.IntOrNot"] = None,
        lt: Optional["grapl_analyzerlib.comparators.IntOrNot"] = None,
        le: Optional["grapl_analyzerlib.comparators.IntOrNot"] = None,

    ):
        (
            self.with_int_property(
                "created_at",
                eq=eq,
                gt=gt,
                ge=ge,
                lt=lt,
                le=le,
            )
        )
        return self

    def with_last_seen_at(
        self,
        *,
        eq: Optional["grapl_analyzerlib.comparators.IntOrNot"] = None,
        gt: Optional["grapl_analyzerlib.comparators.IntOrNot"] = None,
        ge: Optional["grapl_analyzerlib.comparators.IntOrNot"] = None,
        lt: Optional["grapl_analyzerlib.comparators.IntOrNot"] = None,
        le: Optional["grapl_analyzerlib.comparators.IntOrNot"] = None,

    ):
        (
            self.with_int_property(
                "last_seen_at",
                eq=eq,
                gt=gt,
                ge=ge,
                lt=lt,
                le=le,
            )
        )
        return self

    def with_terminated_at(
        self,
        *,
        eq: Optional["grapl_analyzerlib.comparators.IntOrNot"] = None,
        gt: Optional["grapl_analyzerlib.comparators.IntOrNot"] = None,
        ge: Optional["grapl_analyzerlib.comparators.IntOrNot"] = None,
        lt: Optional["grapl_analyzerlib.comparators.IntOrNot"] = None,
        le: Optional["grapl_analyzerlib.comparators.IntOrNot"] = None,

    ):
        (
            self.with_int_property(
                "terminated_at",
                eq=eq,
                gt=gt,
                ge=ge,
                lt=lt,
                le=le,
            )
        )
        return self

    def with_binary_file(self: ProcessQuery, *binary_file: FileQuery) -> ProcessQuery:
        return self.with_to_neighbor(ProcessQuery, "binary_file", "executed_as_processes", binary_file)

    def with_created_file(self: ProcessQuery, *created_file: FileQuery) -> ProcessQuery:
        return self.with_to_neighbor(ProcessQuery, "created_file", "created_by_process", created_file)

    @classmethod
    def node_schema(cls) -> "grapl_analyzerlib.schema.Schema":
        return ProcessSchema()


class ProcessView(grapl_analyzerlib.nodes.entity.EntityView['ProcessView', 'ProcessQuery']):
    queryable = ProcessQuery

    def __init__(
        self,
        uid: int,
        node_key: str,
        graph_client: Any,
        node_types: Set[str],
        process_name: Optional["str"] = None,
        process_id: Optional["int"] = None,
        created_at: Optional["int"] = None,
        last_seen_at: Optional["int"] = None,
        terminated_at: Optional["int"] = None,
        binary_file: Optional["FileView"] = None,
        created_file: Optional[List["FileView"]] = None,
        **kwargs,
    ) -> None:
        super().__init__(uid, node_key, graph_client, node_types, **kwargs)
        if process_name: self.set_predicate("process_name", process_name)
        if process_id: self.set_predicate("process_id", process_id)
        if created_at: self.set_predicate("created_at", created_at)
        if last_seen_at: self.set_predicate("last_seen_at", last_seen_at)
        if terminated_at: self.set_predicate("terminated_at", terminated_at)
        if binary_file: self.set_predicate("binary_file", binary_file)
        if created_file: self.set_predicate("created_file", created_file or [])

    def get_process_name(self, cached: bool = True) -> Optional[str]:
        return self.get_str("process_name", cached=cached)

    def get_process_id(self, cached: bool = True) -> Optional[int]:
        return self.get_int("process_id", cached=cached)

    def get_created_at(self, cached: bool = True) -> Optional[int]:
        return self.get_int("created_at", cached=cached)

    def get_last_seen_at(self, cached: bool = False) -> Optional[int]:
        return self.get_int("last_seen_at", cached=cached)

    def get_terminated_at(self, cached: bool = True) -> Optional[int]:
        return self.get_int("terminated_at", cached=cached)

    def get_binary_file(self, binary_file: Optional[FileQuery] = None, cached=True) -> 'Optional[FileView]':
          return self.get_neighbor(FileQuery, "binary_file", "executed_as_processes", binary_file, cached)
    def get_created_file(self, *created_file: FileQuery, cached=False) -> 'List[FileView]':
          return self.get_neighbor(FileQuery, "created_file", "created_by_process", created_file, cached)

def default_someplugin_properties() -> Dict[str, grapl_analyzerlib.node_types.PropType]:
    return {
        "plugin_prop": grapl_analyzerlib.node_types.PropType(grapl_analyzerlib.node_types.PropPrimitive.Str, False),
    }
def default_someplugin_edges() -> Dict[str, Tuple[grapl_analyzerlib.node_types.EdgeT, str]]:
    return {
    }

class SomePluginSchema(grapl_analyzerlib.nodes.entity.EntitySchema):
    def __init__(self):
        super(SomePluginSchema, self).__init__(
            default_someplugin_properties(), default_someplugin_edges(), lambda: SomePluginView
        );

    @staticmethod
    def self_type() -> str:
        return "SomePlugin"



class SomePluginQuery(grapl_analyzerlib.nodes.entity.EntityQuery['SomePluginView', 'SomePluginQuery']):
    def with_plugin_prop(
        self,
        *,
        eq: Optional[grapl_analyzerlib.comparators.StrOrNot] = None,
        contains: Optional["grapl_analyzerlib.comparators.OneOrMany[grapl_analyzerlib.comparators.StrOrNot]"] = None,
        starts_with: Optional["grapl_analyzerlib.comparators.StrOrNot"] = None,
        ends_with: Optional["grapl_analyzerlib.comparators.StrOrNot"] = None,
        regexp: Optional["grapl_analyzerlib.comparators.OneOrMany[grapl_analyzerlib.comparators.StrOrNot]"] = None,
        distance_lt: Optional[Tuple[str, int]] = None,
    ):
        (
            self.with_str_property(
                "plugin_prop",
                eq=eq,
                contains=contains,
                starts_with=starts_with,
                ends_with=ends_with,
                regexp=regexp,
                distance_lt=distance_lt
            )
        )
        return self

    @classmethod
    def node_schema(cls) -> "grapl_analyzerlib.schema.Schema":
        return SomePluginSchema()


class SomePluginView(grapl_analyzerlib.nodes.entity.EntityView['SomePluginView', 'SomePluginQuery']):
    queryable = SomePluginQuery

    def __init__(
        self,
        uid: int,
        node_key: str,
        graph_client: Any,
        node_types: Set[str],
        plugin_prop: Optional["str"] = None,
        **kwargs,
    ) -> None:
        super().__init__(uid, node_key, graph_client, node_types, **kwargs)
        if plugin_prop: self.set_predicate("plugin_prop", plugin_prop)

    def get_plugin_prop(self, cached: bool = True) -> Optional[str]:
        return self.get_str("plugin_prop", cached=cached)


