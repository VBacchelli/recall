from dataclasses import dataclass
from typing import Protocol

import trafilatura


@dataclass
class ExtractedContent:
    title: str
    content: str
    source: str
    url: str


class ContentExtractor(Protocol):
    def extract(self, url: str) -> ExtractedContent:
        ...


class WebPageExtractor:
    def extract(self, url: str) -> ExtractedContent:
        downloaded = trafilatura.fetch_url(url)

        if downloaded is None:
            raise ValueError(f"Failed to download URL: {url}")

        document = trafilatura.bare_extraction(
    		downloaded,
		url=url,
    		include_comments=False,
    		include_tables=True,
    		with_metadata=True,
	)

        if document is None or not document.text:
            raise ValueError(f"Failed to extract meaningful content from URL: {url}")

        return ExtractedContent(
            title=document.title or url,
            content=document.text,
            source="web",
            url=url,
        )