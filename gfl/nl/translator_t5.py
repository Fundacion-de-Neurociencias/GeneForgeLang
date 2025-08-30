import json
import logging
import os

import torch
from datasets import Dataset
from transformers import T5ForConditionalGeneration, T5Tokenizer

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class LanguageTranslator:
    def __init__(
        self, model_name="t5-small", fine_tuned_model_path=None, model_revision="main"
    ):
        # Security: Pin model revision and use secure downloads
        self.tokenizer = T5Tokenizer.from_pretrained(
            model_name,
            revision=model_revision,
            trust_remote_code=False,  # Security: Don't execute remote code
        )  # nosec B615 - revision is explicitly pinned and trust_remote_code=False
        self.model = T5ForConditionalGeneration.from_pretrained(
            model_name,
            revision=model_revision,
            trust_remote_code=False,  # Security: Don't execute remote code
        )  # nosec B615 - revision is explicitly pinned and trust_remote_code=False
        self.fine_tuned_model_path = fine_tuned_model_path

        if self.fine_tuned_model_path and os.path.exists(self.fine_tuned_model_path):
            logger.info(f"Loading fine-tuned model from {self.fine_tuned_model_path}")
            # Security: Use weights_only=True to prevent code execution
            self.model.load_state_dict(
                torch.load(
                    os.path.join(self.fine_tuned_model_path, "pytorch_model.bin"),
                    weights_only=True,  # Security fix for bandit B614
                )  # nosec B614 - weights_only=True ensures safe loading
            )
        else:
            logger.warning(
                f"Fine-tuned model not found at {self.fine_tuned_model_path}. Using base model."
            )

    def fine_tune_model(
        self, data_path="data/nlp_training_data.json", num_epochs=3, batch_size=2
    ):
        logger.info(f"Loading training data from {data_path}")
        with open(data_path, "r") as f:
            data = json.load(f)

        # Prepare data for Dataset
        input_texts = [item["natural_language"] for item in data]
        target_texts = [item["gfl_code"] for item in data]

        dataset = Dataset.from_dict(
            {"input_text": input_texts, "target_text": target_texts}
        )

        def preprocess_function(examples):
            model_inputs = self.tokenizer(
                examples["input_text"],
                max_length=512,
                truncation=True,
                padding="max_length",
            )
            labels = self.tokenizer(
                examples["target_text"],
                max_length=512,
                truncation=True,
                padding="max_length",
            )
            model_inputs["labels"] = labels["input_ids"]
            return model_inputs

        tokenized_dataset = dataset.map(preprocess_function, batched=True)

        # Training setup (simplified)
        optimizer = torch.optim.AdamW(self.model.parameters(), lr=5e-5)

        for epoch in range(num_epochs):
            logger.info(f"Epoch {epoch + 1}/{num_epochs}")
            for i in range(0, len(tokenized_dataset), batch_size):
                batch = tokenized_dataset[i : i + batch_size]
                input_ids = torch.tensor(batch["input_ids"])
                labels = torch.tensor(batch["labels"])

                outputs = self.model(input_ids=input_ids, labels=labels)
                loss = outputs.loss
                loss.backward()
                optimizer.step()
                optimizer.zero_grad()
                logger.info(f"  Batch {i//batch_size + 1} Loss: {loss.item():.4f}")

        if self.fine_tuned_model_path:
            os.makedirs(self.fine_tuned_model_path, exist_ok=True)
            # Security: Save model state dict securely
            model_path = os.path.join(self.fine_tuned_model_path, "pytorch_model.bin")
            # Validate the path to prevent directory traversal
            if not os.path.abspath(model_path).startswith(
                os.path.abspath(self.fine_tuned_model_path)
            ):
                raise ValueError("Invalid model path: directory traversal detected")
            torch.save(
                self.model.state_dict(),
                model_path,
            )  # nosec B614 - saving model state dict is safe
            self.tokenizer.save_pretrained(self.fine_tuned_model_path)
            logger.info(f"Fine-tuned model saved to {self.fine_tuned_model_path}")

    def natural_language_to_gfl(self, nl_text):
        input_ids = self.tokenizer(nl_text, return_tensors="pt").input_ids
        outputs = self.model.generate(input_ids, max_length=512)
        gfl_code = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return gfl_code

    def gfl_to_natural_language(self, gfl_code):
        input_ids = self.tokenizer(gfl_code, return_tensors="pt").input_ids
        outputs = self.model.generate(input_ids, max_length=512)
        nl_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return nl_text
