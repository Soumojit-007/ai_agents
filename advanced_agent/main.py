from dotenv import load_dotenv
from src.workflow import Workflow  # fixed import to directly import the class

load_dotenv()

def main():
    workflow = Workflow()  # fixed: now using the class, not module
    print("🤖 Welcome to Advanced Agent!\nAdvanced AI Agent Initialized.")

    while True:
        query = input("\nDeveloper Tools Query: ").strip()
        if query.lower() in {"quit", "exit"}:
            break

        if query:
            result = workflow.run(query)
            print(f"\n📝 Results for: {query}")
            print("*" * 60)

            if not result.companies:
                print("⚠️ No companies found for this query.\n")
                continue

            for i, company in enumerate(result.companies, 1):
                print(f"\n{i}. 🏢 {company.name}")
                print(f"   🌐 Website: {company.website}")
                print(f"   💰 Pricing: {company.pricing_model}")
                print(f"   📖 Open Source: {company.is_open_source}")

                # Accessing tech_Stack to match your models
                if company.tech_stack:
                    print(f"   🛠️  Tech Stack: {', '.join(company.tech_stack[:5])}")

                if company.language_support:
                    print(
                        f"   💻 Language Support: {', '.join(company.language_support[:5])}"
                    )

                if company.api_available is not None:
                    api_status = "✅ Available" if company.api_available else "❌ Not Available"
                    print(f"   🔌 API: {api_status}")

                if company.integration_capabilities:
                    print(
                        f"   🔗 Integrations: {', '.join(company.integration_capabilities[:4])}"
                    )

                if company.description and company.description != "Analysis failed":
                    print(f"   📝 Description: {company.description}")

                print()

            if result.analysis:
                print("Developer Recommendation: ")
                print("-" * 40)
                print(result.analysis)

if __name__ == "__main__":
    main()
