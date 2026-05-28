## Boba Buddy Digital Waiter: End-to-End Conversational Drink Recommendation System  
# Boba Buddy Digital Waiter：端到端對話式飲料推薦系統

## From Item-Based Recommendation to Conversational Recommendation with LLM Orchestration, Semantic Retrieval, API Testing, and UI Evaluation  
## 從品項式推薦升級為結合大型語言模型協作流程、語意檢索、應用程式介面測試與使用者介面評估的對話式推薦系統

---

## Project Overview | 專案簡介

### English

This project demonstrates how to turn a traditional drink recommendation feature into a reliability-aware LLM conversational recommender system by connecting preference extraction, multi-turn dialogue, semantic retrieval, reranking, endpoint testing, UI evaluation, and failure analysis.


**Boba Buddy** is a Taiwanese bubble tea discovery app designed to help users explore nearby drink shops, browse drink information, view store menus and reviews, and discover suitable beverages more easily. Its original recommendation logic was closer to a traditional **item-based recommendation system**, where the system directly returned recommended drinks based on stored item relationships or similarity signals.

The **Digital Waiter** feature explores a different interaction model. Instead of requiring users to search through long drink lists, it allows them to describe their needs in natural language, as if they were talking to a friend or a store staff member. Example user requests include:

- “I want something refreshing.”
- “No milk.”
- “Something energizing, but not coffee.”
- “Something suitable for a rainy day.”
- “I want a drink, but I do not know what to order.”

This project reframes Digital Waiter from a simple chatbot feature into a **Conversational Recommender System (CRS)**. Its goal is not only to generate friendly replies, but also to support a complete recommendation workflow: gathering user preferences through multi-turn dialogue, interpreting vague needs, maintaining conversation state, retrieving candidate drinks through backend APIs and database queries, reranking candidates, and generating concise responses that respect user constraints.

From an AI application engineering perspective, this project focuses on a practical reliability question:

> How can a conversational drink recommendation feature remain useful when user preferences are incomplete, ambiguous, changing across turns, or constrained by requirements such as no milk, no coffee, budget, or nearby availability?

### 中文

這個專案展示如何將傳統飲料推薦功能，升級成一套具可靠性意識的 LLM 對話式推薦系統，並串接偏好抽取、多輪對話、語意檢索、重新排序、endpoint 測試、UI 評估與失敗模式分析。

**Boba Buddy** 是一款以台灣手搖飲為主題的飲品探索應用程式，目標是協助使用者搜尋附近飲料店、瀏覽飲品資訊、查看店家菜單與評價，並更容易找到適合自己的飲料。原始推薦邏輯較接近傳統的**品項式推薦系統（item-based recommendation system）**，也就是根據飲品之間既有的關聯或相似程度，直接回傳推薦品項。

**Digital Waiter** 功能則探索不同的互動方式：與其要求使用者自行瀏覽大量飲品清單，不如讓使用者像與朋友或店員對話一樣，以自然語言描述自己的需求。例如：

- 「今天想喝清爽一點的。」
- 「不要奶。」
- 「想提神，但不要咖啡。」
- 「想喝適合下雨天的飲料。」
- 「我想喝飲料，但不知道要點什麼。」

本專案將 Digital Waiter 從單純的聊天功能，重新定位為一套**對話式推薦系統（Conversational Recommender System, CRS）**。它的目標不只是生成友善的文字回覆，而是支援一套完整的推薦流程：透過多輪對話蒐集使用者偏好、理解模糊需求、維護對話狀態、經由後端應用程式介面（Application Programming Interface, API）與資料庫查詢候選飲品、重新排序候選結果，並生成簡潔且符合使用者限制條件的回覆。

從人工智慧應用工程的角度來看，本專案關注的實務可靠性問題是：

> 當使用者偏好資訊不足、需求語意模糊、對話中途改變條件，或提出不要奶、不要咖啡、預算與附近可取得性等限制時，對話式飲料推薦功能要如何仍然提供可靠且有用的建議？

---

## My Contributions | 我負責的內容

### English

My work focused on analyzing, testing, and restructuring the Digital Waiter feature from the perspective of an end-to-end AI application workflow.

Specifically, I contributed to the following areas:

