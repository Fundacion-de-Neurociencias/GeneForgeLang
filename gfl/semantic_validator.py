def validate_ast(ast):
    if isinstance(ast, list):
        return all(validate_ast(item) for item in ast)

    if not isinstance(ast, tuple):
        return False

    head, args = ast

    if head == "prime_edit":
        return isinstance(args, dict) and "target" in args and "edit" in args
    if head == "base_edit":
        return isinstance(args, dict) and "target" in args and "edit" in args
    if head == "prime_del":
        return isinstance(args, dict) and "target" in args and "position" in args
    if head == "peg":
        return isinstance(args, dict) and "sequence" in args and "length" in args
    if head == "nick_site":
        return isinstance(args, dict) and "location" in args
    if head == "reverse_transcriptase":
        return isinstance(args, dict) and "enzyme" in args
    if head == "pirna":
        return isinstance(args, dict) and "target" in args and "cluster" in args
    if head == "transposon":
        return isinstance(args, dict) and "element_name" in args
    if head == "endogenous_retrovirus":
        return isinstance(args, dict) and "locus" in args and "activity" in args
    if head == "mitochondrial_gene":
        return isinstance(args, dict) and "gene" in args and "function" in args

    return False
