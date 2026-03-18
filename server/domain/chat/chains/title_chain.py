from pydantic import BaseModel, Field
from langchain_core.prompts import load_prompt


class TitleChain:

    def __init__(self, llm):

        self.chain = load_prompt("prompt/title.yaml") | llm.with_structured_output(
            Title
        )

    def invoke(self, conversation: str):

        return self.chain.invoke({"conversation": conversation})


class Title(BaseModel):
    title: str = Field(description="generated title")
