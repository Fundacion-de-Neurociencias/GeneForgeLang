# Real Papers Validation Report (Priority 2)

## Metodología
Se extrajeron flujos de trabajo clave de 5 dominios de la literatura científica ("Materiales y Métodos") y se tradujeron a sintaxis GFL manual, estricta y sin sesgos procedentes del generador de ClawBio:
1. **RP_001_rnaseq_longitudinal.gfl**: Análisis de series temporales con DESeq2 (ej. Love et al.).
2. **RP_002_gwas_covariates.gfl**: Estudio GWAS con covariables complejas poblacionales en PLINK2.
3. **RP_003_crispr_mageck.gfl**: Pantalla de viabilidad celular CRISPR-Cas9 analizada con MAGeCK.
4. **RP_004_pharmacogenomics.gfl**: Integración multiómica de IC50 de fármacos con RNA-seq usando ElasticNet.
5. **RP_005_metagenomics.gfl**: Diversidad microbiana 16S rRNA analizada en QIIME2.

## Resultados de Validación (True Gaps Identificados)

El test bruto contra el `EnhancedSemanticValidator` ha revelado vacíos genuinos (*true gaps*) en la especificación actual de GFL:

### 1. Desconexión de Tipología Experimental (Tipos Desconocidos)
GFL actualmente restringe duramente los tipos de experimento que reconoce. Fallan:
- `Unknown experiment type 'RNAseq'`
- `Unknown experiment type 'GWAS'`
- `Unknown experiment type 'Metagenomics'`
- `Unknown experiment type 'CRISPR_cas9'`
*Gap Arquitectónico:* El registro de tipos de `experiment` está fuertemente codificado. Debería existir un mecanismo de registro dinámico a través de plugins o un estándar unificado para ómicas (ADR-0002).

### 2. Estructura Rígida de Bloques Core (Falta de Expresividad)
La estructura actual exige campos fijos que metodológicamente no siempre tienen sentido:
- `Missing required field 'tool' in experiment block`: En muchos métodos, la recolección o secuenciación (el *experiment*) es agnóstica de una "herramienta" de software (ej. secuenciar en Illumina NovaSeq). GFL obliga a especificar un `tool` en el bloque `experiment`, confundiendo la fase experimental con la fase analítica.
- `Missing required field 'strategy' in analysis block`: En la literatura, a menudo la estrategia *es* el modelo estadístico mismo. Obligar a añadir una `strategy` semántica en el bloque `analyze` es artificial en flujos como MAGeCK o ElasticNet.

### 3. Falta de Expresividad Metodológica (No Detectado por el Validador, pero Presente)
Aunque el validador falló en la capa estructural, el diseño manual de los GFL reveló inexpresividad en:
- **Diseños Longitudinales y Emparejados:** GFL no tiene primitivas para `time_series` ni emparejamiento por pacientes.
- **Modelos Estadísticos Complejos:** La inclusión de covariables dinámicas (`~ patient_id + condition + PC1 + PC2`) es vital en GWAS/RNA-seq y carece de representación estructurada en los bloques de diseño actuales.
- **Integración Multi-Input:** El bloque `analyze` asume un solo `input: Experiment`. En Farmacogenómica (`RP_004`) es obligatorio cruzar datos (RNA-seq + IC50), lo cual no es parseable fácilmente hoy.

## Conclusión Estratégica
La validación con literatura real ha purgado el sesgo. GFL es extremadamente coherente sintácticamente, pero semánticamente es inmaduro como "Scientific Language" universal. Adaptar GFL requerirá definir la Extensibilidad del Validador de Tipos y refinar los bloques `experiment` y `analyze` para que no asuman flujos analíticos monolíticos simples. 
Estos *gaps* formarán la base de los próximos Architectural Decision Records (ADRs).
