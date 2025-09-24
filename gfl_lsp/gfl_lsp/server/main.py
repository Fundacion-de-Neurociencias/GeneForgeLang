import asyncio
from typing import List
from lsprotocol.types import (
    Diagnostic, Position, Range, CompletionItem, CompletionItemKind,
    CompletionList, CompletionOptions, DiagnosticSeverity, Hover,
    MarkupContent, MarkupKind, InsertTextFormat
)
from pygls.server import LanguageServer

# Importamos nuestras propias herramientas de GFL directamente desde el proyecto
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from gfl.api import parse, validate
from gfl.error_handling import EnhancedValidationResult, ErrorSeverity

# Creamos una instancia del servidor de lenguaje
server = LanguageServer("gfl-lsp", "v0.1.0")

# Diccionario de documentación para palabras clave de GFL
KEYWORD_DOCS = {
    "guided_discovery": "Bloque principal para orquestar un ciclo de descubrimiento iterativo guiado por IA.",
    "timeline": "Define un flujo de trabajo basado en una secuencia de eventos cronológicos.",
    "contract": "Define el esquema de datos esperado para las entradas (inputs) y salidas (outputs) de un paso.",
    "rules": "Define reglas lógicas para la validación y transformación de datos.",
    "hypothesis": "Define hipótesis científicas con condiciones lógicas.",
    "pathways": "Define rutas biológicas como listas de genes o componentes.",
    "complexes": "Define complejos biológicos como conjuntos de subunidades.",
    "experiment": "Define un experimento con herramientas y parámetros.",
    "analyze": "Define análisis de datos con métodos específicos.",
    "refine_data": "Refina datos mediante técnicas de procesamiento.",
    "optimize": "Optimiza parámetros usando algoritmos de búsqueda.",
    "simulate": "Simula procesos biológicos o experimentales."
}

def _validate(ls: LanguageServer, params):
    """
    Función interna para validar un documento y publicar los diagnósticos.
    """
    text_doc = ls.workspace.get_document(params.text_document.uri)
    source = text_doc.source
    diagnostics: List[Diagnostic] = []

    try:
        # 1. Parsear el código fuente
        ast = parse(source)

        # 2. Validar el AST con resultado mejorado
        validation_result = validate(ast, enhanced=True)

        # 3. Convertir los errores de GFL a Diagnósticos de LSP
        if isinstance(validation_result, EnhancedValidationResult):
            # Procesar errores sintácticos
            for error in validation_result.syntax_errors:
                line = error.location.line - 1 if error.location and error.location.line > 0 else 0
                col = error.location.column - 1 if error.location and error.location.column > 0 else 0

                d = Diagnostic(
                    range=Range(
                        start=Position(line=line, character=col),
                        end=Position(line=line, character=col + len(error.context or ''))
                    ),
                    message=f"[{error.code}] {error.message}",
                    severity=DiagnosticSeverity.Error
                )
                diagnostics.append(d)

            # Procesar errores semánticos
            for error in validation_result.semantic_errors:
                line = error.location.line - 1 if error.location and error.location.line > 0 else 0
                col = error.location.column - 1 if error.location and error.location.column > 0 else 0

                # Determinar severidad
                severity = DiagnosticSeverity.Error  # Error por defecto
                if error.severity == ErrorSeverity.WARNING:
                    severity = DiagnosticSeverity.Warning
                elif error.severity == ErrorSeverity.INFO:
                    severity = DiagnosticSeverity.Information
                elif error.severity == ErrorSeverity.HINT:
                    severity = DiagnosticSeverity.Hint

                d = Diagnostic(
                    range=Range(
                        start=Position(line=line, character=col),
                        end=Position(line=line, character=col + len(error.context or ''))
                    ),
                    message=f"[{error.code}] {error.message}",
                    severity=severity
                )
                diagnostics.append(d)
        else:
            # Resultado legacy (lista de strings)
            for i, error_msg in enumerate(validation_result):
                d = Diagnostic(
                    range=Range(
                        start=Position(line=i, character=0),
                        end=Position(line=i, character=50)
                    ),
                    message=f"[VALIDATION] {error_msg}",
                    severity=DiagnosticSeverity.Error
                )
                diagnostics.append(d)

    except Exception as e:
        # Manejar errores generales del parser
        d = Diagnostic(
            range=Range(
                start=Position(line=0, character=0),
                end=Position(line=0, character=10)
            ),
            message=f"[PARSE_ERROR] {str(e)}",
                severity=DiagnosticSeverity.Error
        )
        diagnostics.append(d)

    # 4. Publicar los diagnósticos en el editor
    ls.publish_diagnostics(text_doc.uri, diagnostics)


