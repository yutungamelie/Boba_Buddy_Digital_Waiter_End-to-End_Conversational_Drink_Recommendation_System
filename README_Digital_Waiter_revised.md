# Boba Buddy Digital Waiter: End-to-End Conversational Drink Recommendation System
# Boba Buddy Digital Waiter：端到端 LLM 對話式飲料推薦系統

## From item-based recommendation to conversational recommendation with LLM orchestration, semantic retrieval, API testing, and UI evaluation
## 從傳統 item-based 推薦升級為結合 LLM 編排、語意檢索、API 測試與 UI 評估的對話式推薦系統

## Project Overview & My Contributions | 專案簡介與我負責的內容

### English

**Boba Buddy** is a Taiwanese bubble tea discovery app designed to help users explore nearby drink shops, browse drink information, and discover suitable beverages more easily. The original recommendation logic was closer to a traditional item-based recommendation system, while the **Digital Waiter** feature aims to create a more natural conversational experience: users can describe preferences such as “something refreshing,” “no milk,” or “energizing but not coffee,” and the system translates those natural-language needs into an executable recommendation workflow.

This project reframes the feature from a simple chatbot into a **conversational recommender system**. The goal is not only to return drink items, but also to collect user preferences through multi-turn dialogue, understand vague requests, retrieve candidate drinks through backend APIs and database queries, rerank recommendations, and generate user-friendly responses.

My contributions focused on understanding the existing FastAPI / OpenAI / Supabase recommendation pipeline, reviewing the original Digital Waiter codebase, testing the recommendation endpoint, comparing UI-level behavior with backend outputs, identifying failure modes in preference understanding and constraint following, and proposing a more reliable layered architecture for conversational recommendation. I also organized the testing process from both UI and endpoint perspectives to separate frontend symptoms from backend recommendation logic.

### 中文

**Boba Buddy** 是一個台灣手搖飲探索 App，目標是幫助使用者探索附近飲料店、瀏覽飲品資訊，並更容易找到適合自己的飲料。原本的推薦邏輯較接近傳統 item-based recommendation system；而 **Digital Waiter** 功能的目標，是讓使用者可以像和朋友或店員聊天一樣，用自然語言描述「今天想喝清爽一點」、「不要奶」、「提神但不要咖啡」等需求，再由系統轉換成可執行的推薦流程。

本專案將 Digital Waiter 從單純的聊天功能，重新定位為一套 **對話式推薦系統**。它不只是一次性吐出推薦結果，而是透過多輪對話蒐集使用者偏好、理解模糊需求、從後端 API 與資料庫檢索候選飲品、重新排序推薦結果，並生成自然、友善且符合限制條件的回覆。

我負責的內容包含理解既有 FastAPI / OpenAI / Supabase 推薦 pipeline、閱讀與整理 Digital Waiter 原始碼架構、測試推薦 endpoint、比較 UI 行為與後端輸出、整理偏好理解與條件遵守的失敗模式，並提出更可靠、可 debug、可評估、可迭代的對話式推薦架構。我也從 UI 與 endpoint 兩個層面規劃測試流程，協助區分前端互動問題與後端推薦邏輯問題。

## Repository Structure | Repository 架構

```text
boba-buddy-digital-waiter/
├── README.md
│   └── Project overview, contribution summary, and repository guide
│
├── docs/
│   ├── system_architecture.md
│   ├── llm_workflow_notes.md
│   ├── recommendation_pipeline.md
│   ├── api_testing_plan.md
│   ├── ui_testing_plan.md
│   ├── failure_analysis.md
│   └── recommendation_risk_policy.md
│
├── examples/
│   ├── endpoint_request_examples.md
│   ├── conversation_test_cases.md
│   ├── sample_prompts.md
│   └── sample_outputs.json
│
├── src/
│   ├── preference_extraction/
│   │   ├── intent_detection.py
│   │   ├── preference_summary.py
│   │   └── constraint_parser.py
│   │
│   ├── retrieval_and_ranking/
│   │   ├── embedding_query_builder.py
│   │   ├── candidate_retrieval.py
│   │   └── reranking.py
│   │
│   └── evaluation/
│       ├── constraint_match_check.py
│       ├── ui_endpoint_comparison.py
│       └── recommendation_reliability_score.py
│
├── reports/
│   ├── ui_vs_endpoint_analysis.md
│   ├── improvement_proposal.md
│   └── product_iteration_notes.md
│
├── demo/
│   ├── screenshots/
│   └── demo_video_link.md
│
├── requirements.txt
└── LICENSE
```
