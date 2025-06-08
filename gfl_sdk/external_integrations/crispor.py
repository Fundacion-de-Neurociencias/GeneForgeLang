def get_crispor_guides(sequence: str, genome: str = 'hg38') -> dict:
    '''
    Simulación de la función que devuelve datos de ejemplo.
    '''
    # Datos simulados simples
    return {
        'guides': [
            {'sequence': 'GAGTCCGAGCAGAAGAAGA', 'score': 85, 'strand': '+'},
            {'sequence': 'CTTCTTCTGCTCGGACTC', 'score': 78, 'strand': '-'}
        ],
        'genome': genome,
        'input_sequence': sequence
    }
