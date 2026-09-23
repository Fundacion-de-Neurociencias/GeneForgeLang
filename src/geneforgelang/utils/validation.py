# gfl/validation_pipeline.py

from typing import Any, Callable

import pandas as pd
from sklearn.metrics import classification_report


class ValidationPipeline:
    def __init__(
        self,
        model: Any,
        data_loader: Callable[[], pd.DataFrame],
        label_column: str,
        feature_extractor: Callable[[dict[str, Any]], dict[str, Any]],
    ):
        """
        model: object implementing a predict() method
        data_loader: callable returning a DataFrame with relevant columns
        label_column: name of the column containing the target variable
        feature_extractor: callable transforming a row or AST into features
        """
        self.model = model
        self.data_loader = data_loader
        self.label_column = label_column
        self.feature_extractor = feature_extractor

    def run(self) -> dict[str, Any]:
        df = self.data_loader()
        X = []
        y_true = []

        for _, row in df.iterrows():
            gfl_ast = row["gfl_ast"]  # expects a column containing parsed ASTs
            label = row[self.label_column]
            features = self.feature_extractor(gfl_ast)
            X.append(features)
            y_true.append(label)

        y_pred = self.model.predict(X)

        report = classification_report(y_true, y_pred, output_dict=True)
        return {"report": report, "true_labels": y_true, "predicted_labels": y_pred}


# Ejemplo de uso:
if __name__ == "__main__":
    from geneforgelang.models.dummy import DummyGeneModel

    # from geneforgelang.utils.data_loader import load_validation_data --- NO ENCONTRADO ---

    def extract_features(ast):  # ejemplo simple
        return {
            "edit": ast.get("edit"),
            "target": ast.get("target"),
            "effect": ast.get("effect"),
        }

    pipeline = ValidationPipeline(
        model=DummyGeneModel(),
        # data_loader=load_validation_data,
        label_column="true_effect",
        feature_extractor=extract_features,
    )

    results = pipeline.run()
    print("Validation report:")
    print(results["report"])