- Reviewed and organized the existing **FastAPI / OpenAI / Supabase** recommendation pipeline to understand how user input, semantic retrieval, candidate selection, and generated responses were connected.
- Read the original Digital Waiter code structure and translated the existing implementation into system architecture and workflow documentation.
- Conducted endpoint-level testing for the recommendation API, including request-schema validation, radius-related behavior, query sensitivity, and raw response inspection.
- Designed UI-level conversational test cases covering preference gathering, constraint following, vague requests, multi-turn memory, change-of-mind handling, and fallback behavior.
- Compared UI symptoms with backend endpoint outputs to distinguish possible frontend issues from backend retrieval, ranking, state-management, or response-generation issues.
- Identified failure modes such as constraint violations, missing conversation state, semantic mismatch, location-filter uncertainty, and ungrounded language-model responses.
- Proposed a more reliable layered architecture that separates preference extraction, conversation-state updates, hard-constraint filtering, semantic candidate retrieval, reranking, grounded response generation, and reliability evaluation.
- Reconstructed portfolio-safe demonstration modules and examples using anonymized or mock content rather than exposing production assets.

Through this project, I developed a stronger understanding of how to evaluate and improve an AI application beyond model output quality alone, especially when recommendations must remain interpretable, testable, and robust under uncertain or changing user requirements.

### 中文

我在此專案中的工作重點，是從**端到端人工智慧應用流程**的角度，分析、測試並重新整理 Digital Waiter 功能。

我負責的內容包括：

- 閱讀並整理既有的 **FastAPI / OpenAI / Supabase** 推薦處理管線（recommendation pipeline），理解使用者輸入、語意檢索、候選飲品選取與最終文字回覆之間的串接方式。
- 閱讀 Digital Waiter 原始程式架構，並將既有實作內容整理為系統架構與工作流程文件。
- 執行推薦應用程式介面（API）的端點測試（endpoint testing），包含請求格式確認、搜尋距離設定行為、不同查詢文字是否影響結果，以及原始回傳內容檢查。
- 設計使用者介面（User Interface, UI）層級的對話測試案例，涵蓋偏好蒐集、限制條件遵守、模糊需求理解、多輪對話記憶、使用者改變心意後的條件更新，以及無合適結果時的替代回應。
- 對照使用者介面中觀察到的問題與後端端點回傳結果，以區分問題可能來自前端呈現、後端檢索、排序邏輯、對話狀態管理，或回覆生成流程。
- 整理主要失敗模式，例如違反使用者限制條件、遺失多輪對話狀態、語意配對不準確、距離篩選行為不明確，以及大型語言模型（Large Language Model, LLM）生成未由候選飲品資訊支持的回覆。
- 提出較具可靠性的分層式系統架構，將偏好擷取、對話狀態更新、必要限制條件篩選、語意候選檢索、候選重新排序、具依據的回覆生成，以及可靠性評估分開處理。
- 以匿名化或模擬內容重新建構適合作品集展示的示範模組與範例，避免公開正式上線系統中的資產或敏感內容。

透過此專案，我進一步建立了評估與改善人工智慧應用的實務能力：不只關注模型或大型語言模型能否生成結果，也關注推薦結果是否可解釋、可測試、可追蹤問題來源，並能在使用者需求不明確或持續變動的情境下維持可靠性。



## Scope of Implementation and Proposed Improvements | 實作範圍與改善提案說明

My hands-on work focused on understanding the existing Digital Waiter workflow, reviewing code structure, conducting UI and endpoint tests, and discussing improvement directions. The layered preference extraction, retrieval, reranking, and reliability-evaluation modules in this repository are portfolio reconstructions and proposed improvement patterns, created to demonstrate how the observed issues could be diagnosed and addressed in a more testable AI application architecture.

我實際參與的工作主要聚焦於理解既有 Digital Waiter 流程、閱讀程式架構、執行使用者介面與後端端點測試，以及討論改善方向。本儲存庫中分層設計的偏好擷取、候選檢索、重新排序與可靠性評估模組，屬於作品集重建內容與改善設計提案，用於呈現如何以更可測試的人工智慧應用架構診斷並處理觀察到的問題。


---

## Portfolio Reconstruction and Disclosure | 作品集重建與公開內容說明

### English

This repository is a **portfolio reconstruction** of the Digital Waiter project. It does not expose production source code, private API keys, identifiable user data, or proprietary database content. Instead, it presents the system architecture, testing strategy, failure analysis, and reliability-aware design approach behind the feature through documentation, anonymized examples, and mock implementations.

### 中文

