import os
import typing as t
from dataclasses import dataclass

from .blocks import *
from .exceptions import EditorJsParseError


@dataclass
class EditorJsParser:
    """
    An Editor.js parser.
    """

    content: dict
    """The JSON data of Editor.js content."""

    def __post_init__(self) -> None:
        if not isinstance(self.content, dict):
            raise EditorJsParseError(f"Content must be `dict`, not {type(self.content).__name__}")

    @staticmethod
    def _get_block(data: dict) -> type[EditorJsBlock] | None:
        """
        Obtains block instance from block data.
        """

        BLOCKS_MAP: dict[str, type[EditorJsBlock]] = {
            "header": HeaderBlock,
            "paragraph": ParagraphBlock,
            "list": ListBlock,
            "table": TableBlock,
            "delimiter": DelimiterBlock,
            "image": ImageBlock,
        }

        _type = data.get("type")

        try:
            return BLOCKS_MAP[_type](_data=data)

        except KeyError:
            return None

    def blocks(self) -> list[type[EditorJsBlock]]:
        """
        Obtains a list of all available blocks from the editor's JSON data.
        """

        all_blocks: list[type[EditorJsBlock]] = []
        blocks = self.content.get("blocks", [])

        if not isinstance(blocks, list):
            raise EditorJsParseError(f"Blocks is not `list`, but `{type(blocks).__name__}`")

        for block_data in blocks:
            block = self._get_block(data=block_data)
            if block is None:
                continue

            all_blocks.append(block)

        return all_blocks

    def __iter__(self) -> t.Iterator[type[EditorJsBlock]]:
        """Returns `iter(self.blocks())`"""

        return iter(self.blocks())

    def html(self, sanitize: bool = False) -> str:
        """
        Renders the editor's JSON content as HTML.

        ### Parameters:
        - `sanitize` - whether to also sanitize the blocks' texts/contents.
        """

        path = os.path.join(os.path.dirname(__file__), "editorjs.css")

        with open(path) as f:
            head = f'<head><style type="text/css">{f.read()}</style></head>'

        body = (
            f"<body>{'\n'.join([block.html(sanitize=sanitize) for block in self.blocks()])}</body>"
        )
        return head + body
