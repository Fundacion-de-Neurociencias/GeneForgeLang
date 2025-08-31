import scanpy as sc


def run_experiment(node):
    """
    Ejecuta un análisis real de scRNA-seq con Scanpy.
    Usa 'data/example.h5ad' como archivo de entrada (puedes cambiar la ruta si lo necesitas).
    """
    params = node.get("params", {})
    h5ad_path = "data/example.h5ad"

    # Si solo es imputación, simula o implementa aquí tu método real
    if params.get("imputation"):
        print(
            "    [Scanpy] Imputación (dummy; implementa aquí MAGIC, ALRA, etc. si quieres)..."
        )
        return {"status": "ok", "note": "Imputation step (no-op in demo)"}

    # Carga el archivo de datos
    print(f"    [Scanpy] Cargando datos desde {h5ad_path} ...")
    try:
        adata = sc.read_h5ad(h5ad_path)
    except Exception as e:
        print(f"    [ERROR] No se pudo cargar el archivo .h5ad: {e}")
        return {"status": "error", "error": str(e)}

    # Normalización
    if params.get("normalize"):
        print("    [Scanpy] Normalizando...")
        sc.pp.normalize_total(adata, target_sum=1e4)
        sc.pp.log1p(adata)

    # Filtro por número de células/genes con robustez anti-crash
    min_cells = params.get("min_cells")
    min_genes = params.get("min_genes")
    if min_cells is not None or min_genes is not None:
        print(f"    [Scanpy] Filtrando: min_cells={min_cells}, min_genes={min_genes}")
        initial_cells, initial_genes = adata.n_obs, adata.n_vars
        sc.pp.filter_cells(adata, min_genes=min_genes or 0)
        sc.pp.filter_genes(adata, min_cells=min_cells or 0)
        if adata.n_obs == 0 or adata.n_vars == 0:
            print(
                f"    [Scanpy][WARN] El filtrado eliminó todos los datos (celdas: {initial_cells}→{adata.n_obs}, genes: {initial_genes}→{adata.n_vars})"
            )
            return {"status": "error", "note": "El filtrado eliminó todos los datos"}

    # PCA solo si quedan datos suficientes
    if "pca_dims" in params:
        if adata.n_obs > 0 and adata.n_vars > 0:
            print(f"    [Scanpy] Calculando PCA ({params['pca_dims']} componentes)...")
            sc.tl.pca(adata, n_comps=params["pca_dims"])
        else:
            print("    [Scanpy][WARN] No se puede calcular PCA sin datos.")
            return {"status": "error", "note": "No hay datos para PCA tras el filtrado"}

    # Clustering simulado (puedes implementar real si quieres)
    target_clusters = params.get("target_cluster_count")
    if target_clusters:
        print(f"    [Scanpy] [Dummy] Objetivo de clusters: {target_clusters}")

    # Devuelve información relevante
    return {
        "status": "ok",
        "n_obs": adata.n_obs,
        "n_vars": adata.n_vars,
        "note": "Scanpy real ejecutado",
    }
