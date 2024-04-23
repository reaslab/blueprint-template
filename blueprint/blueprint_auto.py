import argparse
import re
import os
import jinja2
import json
from typing import List, Tuple
from pprint import pprint

keywords_list = [
    "theorem",
    "def",
    "lemma",
    "example",
    "open",
    "section",
    "variable",
    "/",
    "notation",
    "local notation",
    "noncomputable section",
    "nonrec theorem",
    "end",
    "section",
    "private lemma",
    "@",
    "notation",
    "scoped notation",
    "#",
    "class",
    "structure",
]
keywords = ["\n" + s for s in keywords_list]

type_tex_dict = {
    "\ntheorem": "theorem",
    "\ndef": "definition",
    "\nlemma": "lemma",
    "\nexample": "example",
    "\nclass": "definition",
    "\nsturcture": "definition",
}


def find(s, keywords_list=keywords_list):
    split_index = s.find(":=")
    if split_index == -1:
        return None, None, None, None
    before_string = s[:split_index].strip()
    regex_pattern = (
        r"\b("
        + "|".join(re.escape(keyword) for keyword in keywords_list)
        + r")\b\s*([^ ]*)"
    )
    match = re.search(regex_pattern, before_string)
    if match:
        return (
            s[:split_index],
            s[split_index + 2 :].strip(),
            match.group(2),
            re.search(r"\bsorry\b", s[split_index + 2 :].strip()),
        )
    else:
        return s, None, None, None


def find_dependency(s: str, lemma_list: List[str]) -> List[str]:
    dependent_lemmas = []
    try:
        for lemma in lemma_list:
            if lemma in s:
                dependent_lemmas.append(lemma)
    except:
        pass
    return dependent_lemmas


class leanstr:
    def __init__(self, formal, section=None, file=None, type="theorem"):
        self.type = type
        self.formal = formal
        self.section = section
        self.file = file

    def __str__(self):
        return self.formal


class Statement:
    def __init__(self, type="theorem"):
        self.type: str = type
        self.otherinformation: str = None
        self.informal: str = None
        self.formal: str = None
        self.formal_statement: str = None
        self.informal_statement: str = None
        self.name: str = None
        self.head = None
        self.definitions = []
        self.formal_proof = None
        self.informal_proof = None
        self.sorry: bool = False
        self.wikilink = None
        self.section = None

        # members for TeX generation
        # Automatically find lemmas that this statement depends on
        self.dependent_lemmas: List[str] = []

    def Formalize(self, formal):
        self.formal = formal.strip()
        self.formal_statement, self.formal_proof, self.name, self.sorry = find(
            self.formal
        )

    def Add_Definition(self, definition):
        self.definitions.append(definition)

    def toinput(self, mode=["informal", "formal"]):
        input = ""
        if "informal" in mode:
            input += f"Informal statement: {self.informal}\n"
        if "head" in mode:
            input += f"Head: {self.head}\n"
        if "formal" in mode:
            input += f"Formal: {self.formal}\n"
        elif "name" in mode:
            input += f"Name: {self.name}\n"
        elif "formal_statement" in mode:
            input += f"Formal statement: {self.formal_statement}\n"
        elif "formal_proof" in mode:
            input += f"Formal proof: {self.formal_proof}\n"
        return input

    def wiki(self, wikilink):
        self.wikilink = wikilink

    def __str__(self):
        return self.toinput("formal")