@server.feature(
    'textDocument/completion',
    CompletionOptions(trigger_characters=[':', ' ', '(', '\n'])
)
def completions(params):
    """
    Ofrece sugerencias de autocompletado basadas en el contexto.
    """
    items = []
    document = server.workspace.get_document(params.text_document.uri)
    current_line = document.lines[params.position.line].strip()
    current_line_text = document.lines[params.position.line]

    try:
        # Parsear el documento completo para obtener el AST
        source = document.source
        ast = parse(source)

        # Determinar el contexto actual (bloque padre)
        parent_context = _get_parent_context(document, params.position.line)

        # A. Autocompletado Contextual Anidado
        if parent_context:
            context_items = _get_contextual_completions(parent_context)
            items.extend(context_items)

        # B. Autocompletado de Bloques de Alto Nivel con Snippets
        # Si la línea actual está vacía o tiene indentación cero
        elif not document.lines[params.position.line].startswith('  '):
            # Snippet para guided_discovery
            # Snippet para guided_discovery
            items.append(CompletionItem(
                label="guided_discovery",
                kind=CompletionItemKind.Snippet,
                detail="GFL block: guided_discovery",
                documentation="Bloque principal para orquestar un ciclo de descubrimiento iterativo guiado por IA.",
                insert_text="guided_discovery:\n  design_params:\n    $1\n  active_learning_params:\n    $2\n  objective:\n    $3\n  budget:\n    max_cycles: ${4:10}\n  run:\n    $5\n  output: ${6:final_candidates}",
                insert_text_format=InsertTextFormat.Snippet
            ))

            # Snippet para timeline
            items.append(CompletionItem(
                label="timeline",
                kind=CompletionItemKind.Snippet,
                detail="GFL block: timeline",
                documentation="Define un flujo de trabajo basado en una secuencia de eventos cronológicos.",
                insert_text="timeline:\n  name: \"${1:Mi Terapia}\"\n  description: \"${2:Descripción del protocolo}\"\n  events:\n    - at: \"T0\"\n      actions:\n        - ${3:do_something}",
                insert_text_format=InsertTextFormat.Snippet
            ))

            # Otras palabras clave
            keywords = [
                'import_schemas', 'rules', 'hypothesis',
                'pathways', 'complexes', 'experiment', 'analyze',
                'refine_data', 'optimize', 'simulate'
            ]
            for keyword in keywords:
                items.append(CompletionItem(
                    label=keyword,
                    kind=CompletionItemKind.Keyword,
                    detail=f"GFL block: {keyword}",
                    documentation=f"Define a {keyword} block in your GFL workflow"
                ))

        # C. Autocompletado de Tipos de Esquemas
        elif 'type:' in current_line:
            # Buscar esquemas importados
            if isinstance(ast, dict) and 'import_schemas' in ast:
                schema_files = ast['import_schemas']
                if isinstance(schema_files, list):
                    for schema_file in schema_files:
                        try:
                            # Cargar esquemas usando el schema loader
                            from gfl.schema_loader import load_schemas_from_files
                            from gfl.error_handling import EnhancedValidationResult
                            from gfl.schema_loader import get_global_schema_loader
                            result = EnhancedValidationResult()
                            load_schemas_from_files([schema_file], result)
                            loader = get_global_schema_loader()
                            schemas = loader.get_all_schemas()

                            for schema_name, schema_def in schemas.items():
                                if isinstance(schema_def, dict) and 'type' in schema_def:
                                    items.append(CompletionItem(
                                        label=schema_name,
                                        kind=CompletionItemKind.Class,
                                        detail=f"Schema type: {schema_name}",
                                        documentation=f"Use schema type {schema_name} from {schema_file}"
                                    ))
                        except Exception:
                            # Si no se puede cargar el esquema, continuar
                            continue

        # D. Autocompletado de Entidades Biológicas
        elif 'pathway(' in current_line or current_line.endswith('pathway('):
            # Buscar pathways definidos en el documento
            if isinstance(ast, dict) and 'pathways' in ast:
                pathways = ast['pathways']
                if isinstance(pathways, dict):
                    for pathway_name in pathways.keys():
                        items.append(CompletionItem(
                            label=pathway_name,
                            kind=CompletionItemKind.Value,
                            detail=f"Pathway: {pathway_name}",
                            documentation=f"Use defined pathway {pathway_name}"
                        ))

        elif 'complex(' in current_line or current_line.endswith('complex('):
            # Buscar complexes definidos en el documento
            if isinstance(ast, dict) and 'complexes' in ast:
                complexes = ast['complexes']
                if isinstance(complexes, dict):
                    for complex_name in complexes.keys():
                        items.append(CompletionItem(
                            label=complex_name,
                            kind=CompletionItemKind.Value,
                            detail=f"Complex: {complex_name}",
                            documentation=f"Use defined complex {complex_name}"
                        ))

        # E. Autocompletado de herramientas comunes
        elif 'tool:' in current_line:
            common_tools = [
                'CRISPR_cas9', 'CRISPR_cas12', 'CRISPR_cas13',
                'RNA_seq', 'ChIP_seq', 'ATAC_seq', 'scRNA_seq',
                'qPCR', 'Western_blot', 'Flow_cytometry',
                'Microscopy', 'Mass_spectrometry'
            ]
            for tool in common_tools:
                items.append(CompletionItem(
                    label=tool,
                    kind=CompletionItemKind.Function,
                    detail=f"Tool: {tool}",
                    documentation=f"Use {tool} as experimental tool"
                ))

        # F. Autocompletado de tipos de experimento
        elif 'type:' in current_line and 'tool:' in current_line:
            experiment_types = [
                'gene_editing', 'gene_expression', 'protein_analysis',
                'cell_analysis', 'molecular_interaction', 'pathway_analysis',
                'drug_screening', 'phenotype_analysis'
            ]
            for exp_type in experiment_types:
                items.append(CompletionItem(
                    label=exp_type,
                    kind=CompletionItemKind.Enum,
                    detail=f"Experiment type: {exp_type}",
                    documentation=f"Use {exp_type} as experiment type"
                ))

        # G. Autocompletado de métodos de análisis
        elif 'method:' in current_line:
            analysis_methods = [
                'differential_expression', 'pathway_enrichment', 'clustering',
                'dimensionality_reduction', 'network_analysis', 'statistical_test',
                'machine_learning', 'time_series_analysis'
            ]
            for method in analysis_methods:
                items.append(CompletionItem(
                    label=method,
                    kind=CompletionItemKind.Method,
                    detail=f"Analysis method: {method}",
                    documentation=f"Use {method} for data analysis"
                ))

    except Exception as e:
        # Si hay error en el parsing, devolver lista vacía
        pass

    return CompletionList(is_incomplete=False, items=items)


