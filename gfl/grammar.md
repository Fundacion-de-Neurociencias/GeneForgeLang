### 🔄 2025-05  New constructs
* **`vector()`** – delivery vector and its attributes  
* **`region()`** – chromosomal region / repeat block  
* **`governance()`** – ethical compliance flags  
* **`risk()`** – quantitative risk annotation  
* **`repeat_edit()`** – interruption of pathogenic triplet repeats
### 🔄 Mayo 2025 – Nuevas construcciones
* **ector()** – vector de entrega y atributos  
* **egion()** – región cromosómica / repetidos  
* **governance()** – flags de cumplimiento ético  
* **isk()** – anotación cuantitativa de riesgo  
* **epeat_edit()** – interrupción de repeticiones patogénicas
### 🔄 Mayo 2025 – Nuevas construcciones
* **ector()** – vector de entrega y atributos  
* **egion()** – región cromosómica / repetidos  
* **governance()** – flags de cumplimiento ético  
* **isk()** – anotación cuantitativa de riesgo  
* **epeat_edit()** – interrupción de repeticiones patogénicas
### 🔄 Mayo 2025 – Nuevas construcciones
* **ector()** – vector de entrega y atributos  
* **egion()** – región cromosómica / repetidos  
* **governance()** – flags de cumplimiento ético  
* **isk()** – anotación cuantitativa de riesgo  
* **epeat_edit()** – interrupción de repeticiones patogénicas
### 🔄 Mayo 2025 – Nuevas construcciones
* **ector()** – vector de entrega y atributos  
* **egion()** – región cromosómica / repetidos  
* **governance()** – flags de cumplimiento ético  
* **isk()** – anotación cuantitativa de riesgo  
* **epeat_edit()** – interrupción de repeticiones patogénicas
### 🔄 Mayo 2025 – Nuevas construcciones
* **ector()** – vector de entrega y atributos  
* **egion()** – región cromosómica / repetidos  
* **governance()** – flags de cumplimiento ético  
* **isk()** – anotación cuantitativa de riesgo  
* **epeat_edit()** – interrupción de repeticiones patogénicas
### 🔄 Mayo 2025 – Nuevas construcciones
* **ector()** – vector de entrega y atributos  
* **egion()** – región cromosómica / repetidos  
* **governance()** – flags de cumplimiento ético  
* **isk()** – anotación cuantitativa de riesgo  
* **epeat_edit()** – interrupción de repeticiones patogénicas
### 🆕 Mayo 2025 – Soporte de aminoácidos no canónicos
* `residue(ncAA:<name>)` — declara la inserción o edición de un residuo no estándar
**Nota (Mayo 2025)**  Una llamada puede incluir **varios atributos separados por comas**:

```gfl
vector(AAV9, serotype=9, tropism=retina, payload_kb=4.7)
target(gene:ADE2, organism:Saccharomyces_cerevisiae, locus:ChrXV, allele:wildtype)
```
Cada par `key:val` o `key=val` se guarda en `attrs`.
### 🔄 Mayo 2025 – Inmunogenicidad & atributos libres
* `immunity(alert:<type>, score:<0‑1>, cytokines:IL6|TNFα)`
* `edit()`/`vector()` ahora aceptan `variant`, `ligand`, `payload_kb`, etc.
## 🆕 Junio 2025 – Soporte de UTR y características de traducción endógena
* `uaug(start:AUG, frame:0|1|2)` — uORF start codon (in-frame o fuera de marco)
* `uorf(aa_length:<int>, frame:<0|1|2>)` — región de uORF con longitud y marco
* `structure(ΔG:<float>, region:[<start>-<end>])` — energía libre de estructura secundaria
* `gc_content(pct:<float>, region:[<start>-<end>]|whole)` — contenido G/C de una región o UTR completo
* `rbp_site(rbp:<name>, pos:<start>-<end>)` — sitio de unión de proteína RBP (e.g., Pumilio)
* `mir_site(mir:<name>, pos:<start>-<end>)` — sitio de unión de microRNA (e.g., miR34a)