class LeanFile:
    def __init__(self, path):
        self.path = path
        self.statements: List[Statement] = []
        self.sections: List[Tuple[str, str]] = []
        self.sentences: List[leanstr] = []
        with open(self.path, "r", encoding="utf8") as file:
            self.file_content = file.read()

    def __str__(self):
        return self.file_content

    def prepare(self, section_mode=False):
        import_start = self.file_content.find("import")
        import_end = self.file_content.find("\n", import_start)
        while import_end != -1 and self.file_content[
            import_end + 1 :
        ].strip().startswith("import"):
            import_end = self.file_content.find("\n", import_end + 1)
        import_end = import_end if import_end != -1 else len(self.file_content)
        self.headinformation = self.file_content[:import_start].strip()
        self.headimport = self.file_content[import_start:import_end].strip()
        content = self.file_content[import_end:].strip()

        # sections
        if section_mode == False:
            # If there is no section format, add a main section to mark content
            content = "section main\n" + content + "\nend main\n"
        pattern_sections = r"section\s+([^\n]+)\n(.*?)\nend\s+\1"
        self.sections = re.findall(pattern_sections, content, re.DOTALL)
        if len(self.sections) == 0:
            self.sections = [(None, content)]

        # sentences
        pattern_sentences = "|".join(keywords)
        self.sentences = []
        for section in self.sections:
            last_part = ""
            section_text = "\n" + section[1]
            sentences = re.split(f"({pattern_sentences})", section_text)
            current_sentence = ""
            for part in sentences:
                if part in keywords:
                    if current_sentence:
                        if current_sentence.strip():
                            self.sentences.append(
                                leanstr(
                                    current_sentence.strip(),
                                    section=section[0],
                                    file=self.path,
                                    type=last_part,
                                )
                            )
                            last_part = part
                    current_sentence = part
                else:
                    current_sentence += part
            if current_sentence:
                if current_sentence.strip():
                    self.sentences.append(
                        leanstr(
                            current_sentence.strip(),
                            section=section[0],
                            file=self.path,
                            type=last_part,
                        )
                    )

        # statements
        self.statements = []
        notation = None
        info = None
        past_section = ""
        section_head = ""
        past_path = ""
        for sentence in self.sentences:
            if sentence.file != past_path:
                past_path = sentence.file
                section_head = ""
            if sentence.section != past_section:
                past_section = sentence.section
                section_head = ""
            if sentence.type in [
                "\ntheorem",
                "\ndef",
                "\nlemma",
                "\nexample",
                "\nnonrec theorem",
                "\nprivate lemma",
            ]:
                statement = Statement(sentence.type)
                statement.section = sentence.section
                statement.Formalize(sentence.formal)
                # statement.GetNameFromFormal()
                self.statements.append(statement)
                self.statements[-1].head = self.headimport + "\n" + section_head
                if info:
                    self.statements[-1].wiki(info)
                    info = None

            elif sentence.type == "\n/":
                notation = sentence.formal
            elif sentence.type == "\n@":
                info = sentence.formal
            elif sentence.type == "\nopen":
                section_head += sentence.formal
                section_head += "\n"
            elif sentence.type == "\nvariable":
                section_head += sentence.formal
                section_head += "\n"
            elif sentence.type == "\nnotation":
                section_head += sentence.formal
                section_head += "\n"
            elif sentence.type == "\nlocal notation":
                section_head += sentence.formal
                section_head += "\n"
            elif sentence.type == "\nnoncomputable section":
                section_head += sentence.formal
                section_head += "\n"
            elif sentence.type == "\nnotation" or "\nscoped notation":
                section_head += sentence.formal
                section_head += "\n"

    # Find lemmas after all statements are prepared
    def find_dependency(self):
        lemma_list = [statement.name for statement in self.statements]
        for statement in self.statements:
            statement.dependent_lemmas = find_dependency(
                statement.formal_proof, lemma_list
            )

    def generate_statements(self):
        statements = []
        for statement in self.statements:
            statement_dict = statement.__dict__
            statement_dict["dependent_lemmas"] = ", ".join(statement.dependent_lemmas)
            statement_dict["type_TeX"] = None
            if statement.type in type_tex_dict.keys():
                statement_dict["type_TeX"] = type_tex_dict[statement.type]

            statements.append(statement_dict)
        return statements


def find_lean_files(folder_path):
    lean_files = []

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.lean'):
                relative_path = os.path.join(root, file)
                lean_files.append(relative_path)

    return lean_files

def generate_Tex(structure_dict : dict):
    env = jinja2.Environment(
        block_start_string="((*",
        block_end_string="*))",
        variable_start_string="(((",
        variable_end_string=")))",
        comment_start_string="((#",
        comment_end_string="#))",
        trim_blocks=True,
        autoescape=False,
        loader=jinja2.FileSystemLoader(os.path.abspath(".")),
    )

    template = env.get_template(os.path.join("blueprint", "template.tex"))
    output = template.render(structure_dict=structure_dict)
    with open(os.path.join("blueprint", "src", "demo.tex"), "w") as f:
        f.write(output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--project", type=str)
    arg = parser.parse_args()
    lean_files = find_lean_files(arg.project)
    structure_dict = {
        "statements" : []
    }
    for file in lean_files:
        leanfile = LeanFile(file)
        leanfile.prepare()
        leanfile.find_dependency()
        statements = leanfile.generate_statements()
        structure_dict["statements"].extend(statements)
    generate_Tex(structure_dict)
