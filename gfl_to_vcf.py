def gfl_to_vcf(gfl_expr):
    parsed = parse_gfl(gfl_expr)
    if parsed["type"] != "v":
        return None
    chrom = parsed["id"].split(".")[0]
    pos = parsed["id"].split(".")[1].split(">")[0][1:]
    ref = parsed["id"].split(">")[0][-1]
    alt = parsed["id"].split(">")[1]
    return f"{chrom}\t{pos}\t.\t{ref}\t{alt}\t.\t.\t."