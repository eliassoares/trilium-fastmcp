from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from app.branch.schemas import Branch


class NoteOrderBy(Enum):
    title = "title"
    publication_date = "#publicationDate"
    is_protected = "isProtected"
    is_archived = "isArchived"
    date_created = "dateCreated"
    date_modified = "dateModified"
    utc_date_created = "utcDateCreated"
    utc_date_modified = "utcDateModified"
    parent_count = "parentCount"
    children_count = "childrenCount"
    attribute_count = "attributeCount"
    label_count = "labelCount"
    owned_label_count = "ownedLabelCount"
    relation_count = "relationCount"
    owned_relation_count = "ownedRelationCount"
    relation_count_including_links = "relationCountIncludingLinks"
    owned_relation_count_including_links = "ownedRelationCountIncludingLinks"
    target_relation_count = "targetRelationCount"
    target_relation_count_including_links = "targetRelationCountIncludingLinks"
    content_size = "contentSize"
    content_and_attachments_size = "contentAndAttachmentsSize"
    content_and_attachments_and_revisions_size = "contentAndAttachmentsAndRevisionsSize"
    revision_count = "revisionCount"


class NoteOrderDirection(Enum):
    asc = "asc"
    desc = "desc"


class NoteType(Enum):
    text = "text"
    code = "code"
    render = "render"
    file = "file"
    image = "image"
    search = "search"
    relation_map = "relationMap"
    book = "book"
    note_map = "noteMap"
    mermaid = "mermaid"
    web_view = "webView"
    shortcut = "shortcut"
    doc = "doc"
    content_widget = "contentWidget"
    launcher = "launcher"
    spreadsheet = "spreadsheet"
    canvas = "canvas"
    mind_map = "mindMap"
    geo_map = "geoMap"
    llm_chat = "llmChat"


class NoteExportType(Enum):
    html = "html"
    markdown = "markdown"
    share = "share"


