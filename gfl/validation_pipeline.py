# gfl/validation_pipeline.py

import pandas as pd
from typing import Dict, Any, Callable
from sklearn.metrics import classification_report

class ValidationPipeline:
    def __init__(self,
                 model: Any,
                 data_loader: Callable[[], pd.DataFrame],
                 label_column: str,
                 feature_extractor: Callable[[Dict[str, Any]], Dict[str, Any]]):
        """
        model: objeto con método predict()
        data_loader: función que retorna un DataFrame con columnas relevantes
        label_column: nombre de la columna que contiene la variable objetivo
        feature_extractor: función que transforma una fila o AST en features
        """
        self.model = model
        self.data_loader = data_loader
        self.label_column = label_column
        self.feature_extractor = feature_extractor

    def run(self) -> Dict[str, Any]:
        df = self.data_loader()
        X = []
        y_true = []

        for _, row in df.iterrows():
            gfl_ast = row['gfl_ast']  # se espera una columna con ASTs ya parseados
            label = row[self.label_column]
            features = self.feature_extractor(gfl_ast)
            X.append(features)
            y_true.append(label)

        y_pred = self.model.predict(X)

        report = classification_report(y_true, y_pred, output_dict=True)
        return {
            "report": report,
            "true_labels": y_true,
            "predicted_labels": y_pred
        }

# Ejemplo de uso:
if __name__ == "__main__":
    from dummy_model import DummyGeneModel
    from dummy_data import load_validation_data
    from inference_engine import InferenceEngine

    def extract_features(ast):  # ejemplo simple
        return {
            "edit": ast.get("edit"),
            "target": ast.get("target"),
            "effect": ast.get("effect")
        }

    pipeline = ValidationPipeline(
        model=DummyGeneModel(),
        data_loader=load_validation_data,
        label_column="true_effect",
        feature_extractor=extract_features
    )

    results = pipeline.run()
    print("Validation report:")
    print(results["report"])
