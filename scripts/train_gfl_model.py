from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments

# 1. Definir el modelo y el tokenizer
model_name = (
    "distilgpt2"  # Puedes probar con "distilgpt2" para un entrenamiento más rápido
)
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# Asegúrate de que el tokenizer tenga un pad_token. GPT2 no lo tiene por defecto.
if tokenizer.pad_token is None:
    tokenizer.add_special_tokens({"pad_token": "[PAD]"})
    model.resize_token_embeddings(len(tokenizer))  # Redimensionar embeddings del modelo


# 2. Cargar y preparar los datos de entrenamiento
# Usamos TextDataset para cargar un archivo de texto simple
# block_size es importante: define cuántos tokens (palabras/partes de palabras)
# el modelo considerará a la vez en cada "bloque" de entrenamiento.
# Un valor común para gpt2 y tareas de generación de texto.
def tokenize_function(examples):
    # Asegúrate de que la tokenización maneje correctamente las líneas como textos separados o concatenados
    # para fine-tuning de causal language modeling, es común concatenar todo y luego dividir en bloques.
    return tokenizer(examples["text"])


print("Cargando dataset...")
# El dataset se carga desde el archivo de texto que creaste
# Puedes ajustar la ruta si es necesario.
dataset = load_dataset("text", data_files={"train": "examples/gfl_training_data.txt"})

print("Tokenizando dataset...")
tokenized_datasets = dataset.map(
    tokenize_function,
    batched=True,
    num_proc=1,  # Puedes aumentar si tienes muchos núcleos de CPU y quieres más velocidad
    remove_columns=["text"],
)

# Agrupar textos en bloques de `block_size`
block_size = 128  # Tamaño del bloque de tokens para el entrenamiento


def group_texts(examples):
    # Concatenar todos los textos.
    concatenated_examples = {k: sum(examples[k], []) for k in examples.keys()}
    total_length = len(concatenated_examples[list(examples.keys())[0]])
    # Eliminamos el exceso para que todos los bloques tengan el mismo tamaño
    total_length = (total_length // block_size) * block_size
    # Dividir por chunks de block_size
    result = {
        k: [t[i : i + block_size] for i in range(0, total_length, block_size)]
        for k, t in concatenated_examples.items()
    }
    result["labels"] = result["input_ids"].copy()
    return result


lm_datasets = tokenized_datasets.map(
    group_texts,
    batched=True,
    num_proc=1,  # Puedes aumentar si tienes muchos núcleos de CPU
)

# 3. Configurar los argumentos de entrenamiento
training_args = TrainingArguments(
    output_dir="./gfl_finetuned_model",  # Donde se guardará el modelo entrenado
    overwrite_output_dir=True,
    num_train_epochs=100,  # Número de veces que el modelo verá todos los datos (puedes ajustar)
    per_device_train_batch_size=8,  # Número de ejemplos por batch (reducir si hay OOM)
    save_steps=10_000,  # Guardar el modelo cada X pasos (ajustar si epochs es pequeño)
    save_total_limit=2,  # Mantener solo los 2 últimos checkpoints
    logging_dir="./gfl_finetuned_logs",  # Directorio para logs de entrenamiento
    logging_steps=500,  # Frecuencia de loggeo
    report_to="none",  # Desactivar reportes a Weights & Biases u otros
    # Puedes añadir más argumentos para optimizar o para GPUs:
    # fp16=True, # Usar precisión media si tienes GPU compatible para acelerar
)

# 4. Crear el Trainer y empezar el entrenamiento
print("Iniciando entrenamiento del modelo...")
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=lm_datasets["train"],
)

trainer.train()

# 5. Guardar el modelo y el tokenizer afinados
print("Entrenamiento completado. Guardando modelo y tokenizer afinados...")
model.save_pretrained("./gfl_finetuned_model")
tokenizer.save_pretrained("./gfl_finetuned_model")
print("Modelo y tokenizer afinados guardados en: ./gfl_finetuned_model")