本程式碼儲存庫（repository）是針對 Digital Waiter 專案所整理的**作品集重建版本（portfolio reconstruction）**。本儲存庫不公開正式上線系統原始碼、私人應用程式介面金鑰、可識別使用者資料或專有資料庫內容，而是透過文件、匿名化範例與模擬實作，展示此功能背後的系統架構、測試策略、失敗分析，以及可靠性導向的設計思維。
---

## Problem Framing | 問題定義

### English

Traditional recommendation systems often assume that user preferences are already available or can be inferred from past item interactions. However, in a drink-ordering scenario, users often begin with vague, incomplete, or situational preferences.

A user may not know the exact drink name, but may express a goal, mood, constraint, or context:

- taste: refreshing, creamy, roasted, fruity
- constraints: no milk, no coffee, not too sweet, under a budget
- situation: rainy day, after a meal, needs energy, wants comfort
- uncertainty: “I do not know what I want yet.”

This makes the task different from simple item retrieval. The system needs to behave like a digital waiter: ask useful follow-up questions, remember previous preferences, update the internal state when the user changes their mind, retrieve relevant drinks, and recommend only items that satisfy explicit constraints.

### 中文

傳統推薦系統通常假設使用者偏好已經存在，或可以從歷史互動中推論出來。但在點飲料的情境中，使用者一開始常常只有模糊、不完整、甚至情境式的需求。

使用者可能不知道具體飲料名稱，而是用目標、心情、限制或場景來描述：

- 口味：清爽、濃郁、焙茶感、水果感
- 限制：不要奶、不要咖啡、不要太甜、預算內
- 情境：下雨天、飯後、想提神、想被安慰
- 不確定：「我也不知道想喝什麼。」

因此，這個任務不只是單純搜尋品項，而是需要像數位店員一樣：提出有用的追問、記住前面偏好、在使用者改口時更新內部狀態、檢索合適飲品，並只推薦符合明確限制條件的品項。

---

## System Architecture Overview | 系統架構總覽

### High-Level Workflow | 整體運作流程概覽

```text
User Chat
→ Frontend UI
→ FastAPI Endpoint
→ Language Detection / Translation
→ Conversation History Retrieval
→ Intent Detection
→ Preference State / Composite Query Update
→ Embedding Query Generation
→ Supabase RPC Candidate Retrieval
→ GPT-based Reranking
→ Natural Language Recommendation
→ Save Chat Metadata
→ Return Response to UI
```

### Main Components | 主要模組

| Component | English Description | 中文說明 |
|---|---|---|
| Frontend UI | User-facing chat interface for drink discovery | 使用者輸入飲料需求的聊天介面 |
| FastAPI Endpoint | Backend API entry point for recommendation requests | 後端推薦請求入口 |
| Language Processing | Detects user language and translates inputs when needed | 偵測語言，必要時轉成英文處理 |
| Conversation History | Retrieves previous turns to support multi-turn dialogue | 讀取過去對話，支援多輪互動 |
| Intent Detection | Classifies whether the user is chatting, refining preferences, asking for recommendations, clearing history, or asking unrelated questions | 判斷使用者目前是在聊天、補充偏好、要求推薦、清除紀錄或提出無關問題 |
| Composite Query | Accumulates user preferences across turns | 累積多輪對話中的使用者偏好 |
| Embedding Retrieval | Converts preference summary into vector representation and retrieves candidate drinks | 將偏好摘要轉成向量並檢索候選飲品 |
| Supabase RPC | Queries nearby stores and similar drinks | 查詢附近店家與相似飲品 |
| LLM Reranking | Uses LLM to rerank retrieved drinks and generate short recommendation reasons | 使用 LLM 重新排序候選飲品並生成推薦理由 |
| Metadata Logging | Saves composite query and shown drink IDs for memory and duplicate avoidance | 儲存偏好狀態與已推薦品項，避免重複推薦 |

---

## Conversational Recommendation Design | 對話式推薦設計

### English

A general chatbot can generate fluent responses, but a conversational recommender system must support **task-oriented decision-making**. For Digital Waiter, this means the system should be evaluated by whether it can:

1. Understand user preferences.
2. Ask useful follow-up questions.
3. Respect hard constraints such as “no milk” or “under 60 NTD.”
4. Maintain natural and coherent conversation flow.
5. Remember earlier context across multiple turns.
6. Update preferences correctly when the user changes their mind.
7. Handle vague or abstract requests without hallucinating unsupported recommendations.

### 中文

一般 chatbot 可以生成流暢回答，但對話式推薦系統必須支援 **任務導向的決策輔助**。對 Digital Waiter 來說，系統不能只看起來會聊天，而是要被以下能力評估：

