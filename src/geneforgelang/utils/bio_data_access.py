from bioservices import UniProt


class BioDataAccess:
    """
    A high-level class to simplify bioinformatics database access using bioservices.
    """

    def __init__(self):
        self.uniprot = UniProt()

    def get_protein_info(self, uniprot_id):
        """
        Retrieves protein information from UniProt.
        :param uniprot_id: UniProt accession ID (e.g., 'P0DP23')
        :return: A dictionary containing protein information or None if not found.
        """
        try:
            data = self.uniprot.retrieve(uniprot_id, frmt="xml")
            # You would typically parse the XML data here to extract specific information.
            # For simplicity, we'll just return a confirmation for now.
            return {"status": "success", "uniprot_id": uniprot_id, "data_length": len(data)}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def search_uniprot(self, query, columns=None, limit=10):
        """
        Searches UniProt for proteins matching a query.
        :param query: Search query (e.g., 'gene:TP53 human')
        :param columns: Comma-separated list of columns to retrieve (e.g., 'id,entry name,protein names')
        :param limit: Maximum number of results to return.
        :return: A list of dictionaries, each representing a protein entry.
        """
        try:
            results = self.uniprot.search(query, columns=columns, limit=limit)
            # bioservices.search returns a string, often tab-separated.
            # We need to parse it into a more usable format (e.g., list of dicts).
            if not results:
                return []

            lines = results.strip().split("\n")
            if not lines:
                return []

            header = [h.strip().lower().replace(" ", "_") for h in lines[0].split("\t")]
            parsed_results = []
            for line in lines[1:]:
                values = line.split("\t")
                if len(header) == len(values):
                    parsed_results.append(dict(zip(header, values)))
            return parsed_results
        except Exception as e:
            return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    # Example Usage:
    bio_access = BioDataAccess()

    print("--- Testing get_protein_info ---")
    protein_info = bio_access.get_protein_info("P0DP23")  # Example UniProt ID for Human TP53
    print(protein_info)

    print("\n--- Testing search_uniprot ---")
    search_results = bio_access.search_uniprot(
        query="gene:TP53 human", columns="id,entry name,protein names,organism", limit=5
    )
    if isinstance(search_results, list):
        for entry in search_results:
            print(entry)
    else:
        print(search_results)
