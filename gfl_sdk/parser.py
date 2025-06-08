import json
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
grammar_path = os.path.join(current_dir, "geneforge_grammar.json")

with open(grammar_path, "r", encoding="utf-8") as f:
    grammar = json.load(f)

def parse(phrase):
    # Aquí el parser usa grammar (simplificado)
    return {"parsed_phrase": phrase, "grammar_used": grammar}