1. 是否理解使用者偏好。
2. 是否會追問關鍵資訊。
3. 是否遵守「不要奶」、「60 元內」等硬限制。
4. 聊天是否自然且連貫。
5. 多輪對話後是否記得前文。
6. 使用者改口時是否能正確更新偏好。
7. 面對模糊或抽象需求時，是否能先澄清，而不是直接幻想式推薦。

---

## Testing Strategy | 測試策略

This project organizes testing from two complementary perspectives:

```text
UI Testing
→ Observe user-facing symptoms

Endpoint Testing
→ Inspect backend recommendation behavior
```

### UI Testing | UI 測試

UI testing focuses on whether the chat experience feels useful, coherent, and recommendation-oriented.

Test categories include:

```text
1. Preference gathering
2. Clarifying questions
3. Constraint following
4. Multi-turn memory
5. Preference update after user correction
6. Vague request handling
7. Fallback behavior when no valid recommendation exists
```

### Endpoint Testing | Endpoint 測試

Endpoint testing focuses on whether the backend pipeline behaves as expected independently of the frontend.

Test dimensions include:

```text
1. Endpoint availability
2. Request schema validation
3. Language detection and translation
4. Intent classification
5. Composite query update
6. Candidate retrieval
7. Radius / location behavior
8. Reranking output
9. JSON response structure
10. Error and fallback messages
```

The key reason for testing the endpoint directly is to separate **frontend symptoms** from **backend causes**. If the UI shows an irrelevant recommendation, the issue may come from preference extraction, state update, candidate retrieval, reranking, or final response generation. Direct API testing makes this easier to debug.

---

## Failure Modes & Reliability Concerns | 失敗模式與可靠性問題

This project treats Digital Waiter as a reliability-aware AI application, not just a prompt demo. The main risks include:

| Failure Mode | Description | Risk |
|---|---|---|
| Early Recommendation | The system recommends before collecting enough preference information | User receives irrelevant drinks |
| Missing Clarification | The system does not ask follow-up questions for vague requests | System guesses instead of supporting decision-making |
| Constraint Violation | The system recommends items that violate hard constraints | Loss of user trust |
| State Update Failure | The system forgets or incorrectly merges previous preferences | Multi-turn dialogue becomes inconsistent |
| Preference Overwrite Failure | User changes their mind, but the system keeps old preferences | Wrong recommendations |
| Embedding Drift | Semantic retrieval returns similar-sounding but unsuitable drinks | Fluent but irrelevant output |
| Reranking Hallucination | LLM gives convincing reasons not grounded in drink metadata | Misleading recommendation |
| UI / Endpoint Mismatch | UI behavior does not match backend output | Debugging becomes difficult |
| Overlong Recommendation List | The system returns too many options instead of reducing decision burden | Poor user experience |

---

## Proposed Reliability-Aware Recommendation Pipeline | 可靠性導向推薦流程

The improved architecture separates the recommendation process into layers:

```text
Conversation History
→ Preference Extraction
→ Structured Preference State
   ├── Hard Constraints
   ├── Soft Preferences
   └── Situational / Emotional Intent
→ Hard Constraint Filtering
→ Semantic Retrieval
→ Candidate Reranking
→ Grounded Natural Language Response
→ Reliability Check
```

### Key Design Principle | 核心設計原則

> The LLM should not be responsible for everything. It should help interpret language and generate responses, but hard constraints, candidate filtering, state tracking, and reliability checks should be handled explicitly by the system.

> LLM 不應該負責所有事情。它可以協助理解語言與生成回覆，但硬限制過濾、候選品項篩選、狀態追蹤與可靠性檢查，應該由系統明確處理。

---

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

---

## Repository Guide | 檔案說明

