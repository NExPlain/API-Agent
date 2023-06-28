---

# API-Agent: Decouple Your Work into APIs

API-Agent is an open-source application enabling users to converts their work into a sequence of executable API calls. The API-Agent solves the problems of transforming natural language into API calls and executing the APIs for user, it can be done either through chatting with a AI-agent, or enabling the agent to self-prompt solutions for emails or notifications.

<h2 align="center"> Demo 07 11st 2023 </h2>

https://github.com/NExPlain/API-Agent/assets/4609844/021ad24c-5c60-4782-aa34-c4e75986fdb3

Demo made by <a href=https://twitter.com/zhenthebuilder>Zhen Li</a>

## 🚀 Features

- 🧠 Capability to convert natural language into executable API calls
- 🔌 Integrations with Google Calendar and Gmail
- 🔗 Self-prompting email reply actions


## Quickstart

0. Get an OpenAI [API Key](https://platform.openai.com/account/api-keys), and add it in .env file.
1. Download the latest repo
  ```git clone https://github.com/NExPlain/API-Agent && cd API-Agent```
1. Install the requirements 
  ```pip install -r requirements.txt```
1. Start the local demo
   ```chainlit run api_gpt/prompts/explore_api_demo.py -w```




## 🌐 Live demo
- www.debrief-ai.com
  - Self-prompting email reply actions
- www.plasma-ai.com 
  - API Agent demo
  - This demo is using a outdated version of this repo

## ⚠️ Limitations

This project comes with some limitations:

1. May not provide accurate API to execute in some scenarios, the capability is capped by GPT.
2. The integration only supports Gmail and Google Calendar at this point.

## 👀 What I'm looking for

I open source this project to attract more people believes in the productivity from combining LLM + API. Chatgpt plugins are great, but the world need more adventurers.
If you are intereted in this project, here are some items on the roadmap:
1. **Improve the demo experience**. We polished the experience on launched product, but for demo experience we need more user feedback and contributions.
2. **Expand use cases to more APIs**. github and slack will be a great starting point.
3. **Auto API integrations**
   - Integrating more APIs is the bottleneck for expanding the capability for this project.
   - GPT-4 can generate code that connects Debrief-AI easily, you can check out [this demo video](https://www.youtube.com/watch?v=HxfFAnldcRg&t=81s).
