from transformers import pipeline

class explain_relevance():
    def __init__(self):
        self.llm_name = "tiny-llama"
        self.pipe = pipeline("text-generation",
                             model=self.llm_name,
                             torch_dtype="auto",
                             device_map="auto")


    def generate_explanation(self, query, caption):
        instruction = (
            "In one sentence, explain how the given query relates to the caption.\n"
            f"Query: {query}\nCaption: {caption}\n"
            f"Relation: The image is a good match to the query \'{query}\' because"
        )
        output = self.pipe(
            instruction,
            max_new_tokens=16,
            do_sample=False
        )
        # Extract and clean the response
        return output[0].get('generated_text').split("Relation:")[-1].strip()