| Path | Purpose |
|---|---|
| `docs/system_architecture.md` | Documents the FastAPI / OpenAI / Supabase architecture and data flow |
| `docs/llm_workflow_notes.md` | Summarizes LLM workflow concepts such as chatbot, RAG, stack, pipeline, and workflow |
| `docs/recommendation_pipeline.md` | Explains the conversational recommendation pipeline from preference extraction to reranking |
| `docs/api_testing_plan.md` | Defines endpoint-level testing strategy and request examples |
| `docs/ui_testing_plan.md` | Defines user-facing CRS testing categories and conversation scenarios |
| `docs/failure_analysis.md` | Organizes observed and expected failure modes |
| `docs/recommendation_risk_policy.md` | Defines reliability criteria and fallback rules for recommendations |
| `examples/endpoint_request_examples.md` | Provides anonymized API request examples |
| `examples/conversation_test_cases.md` | Provides multi-turn conversation test cases |
| `examples/sample_prompts.md` | Provides prompt examples for testing intent detection, preference extraction, and reranking |
| `examples/sample_outputs.json` | Provides mock endpoint outputs |
| `src/preference_extraction/` | Contains simplified code for intent detection, preference summarization, and constraint parsing |
| `src/retrieval_and_ranking/` | Contains simplified code for query building, candidate retrieval, and reranking |
| `src/evaluation/` | Contains simplified code for constraint checking, UI/API comparison, and recommendation reliability scoring |
| `reports/` | Contains analysis reports and product iteration notes |
| `demo/` | Contains screenshots and demo video link placeholder |

---

## Example Use Cases | 範例使用情境

### Case 1: Vague Preference | 模糊需求

```text
User: I want something refreshing.
Expected behavior:
- Do not recommend immediately.
- Ask a clarifying question, such as tea-based or fruit-based.
- Update preference state with "refreshing."
```

### Case 2: Hard Constraints | 明確限制

```text
User: I want something not too sweet, no milk, and under 60 NTD.
Expected behavior:
- Extract hard constraints.
- Filter out milk-based drinks.
- Filter out items above budget when price metadata is available.
- Recommend only candidates that satisfy constraints.
```

### Case 3: Multi-Turn Preference Update | 多輪改口

```text
User: I do not want milk.
Assistant: Got it.
User: Actually, a little milk is okay.
Expected behavior:
- Update dairy preference from "no milk" to "little milk."
- Do not keep contradictory states.
```

### Case 4: Recommendation Readiness | 是否準備推薦

```text
User: I feel tired today.
Expected behavior:
- Interpret the goal as "energizing."
- Ask whether caffeine or tea is acceptable.
- Recommend only after enough preference information is collected or the user explicitly asks for recommendations.
```

---

## Confidentiality & Ethical Note | 保密與倫理聲明

This repository is intended for portfolio demonstration only.

It does **not** include:

```text
- Production source code
- Private API keys
- Real user IDs
- User chat logs
- Proprietary database content
- Internal credentials
- Non-public business data
```

All examples in this repository are reconstructed, anonymized, simplified, or mocked for educational and portfolio purposes.


本程式碼儲存庫（repository）僅供作品集展示用途。

本儲存庫 **不包含**：


```text
- 正式上線系統的原始碼
- 私人應用程式介面金鑰（API keys）
- 真實使用者識別碼（user IDs）
- 使用者聊天紀錄
- 專有資料庫內容
- 內部存取憑證
- 非公開商業資料
```

本儲存庫中的所有範例，皆為基於作品集展示目的所重新建構、匿名化、簡化或模擬產生的內容。

---

## Reusable Design Patterns and Practical Capabilities | 可延伸應用的設計模式與實作能力

This repository organizes the Digital Waiter project into reusable design patterns for building and evaluating conversational AI applications. These patterns are especially relevant when user requirements are incomplete, ambiguous, changing across turns, or constrained by practical conditions such as dietary preferences, distance, and recommendation reliability.

本程式碼儲存庫（repository）將 Digital Waiter 專案整理為可延伸應用於對話式人工智慧系統的設計模式與實作方法，特別適合參考於使用者需求資訊不足、語意模糊、在多輪互動中持續改變，或受到飲食偏好、距離與推薦可靠性等實務條件限制的應用情境。

### Conversational AI Application Architecture | 對話式人工智慧應用架構

- **From item-based recommendation to conversational recommendation**  
  A practical design transition from directly returning similar drink items to supporting preference discovery through natural-language interaction.  
  從直接回傳相似飲品的品項式推薦方式，延伸為透過自然語言互動協助使用者探索偏好的對話式推薦設計。

- **End-to-end recommendation workflow decomposition**  
  A system-level view of how user chat, backend requests, conversation history, intent detection, preference updates, candidate retrieval, reranking, and response generation connect together.  
  從系統角度拆解使用者對話、後端請求、歷史對話讀取、意圖判斷、偏好更新、候選飲品檢索、重新排序與回覆生成之間的端到端串接流程。

