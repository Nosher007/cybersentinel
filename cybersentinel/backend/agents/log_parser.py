"""
TICKET-015 — Log Parser Agent.
Takes a raw log string and returns a structured ParsedLog Pydantic model
using LangChain with_structured_output() — no free-form text.
"""
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from backend.models.logs import ParsedLog, LogType

SYSTEM_PROMPT = """You are a log parsing agent for CyberSentinel, a cybersecurity monitoring system.
Extract structured fields from raw log lines produced by NovaPay infrastructure.
Use null for fields not present. Always preserve the exact raw log string."""

PARSE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "Parse this {log_type} log:\n\n{raw_log}"),
])


class LogParserAgent:

    def __init__(self, model: str = "gpt-4o-mini"):
        self._llm = ChatOpenAI(
            model=model,
            temperature=0,
            api_key=os.getenv("OPENAI_API_KEY", "sk-placeholder"),
        )

    def parse(self, raw_log: str, log_type: LogType) -> ParsedLog:
        if not raw_log or not raw_log.strip():
            raise ValueError("raw_log cannot be empty")

        structured_llm = self._llm.with_structured_output(ParsedLog)
        messages = PARSE_PROMPT.format_messages(
            raw_log=raw_log,
            log_type=log_type.value,
        )
        result: ParsedLog = structured_llm.invoke(messages)
        result.raw = raw_log
        result.log_type = log_type
        return result

    def parse_batch(self, logs: list[tuple[str, LogType]]) -> list[ParsedLog]:
        if not logs:
            return []
        return [self.parse(raw_log, log_type) for raw_log, log_type in logs]