def _get_parent_context(document, line_number):
    """
    Determina el bloque padre de la línea actual.
    """
    # Buscar hacia atrás para encontrar el bloque padre
    for i in range(line_number - 1, -1, -1):
        line = document.lines[i].strip()
        if line.endswith(':') and not line.startswith('  '):
            return line.rstrip(':')
        # Si encontramos una línea sin indentación que no es un bloque, paramos
        if not document.lines[i].startswith('  ') and line != '':
            break
    return None


def _get_contextual_completions(parent_context):
    """
    Devuelve sugerencias contextuales basadas en el bloque padre.
    """
    items = []
    
    if parent_context == 'budget':
        contextual_keywords = [
            ('max_cycles', 'Número máximo de ciclos de optimización'),
            ('convergence_threshold', 'Umbral de convergencia para detener la optimización'),
            ('target_objective_value', 'Valor objetivo deseado')
        ]
        for keyword, description in contextual_keywords:
            items.append(CompletionItem(
                label=keyword,
                kind=CompletionItemKind.Property,
                detail=f"Budget parameter: {keyword}",
                documentation=description
            ))
    
    elif parent_context == 'contract':
        contextual_keywords = [
            ('inputs', 'Definición de entradas esperadas'),
            ('outputs', 'Definición de salidas esperadas')
        ]
        for keyword, description in contextual_keywords:
            items.append(CompletionItem(
                label=keyword,
                kind=CompletionItemKind.Property,
                detail=f"Contract parameter: {keyword}",
                documentation=description
            ))
    
    elif parent_context == 'active_learning_params':
        contextual_keywords = [
            ('strategy', 'Estrategia de aprendizaje activo'),
            ('active_learning', 'Configuración de aprendizaje activo')
        ]
        for keyword, description in contextual_keywords:
            items.append(CompletionItem(
                label=keyword,
                kind=CompletionItemKind.Property,
                detail=f"Active learning parameter: {keyword}",
                documentation=description
            ))
    
    return items


