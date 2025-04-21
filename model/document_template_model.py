from typing import List, Optional
from dataclasses import dataclass

@dataclass
class Section:
    title: str
    content: str = ""
    subsections: List['Section'] = None

    def __post_init__(self):
        if self.subsections is None:
            self.subsections = []

@dataclass
class Chapter:
    title: str
    content: str = ""
    sections: List[Section] = None

    def __post_init__(self):
        if self.sections is None:
            self.sections = []

@dataclass
class DocumentTemplate:
    title: str = "Project Documentation"
    chapters: List[Chapter] = None

    def __post_init__(self):
        if self.chapters is None:
            self.chapters = []

    @classmethod
    def get_default_template(cls) -> 'DocumentTemplate':
        """Returns the default document template structure"""
        return cls(
            title="Project Documentation",
            chapters=[
                Chapter(
                    title="Chapter 1: Overview and Project Scope",
                    sections=[
                        Section(title="1.1 Project Overview"),
                        Section(title="1.2 Scope Definition"),
                        Section(title="1.3 Objectives")
                    ]
                ),
                Chapter(
                    title="Chapter 2: Key Highlights and Assumptions",
                    sections=[
                        Section(
                            title="2.1 Sizing",
                            subsections=[
                                Section(title="2.1.1 System Requirements"),
                                Section(title="2.1.2 Resource Allocation")
                            ]
                        ),
                        Section(
                            title="2.2 Architecture",
                            subsections=[
                                Section(title="2.2.1 System Architecture"),
                                Section(title="2.2.2 Component Overview")
                            ]
                        )
                    ]
                ),
                Chapter(
                    title="Chapter 3: Project Activities",
                    sections=[
                        Section(
                            title="3.1 Software Installation",
                            subsections=[
                                Section(title="3.1.1 Prerequisites"),
                                Section(title="3.1.2 Installation Steps"),
                                Section(title="3.1.3 Configuration")
                            ]
                        ),
                        Section(title="3.2 Testing"),
                        Section(title="3.3 Deployment")
                    ]
                )
            ]
        )

    def to_dict(self) -> dict:
        """Converts the template to a dictionary for JSON serialization"""
        return {
            "title": self.title,
            "chapters": [
                {
                    "title": chapter.title,
                    "content": chapter.content,
                    "sections": [
                        {
                            "title": section.title,
                            "content": section.content,
                            "subsections": [
                                {
                                    "title": subsection.title,
                                    "content": subsection.content
                                }
                                for subsection in section.subsections
                            ]
                        }
                        for section in chapter.sections
                    ]
                }
                for chapter in self.chapters
            ]
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'DocumentTemplate':
        """Creates a template from a dictionary"""
        template = cls(title=data.get("title", ""))
        for chapter_data in data.get("chapters", []):
            chapter = Chapter(
                title=chapter_data["title"],
                content=chapter_data.get("content", "")
            )
            for section_data in chapter_data.get("sections", []):
                section = Section(
                    title=section_data["title"],
                    content=section_data.get("content", "")
                )
                for subsection_data in section_data.get("subsections", []):
                    subsection = Section(
                        title=subsection_data["title"],
                        content=subsection_data.get("content", "")
                    )
                    section.subsections.append(subsection)
                chapter.sections.append(section)
            template.chapters.append(chapter)
        return template 