class NoteRecentChange(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    note_id: str = Field(
        ...,
        description="Identifies the note this change belongs to",
        examples=["evnnmvHTCgIn"],
        pattern="[a-zA-Z0-9_]{4,32}",
    )
    title: str = Field(
        ...,
        description=(
            "Title at the time of the change (may be '[protected]' for protected notes)"
        ),
    )
    current_title: str = Field(
        ...,
        description=(
            "Current title of the note (may be '[protected]' for protected notes)"
        ),
    )
    current_is_deleted: bool | None = Field(
        default=None,
        description="Whether the note is currently deleted",
    )
    current_delete_id: str | None = Field(
        default=None,
        description="Delete ID if the note is deleted",
    )
    current_is_protected: bool | None = Field(
        default=None,
        description="Whether the note is protected",
    )
    utc_date: datetime = Field(
        ...,
        description="UTC timestamp of the change",
        examples=[datetime.fromisoformat("2022-03-07T21:54:25.277+00:00")],
    )
    date: datetime = Field(
        ...,
        description="Local timestamp of the change",
        examples=[datetime.fromisoformat("2022-03-07T21:54:25.277+00:00")],
    )
    can_be_undeleted: bool | None = Field(
        default=None,
        description=(
            "Whether the note can be undeleted (only present for deleted notes)"
        ),
    )


class AttributeType(Enum):
    label = "label"
    relation = "relation"


class Attribute(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    attribute_id: str = Field(
        ...,
        description="Unique identifier of the attribute",
        examples=["evnnmvHTCgIn"],
        pattern="[a-zA-Z0-9_]{4,32}",
    )
    note_id: str = Field(
        ...,
        description="Identifies the note this attribute belongs to",
        examples=["evnnmvHTCgIn"],
        pattern="[a-zA-Z0-9_]{4,32}",
    )
    type: AttributeType = Field(
        ...,
        description=(
            "Whether this attribute is a label (key-value) or a "
            "relation (link to another note)"
        ),
        examples=[AttributeType.label.value],
    )
    name: str = Field(..., description="Attribute name", examples=["shareCss"])
    value: str = Field(
        ...,
        description=(
            "Value of the label, or ID of the related note for relations. "
            "Can be empty for flag-like labels."
        ),
        examples=[""],
    )
    position: int = Field(
        ..., description="Order position of the attribute on the note", examples=[10]
    )
    is_inheritable: bool = Field(
        ...,
        description="Whether child notes inherit this attribute",
        examples=[False],
    )
    utc_date_modified: datetime = Field(
        ...,
        description="UTC timestamp of the last modification",
        examples=[datetime.fromisoformat("2022-03-07T21:54:25.277+00:00")],
    )


class Note(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    note_id: str = Field(
        ...,
        description="Unique identifier of the note",
        examples=["evnnmvHTCgIn"],
        pattern="[a-zA-Z0-9_]{4,32}",
    )
    title: str = Field(..., description="Note title", examples=["My Note"])
    type: NoteType = Field(..., description="Note type", examples=[NoteType.text.value])
    mime: str = Field(
        ...,
        description=(
            "MIME type that determines how the note content is processed and displayed"
            " (e.g. text/html, text/plain, application/json). "
            "Required for 'code', 'file' and 'image' note types."
        ),
        examples=["text/html"],
    )
    is_protected: bool = Field(
        ...,
        description="Whether the note is encrypted and requires credentials to access",
        examples=[False],
    )
    blob_id: str = Field(
        ...,
        description="ID of the blob object which effectively serves as a content hash",
        examples=["DecH36BK5cLX6dYDg5yx"],
    )
    attributes: list[Attribute] = Field(
        default_factory=list, description="Labels and relations attached to the note"
    )
    parent_note_ids: list[str] = Field(
        default_factory=list, description="IDs of parent notes in the tree"
    )
    child_note_ids: list[str] = Field(
        default_factory=list, description="IDs of child notes in the tree"
    )
    parent_branch_ids: list[str] = Field(
        default_factory=list,
        description="IDs of branches linking this note to its parents",
    )
    child_branch_ids: list[str] = Field(
        default_factory=list,
        description="IDs of branches linking this note to its children",
    )
    date_created: datetime = Field(
        ...,
        description="Local timestamp of note creation",
        examples=[datetime.fromisoformat("2022-02-09T22:52:36+01:00")],
    )
    date_modified: datetime = Field(
        ...,
        description="Local timestamp of the last modification",
        examples=[datetime.fromisoformat("2022-02-09T22:52:36+01:00")],
    )
    utc_date_created: datetime = Field(
        ...,
        description="UTC timestamp of note creation",
        examples=[datetime.fromisoformat("2022-03-07T21:54:25.277+00:00")],
    )
    utc_date_modified: datetime = Field(
        ...,
        description="UTC timestamp of the last modification",
        examples=[datetime.fromisoformat("2022-03-07T21:54:25.277+00:00")],
    )


class NoteWithBranch(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    note: Note = Field(..., description="The created note")
    branch: Branch = Field(..., description="The branch placing the note in the tree")


class SearchNotesParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    search: str = Field(
        ...,
        description="Search query string as described in https://triliumnext.github.io/Docs/Wiki/search.html",
        examples=["#book #published"],
    )
    fast_search: bool = Field(
        default=False,
        description=(
            "Enable fast search — fulltext search does not look into note content"
        ),
    )
    include_archived_notes: bool = Field(
        default=False,
        description=(
            "By default archived notes are excluded. "
            "Set to true to include them in results."
        ),
    )
    ancestor_note_id: str | None = Field(
        default=None,
        description=(
            "Restrict search to a subtree identified by this note ID. "
            "By default the whole tree is searched."
        ),
        examples=["evnnmvHTCgIn"],
        pattern="[a-zA-Z0-9_]{4,32}",
    )
    ancestor_depth: str | None = Field(
        default=None,
        description=(
            "Filter by depth in the tree relative to ancestor_note_id "
            "(e.g. 'eq1' for direct children, 'lt4' for depth less than 4)."
        ),
        examples=["eq1", "lt4", "gt2"],
    )
    order_by: NoteOrderBy | None = Field(
        default=None,
        description="Property or label name to order search results by",
    )
    order_direction: NoteOrderDirection = Field(
        default=NoteOrderDirection.asc,
        description="Sort direction for the results",
    )
    limit: int | None = Field(
        default=None,
        description="Maximum number of results to return",
        examples=[10],
        gt=0,
    )
    debug: bool = Field(
        default=False,
        description="Set to true to include query parsing debug info in the response",
    )


class CreateNoteParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    parent_note_id: str
    title: str
    type: NoteType
    content: str
    mime: str | None = None
    note_position: int | None = None
    prefix: str | None = None
    is_expanded: bool = False
    note_id: str | None = None
    branch_id: str | None = None
    date_created: datetime | None = None
    utc_date_created: datetime | None = None


class UpdateNoteParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    title: str | None = None
    type: NoteType | None = None
    mime: str | None = None
    date_created: datetime | None = None
    utc_date_created: datetime | None = None


class SearchNotesResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    results: list[Note]
    debug_info: dict[str, object] | None = Field(
        default=None,
        description=(
            "Debugging info on parsing the search query. "
            "Only present when &debug=true is passed."
        ),
    )