@server.feature('textDocument/hover')
def hover(params):
    """
    Muestra información contextual cuando el usuario pasa el ratón sobre un token.
    """
    document = server.workspace.get_document(params.text_document.uri)
    pos = params.position

    # Obtener la palabra/token debajo del cursor
    word = document.word_at_position(pos)

    if not word:
        return None

    # A. Hover sobre palabras clave de GFL
    if word in KEYWORD_DOCS:
        return Hover(contents=MarkupContent(
            kind=MarkupKind.Markdown,
            value=f"**{word}**\n\n---\n\n{KEYWORD_DOCS[word]}"
        ))

    try:
        # Parsear el documento para obtener el AST
        source = document.source
        ast = parse(source)

        # A. Hover sobre IDs de Hipótesis
        if 'hypothesis' in ast and isinstance(ast['hypothesis'], dict):
            hypothesis = ast['hypothesis']
            if hypothesis.get('id') == word:
                description = hypothesis.get('description', 'No description available.')
                return Hover(contents=MarkupContent(
                    kind=MarkupKind.Markdown,
                    value=f"**Hypothesis: {word}**\n\n---\n\n{description}"
                ))

        # B. Hover sobre Tipos de Esquemas
        if 'type:' in document.lines[pos.line]:
            # Buscar esquemas importados
            if 'import_schemas' in ast and isinstance(ast['import_schemas'], list):
                schema_files = ast['import_schemas']
                for schema_file in schema_files:
                    try:
                        from gfl.schema_loader import load_schemas_from_files
                        from gfl.error_handling import EnhancedValidationResult
                        from gfl.schema_loader import get_global_schema_loader
                        result = EnhancedValidationResult()
                        load_schemas_from_files([schema_file], result)
                        loader = get_global_schema_loader()
                        loaded_schemas = loader.get_all_schemas()

                        if word in loaded_schemas:
                            schema_def = loaded_schemas[word]
                            contents_md = f"**Schema: `{word}`**\n\n---\n\n"
                            contents_md += f"**Base Type:** `{schema_def.base_type}`\n\n"

                            if schema_def.description:
                                contents_md += f"**Description:** {schema_def.description}\n\n"

                            if schema_def.attributes:
                                contents_md += "**Attributes:**\n"
                                for attr, props in schema_def.attributes.items():
                                    required = props.get('required', False)
                                    attr_type = props.get('type', 'unknown')
                                    contents_md += f"- `{attr}`: (type: `{attr_type}`, required: `{required}`)\n"

                            return Hover(contents=MarkupContent(
                                kind=MarkupKind.Markdown,
                                value=contents_md
                            ))
                    except Exception:
                        continue

        # C. Hover sobre Entidades Biológicas (Pathways)
        if 'pathways' in ast and isinstance(ast['pathways'], dict):
            pathways = ast['pathways']
            if word in pathways:
                pathway_def = pathways[word]
                contents_md = f"**Pathway: {word}**\n\n---\n\n"

                if 'description' in pathway_def:
                    contents_md += f"**Description:** {pathway_def['description']}\n\n"

                if 'genes' in pathway_def:
                    genes = pathway_def['genes']
                    if isinstance(genes, list):
                        contents_md += f"**Genes ({len(genes)}):**\n"
                        for gene in genes[:10]:  # Mostrar máximo 10 genes
                            contents_md += f"- `{gene}`\n"
                        if len(genes) > 10:
                            contents_md += f"- ... and {len(genes) - 10} more genes\n"

                return Hover(contents=MarkupContent(
                    kind=MarkupKind.Markdown,
                    value=contents_md
                ))

        # D. Hover sobre Entidades Biológicas (Complexes)
        if 'complexes' in ast and isinstance(ast['complexes'], dict):
            complexes = ast['complexes']
            if word in complexes:
                complex_def = complexes[word]
                contents_md = f"**Complex: {word}**\n\n---\n\n"

                if 'description' in complex_def:
                    contents_md += f"**Description:** {complex_def['description']}\n\n"

                if 'subunits' in complex_def:
                    subunits = complex_def['subunits']
                    if isinstance(subunits, list):
                        contents_md += f"**Subunits ({len(subunits)}):**\n"
                        for subunit in subunits[:10]:  # Mostrar máximo 10 subunidades
                            contents_md += f"- `{subunit}`\n"
                        if len(subunits) > 10:
                            contents_md += f"- ... and {len(subunits) - 10} more subunits\n"

                return Hover(contents=MarkupContent(
                    kind=MarkupKind.Markdown,
                    value=contents_md
                ))

        # E. Hover sobre Herramientas Experimentales
        if 'tool:' in document.lines[pos.line]:
            tool_descriptions = {
                'CRISPR_cas9': 'CRISPR-Cas9 gene editing system for precise DNA modifications',
                'CRISPR_cas12': 'CRISPR-Cas12 gene editing system with different PAM requirements',
                'CRISPR_cas13': 'CRISPR-Cas13 system for RNA targeting and editing',
                'RNA_seq': 'RNA sequencing for transcriptome analysis',
                'ChIP_seq': 'Chromatin Immunoprecipitation sequencing for protein-DNA interactions',
                'ATAC_seq': 'Assay for Transposase-Accessible Chromatin sequencing',
                'scRNA_seq': 'Single-cell RNA sequencing for cellular heterogeneity analysis',
                'qPCR': 'Quantitative Polymerase Chain Reaction for gene expression quantification',
                'Western_blot': 'Western blotting for protein detection and quantification',
                'Flow_cytometry': 'Flow cytometry for cell analysis and sorting',
                'Microscopy': 'Microscopy techniques for cellular and molecular imaging',
                'Mass_spectrometry': 'Mass spectrometry for protein and metabolite analysis'
            }

            if word in tool_descriptions:
                return Hover(contents=MarkupContent(
                    kind=MarkupKind.Markdown,
                    value=f"**Tool: {word}**\n\n---\n\n{tool_descriptions[word]}"
                ))

        # F. Hover sobre Tipos de Experimento
        if 'type:' in document.lines[pos.line] and 'tool:' in document.lines[pos.line]:
            experiment_type_descriptions = {
                'gene_editing': 'Modification of DNA sequences using gene editing tools',
                'gene_expression': 'Analysis of gene expression levels and patterns',
                'protein_analysis': 'Study of protein structure, function, and interactions',
                'cell_analysis': 'Analysis of cellular properties and behaviors',
                'molecular_interaction': 'Study of interactions between biomolecules',
                'pathway_analysis': 'Analysis of biological pathways and networks',
                'drug_screening': 'Testing of compounds for biological activity',
                'phenotype_analysis': 'Analysis of observable characteristics or traits'
            }

            if word in experiment_type_descriptions:
                return Hover(contents=MarkupContent(
                    kind=MarkupKind.Markdown,
                    value=f"**Experiment Type: {word}**\n\n---\n\n{experiment_type_descriptions[word]}"
                ))

        # G. Hover sobre Métodos de Análisis
        if 'method:' in document.lines[pos.line]:
            method_descriptions = {
                'differential_expression': 'Identify genes with significantly different expression levels',
                'pathway_enrichment': 'Determine which biological pathways are over-represented',
                'clustering': 'Group similar data points or samples together',
                'dimensionality_reduction': 'Reduce the number of variables while preserving information',
                'network_analysis': 'Analyze relationships and interactions in biological networks',
                'statistical_test': 'Apply statistical tests to validate hypotheses',
                'machine_learning': 'Use ML algorithms to find patterns in data',
                'time_series_analysis': 'Analyze data points collected over time'
            }

            if word in method_descriptions:
                return Hover(contents=MarkupContent(
                    kind=MarkupKind.Markdown,
                    value=f"**Analysis Method: {word}**\n\n---\n\n{method_descriptions[word]}"
                ))

    except Exception as e:
        # Si hay error, devolver None
        pass

    return None


@server.feature('textDocument/didOpen')
async def did_open(ls: LanguageServer, params):
    """
    Se ejecuta cuando se abre un fichero.
    """
    ls.show_message('GFL LSP: Documento abierto.')
    _validate(ls, params)

@server.feature('textDocument/didChange')
async def did_change(ls: LanguageServer, params):
    """
    Se ejecuta cuando se modifica un fichero.
    """
    _validate(ls, params)


def main():
    """
    Punto de entrada para iniciar el servidor.
    """
    print("Iniciando GFL Language Server...")
    server.start_io()

if __name__ == '__main__':
    main()