- **Layered architecture for maintainable AI applications**  
  A modular design pattern that separates language understanding, recommendation logic, testing, and reliability evaluation rather than relying on one large prompt.  
  將語言理解、推薦邏輯、測試與可靠性評估分層處理的模組化設計模式，避免將所有功能依賴於單一大型提示指令。

### Preference Understanding and Recommendation Logic | 偏好理解與推薦邏輯

- **Preference extraction from natural-language requests**  
  A reusable approach for converting requests such as “refreshing,” “no milk,” or “energizing but not coffee” into structured recommendation conditions.  
  將「清爽」、「不要奶」或「想提神但不要咖啡」等自然語言需求，轉換為結構化推薦條件的可重用方法。

- **Multi-turn conversation state management**  
  A design pattern for preserving previous preferences and correctly updating them when users add conditions or change their minds.  
  保留先前偏好，並在使用者補充條件或改變心意時正確更新狀態的多輪對話管理方式。

- **Constraint-aware recommendation design**  
  A safer recommendation pattern that treats requirements such as no milk, no coffee, budget, or nearby availability as executable constraints rather than optional wording in a generated reply.  
  將不要奶、不要咖啡、預算與附近可取得性等需求視為可實際執行的篩選條件，而非僅出現在生成回覆文字中的安全推薦設計。

- **Semantic retrieval and candidate reranking**  
  A workflow that uses semantic meaning to retrieve candidate drinks, then reranks them according to structured preferences, constraints, and available metadata.  
  先依語意內容檢索候選飲品，再根據結構化偏好、限制條件與可取得的飲品資訊重新排序的推薦流程。

### Testing and Evaluation Workflow | 測試與評估流程

- **Application programming interface endpoint testing**  
  A reproducible testing method for checking request structure, distance-related behavior, query sensitivity, and raw backend responses.  
  用於檢查請求格式、搜尋距離設定行為、查詢文字是否影響結果，以及後端原始回傳內容的可重複應用程式介面端點測試方法。

- **User interface and conversational behavior evaluation**  
  A test-case design approach for evaluating preference gathering, clarification quality, multi-turn memory, change-of-mind handling, and fallback behavior.  
  用於評估偏好蒐集、追問品質、多輪對話記憶、改口後的條件更新，以及無合適結果時替代回應的使用者介面與對話行為測試方式。

- **UI-to-endpoint comparison for debugging**  
  A diagnosis workflow that compares user-facing symptoms with backend outputs to distinguish frontend display issues from retrieval, ranking, state-management, or response-generation failures.  
  將使用者介面中觀察到的問題與後端端點輸出進行對照，以區分問題可能來自前端顯示、候選檢索、排序邏輯、狀態管理或回覆生成的除錯流程。

### Reliability-Aware AI Application Design | 可靠性導向的人工智慧應用設計

- **Failure-mode analysis for conversational recommendations**  
  A structured way to identify risks such as constraint violations, lost conversation state, irrelevant candidates, unsupported response claims, or inconsistent frontend and backend results.  
  以結構化方式辨識違反限制條件、遺失對話狀態、候選結果不相關、回覆理由缺乏依據，以及前後端結果不一致等推薦風險。

- **Grounded response generation**  
  A design principle that limits generated explanations to verified candidate drinks and available metadata rather than allowing unsupported recommendations.  
  將生成式回覆限制在已確認的候選飲品與可取得資訊之上，避免產生缺乏依據之推薦內容的設計原則。

- **Recommendation reliability assessment**  
  A proposed evaluation approach that considers constraint satisfaction, semantic relevance, location validity, conversation-state consistency, and response grounding before presenting a recommendation confidently.  
  在自信呈現推薦結果前，綜合考量限制條件符合程度、語意相關性、距離有效性、對話狀態一致性與回覆依據完整性的推薦可靠性評估方式。

### Product-Oriented AI Engineering Communication | 產品導向的人工智慧工程溝通

- **Turning observed user experience issues into engineering questions**  
  A practical method for translating problems such as “recommendations feel wrong” or “the chatbot forgets preferences” into testable backend and system-design hypotheses.  
  將「推薦感覺不準」或「聊天功能忘記偏好」等使用體驗問題，轉換為可測試的後端與系統設計假設之實務方法。

- **Documenting reconstructed work responsibly**  
  A portfolio practice that clearly distinguishes analyzed workflows, proposed improvements, mock implementations, and non-public production assets.  
  清楚區分已分析的工作流程、提出的改善設計、模擬實作內容，以及不公開之正式上線系統資產的負責任作品集呈現方式。

---
