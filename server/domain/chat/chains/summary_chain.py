from langchain_core.prompts import load_prompt
from pydantic import BaseModel, Field


class Summary(BaseModel):
    title: str = Field(description="generated title")
    summary: str = Field(description="updated summary")


class SummaryChain:

    def __init__(self, llm):

        self.chain = load_prompt("prompt/summary.yaml") | llm.with_structured_output(
            Summary
        )

    def invoke(self, previous_summary: str, new_conversation: str):

        return self.chain.invoke(
            {"previous_summary": previous_summary, "new_conversation": new_conversation}
        )
