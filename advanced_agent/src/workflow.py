from typing import Dict, Any
from src.langgraph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from .models import ResearchState, CompanyInfo, CompanyAnalysis
from .firecrawl import FireCrawlService
from .prompts import DeveloperToolsPrompts
import json
import re


class Workflow:
    def __init__(self):
        self.firecrawl = FireCrawlService()
        # ✅ Use Groq’s official free models
        self.llm = ChatGroq(
            model="llama-3.1-8b-instant",   # or "mixtral-8x7b-32768"
            temperature=0.9
        )
        self.prompts = DeveloperToolsPrompts()
        self.workflow = self._build_workflow()

    def _build_workflow(self):
        graph = StateGraph()
        graph.add_node("extract_tools", self._extract_tools_step)
        graph.add_node("research", self._research_step)
        graph.add_node("analyze", self._analyze_step)
        graph.set_entry_point("extract_tools")
        graph.add_edge("extract_tools", "research")
        graph.add_edge("research", "analyze")
        graph.add_edge("analyze", END)
        return graph.compile()

    def _extract_tools_step(self, state: ResearchState) -> Dict[str, Any]:
        print(f"🔍 Finding articles about: {state.query}")
        article_query = f"{state.query} tools comparison best alternatives"
        search_results = self.firecrawl.search(article_query, num_results=3)

        all_content = ""
        for result in search_results:
            url = result.get("url", "")
            scraped = self.firecrawl.scrape(url)
            if scraped:
                for item in scraped:
                    all_content += item.get("markdown", "")[:1500] + "\n\n"

        messages = [
            SystemMessage(content=self.prompts.TOOL_EXTRACTION_SYSTEM),
            HumanMessage(content=self.prompts.tool_extraction_user(state.query, all_content))
        ]

        try:
            response = self.llm.invoke(messages)
            raw_lines = response.content.split("\n")

            tool_names = []
            for line in raw_lines:
                line = line.strip()
                if not line or "after analyzing" in line.lower():
                    continue
                line = re.sub(r'^\d+[\).\s-]+', '', line)
                if line and not line.lower().startswith("example"):
                    tool_names.append(line)

            print(f"✅ Extracted tools: {', '.join(tool_names[:5])}")
            return {"extracted_tools": tool_names}
        except Exception as e:
            print("❌ Tool extraction failed:", e)
            return {"extracted_tools": []}

    def _analyze_company_step(self, company_name: str, content_text: str) -> CompanyAnalysis:
        structured_llm = self.llm.with_structured_output(CompanyAnalysis)

        messages = [
            SystemMessage(content=self.prompts.TOOL_ANALYSIS_SYSTEM),
            HumanMessage(content=self.prompts.tool_analysis_user(company_name, content_text))
        ]

        try:
            analysis = structured_llm.invoke(messages)
            return analysis
        except Exception as e:
            print(f"❌ Analysis failed for {company_name}:", e)
            return CompanyAnalysis(
                pricing_model="Unknown",
                is_open_source=None,
                tech_stack=[],
                description="Analysis failed",
                api_available=None,
                language_support=[],
                integration_capabilities=[]
            )

    def _research_step(self, state: ResearchState) -> Dict[str, Any]:
        extracted_tools = getattr(state, "extracted_tools", [])

        if not extracted_tools:
            print("⚠️ No extracted tools found, falling back to direct search")
            search_results = self.firecrawl.search(state.query, num_results=3)
            tool_names = [result.get("title", "Unknown") for result in search_results]
        else:
            tool_names = extracted_tools[:4]
            print(f"🔬 Researching specific tools: {', '.join(tool_names)}")

        companies = []

        for tool_name in tool_names:
            # Try searching official site
            tool_search_results = self.firecrawl.search(tool_name + " official site", num_results=1)
            if tool_search_results:
                result = tool_search_results[0]
                url = result.get("url", f"https://www.{tool_name.replace(' ', '').lower()}.com")
                scraped = self.firecrawl.scrape(url)
                content = scraped[0].get("markdown", "") if scraped else f"No scraped content for {tool_name}"
            else:
                # Fallback if search fails
                url = f"https://www.{tool_name.replace(' ', '').lower()}.com"
                content = f"No scraped content available for {tool_name}"

            # Create company object
            company = CompanyInfo(
                name=tool_name,
                description=content,
                website=url,
                tech_stack=[],
                competitors=[]
            )

            # Run analysis
            analysis = self._analyze_company_step(company.name, content)

            company.pricing_model = analysis.pricing_model
            company.is_open_source = analysis.is_open_source
            company.tech_stack = analysis.tech_stack
            company.description = analysis.description
            company.api_available = analysis.api_available
            company.language_support = analysis.language_support
            company.integration_capabilities = analysis.integration_capabilities

            companies.append(company)

        return {"companies": companies}

    def _analyze_step(self, state: ResearchState) -> Dict[str, Any]:
        print("🧠 Generating final recommendations...")

        company_data = ",".join([json.dumps(company.__dict__) for company in state.companies])

        messages = [
            SystemMessage(content=self.prompts.RECOMMENDATIONS_SYSTEM),
            HumanMessage(content=self.prompts.recommendations_user(state.query, company_data))
        ]

        try:
            response = self.llm.invoke(messages)
            return {"analysis": response.content}
        except Exception as e:
            print("❌ Final analysis failed:", e)
            return {"analysis": "Analysis failed"}

    def run(self, query: str) -> ResearchState:
        initial_state = ResearchState(query=query)
        final_state = self.workflow.invoke(initial_state)
        if isinstance(final_state, ResearchState):
            return final_state
        return ResearchState(**final_state)
