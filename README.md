# Boba Buddy Digital Waiter: End-to-End Conversational Drink Recommendation System
# Boba Buddy Digital Waiter：端到端 LLM 對話式飲料推薦系統
## From collaborative filtering to conversational recommendation with LLM orchestration, semantic retrieval, API testing, and UI evaluation.


Boba Buddy 原本是台灣手搖飲探索 App，主打幫使用者找附近飲料、看評價、快速發現合適飲品；網站也描述它是「台灣 #1 手搖飲料探索應用程式」，並提供 App Store / Google Play 下載。

傳統推薦邏輯偏向 item-based collaborative filtering，但 Digital Waiter 的目標是讓使用者像跟朋友或店員聊天一樣，透過自然語言描述「今天想喝清爽一點」、「不要奶」、「提神但不要咖啡」等需求，再由系統轉換成可執行的推薦流程。

我把專案從「聊天功能」提升成：**對話式推薦系統 Conversational Recommender System**
我利用CRS 的觀點進行測試，不是一次吐答案，而是透過多輪對話蒐集偏好，再逐步縮小選項。

**Boba Buddy Digital Waiter** is an end-to-end conversational recommendation feature for a Taiwanese bubble tea discovery app. The project upgrades a traditional recommendation experience into an LLM-powered digital waiter that can collect user preferences through multi-turn dialogue, understand vague drink requests, retrieve candidate drinks through backend APIs and database queries, rerank recommendations, and generate natural language responses.

My contribution focused on understanding the existing FastAPI / OpenAI / Supabase pipeline, testing the recommendation endpoint, comparing UI-level behavior with backend outputs, identifying failure modes in preference understanding and constraint following, and proposing a more reliable layered architecture for conversational recommendation.

Boba Buddy Digital Waiter 是一個端到端 LLM 對話式飲料推薦功能，目標是把傳統 item-based 推薦升級成像店員或朋友一樣的互動式推薦體驗。我的工作重點包含理解既有 FastAPI / OpenAI / Supabase 推薦 pipeline、測試推薦 endpoint、比較 UI 與 API 輸出、整理偏好理解與條件遵守的失敗模式，並提出更可 debug、可評估、可迭代的對話式推薦架構。


# Core Skills:
1. **LLM application architecture**
    
    
2. **UI/ API / backend debugging**
    
    
3. **Conversational recommender system thinking**
    
    
4. **Reliability / risk awareness**
    
    
5. **Product sense**


## Structure
boba-buddy-digital-waiter/

├── README.md

├── docs/

│   ├── system_architecture.md

│   ├── api_testing_plan.md

│   ├── ui_testing_plan.md

│   ├── failure_analysis.md

│   └── recommendation_risk_policy.md

├── examples/

│   ├── endpoint_request_examples.md

│   ├── conversation_test_cases.md

│   └── sample_outputs.json

├── reports/

│   ├── ui_vs_endpoint_analysis.md

│   └── improvement_proposal.md

└── demo/

    ├── screenshots/
    
    └── demo_video_link.md
    
