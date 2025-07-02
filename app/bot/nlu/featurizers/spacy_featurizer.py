from typing import Any, Dict, List
from app.bot.nlu.pipeline import NLUComponent


class SpacyFeaturizer(NLUComponent):
    """Spacy featurizer component that processes text and adds spacy features."""

    def __init__(self, model_name: str):
        import spacy

        try:
            self.tokenizer = spacy.load(model_name)
        except OSError as e:
            # If the specified model is not available, try fallback models
            fallback_models = ["en_core_web_md", "en_core_web_sm", "en"]
            
            print(f"Warning: Could not load spaCy model '{model_name}': {e}")
            
            for fallback_model in fallback_models:
                try:
                    print(f"Trying fallback model: {fallback_model}")
                    self.tokenizer = spacy.load(fallback_model)
                    print(f"Successfully loaded fallback model: {fallback_model}")
                    break
                except OSError:
                    continue
            else:
                # If no models work, raise an informative error
                raise OSError(
                    f"Could not load spaCy model '{model_name}' or any fallback models. "
                    f"Please install a spaCy model using: python -m spacy download en_core_web_md"
                )

    def train(self, training_data: List[Dict[str, Any]], model_path: str) -> None:
        for example in training_data:
            if example.get("text", "").strip() == "":
                continue
            example["spacy_doc"] = self.tokenizer(example["text"])

    def load(self, model_path: str) -> bool:
        """Nothing to load for spacy featurizer."""
        return True

    def process(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process text with spacy and add doc to message."""
        if not message.get("text"):
            return message

        doc = self.tokenizer(message["text"])
        message["spacy_doc"] = doc
        return message
