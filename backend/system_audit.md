# System Audit & Refinement Plan

## 1. Missing Features / Gaps
- **Storage**: 
    - `Sentry` approves and "posts", but the content is lost (not saved to DB). Needs `store_in_vault`.
    - `Engineer` generates insights/charts but doesn't save the report text for future RAG.
    - `Analyst` reports are ephemeral.
- **RAG Capabilities**:
    - Current RAG is providing context to *Scout* (Brand Voice).
    - **User Request**: User wants to *chat* with this data (Brand Voice + Monitoring Data).
    - **Solution**: A dedicated "Guru" or "Manager" agent is needed to handle ad-hoc user queries outside the main "Drafting" flow.

## 2. Agent Refinements
- **Sentry**: Add `store_in_vault` call upon approval.
- **Engineer**: Add `store_in_vault` for the generated report.
- **Scout**: Ensure it's using the *latest* RAG tools.

## 3. New 'Guru' Agent (The Chatbot)
- **Role**: Omni-present assistant.
- **Tools**: 
    - `search_vault` (Brand Voice, Past Posts, Engineer Reports).
    - `monitor_social_media` (Direct access to data).
    - `generate_growth_chart` (On demand visualization).
- **Access**: Needs to be a node in the graph, likely a parallel start or a conditional entry point based on user input intent (Drafting vs Chatting).

## 4. Database Check
- `KnowledgeVault` table exists. We need to ensure we use strict categories (e.g., "brand_voice", "published_post", "growth_report") to make RAG effective.
