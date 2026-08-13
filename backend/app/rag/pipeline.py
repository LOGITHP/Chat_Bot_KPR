import asyncio
from typing import Dict, Any, Optional
from app.rag.retrieval import retrieve_context
from app.rag.memory import get_conversation_context, add_message_to_conversation
from app.llm.ollama_client import ollama_client

async def generate_rag_response(
    question: str,
    conversation_id: str,
    user_profile: dict,
    is_guest: bool = False,
    requested_scope: Optional[dict] = None
) -> Dict[str, Any]:
    # 1. Retrieve context (blocking call — run in threadpool to avoid blocking event loop)
    context_matches = await asyncio.to_thread(
        retrieve_context, question, user_profile, is_guest, requested_scope
    )
    
    # Format context
    context_str = ""
    sources = []
    if not context_matches:
        context_str = "No relevant context found in uploaded documents."
    else:
        context_str_list = []
        for idx, match in enumerate(context_matches):
            payload = match["payload"]
            filename = payload.get("filename", "Unknown File")
            text = payload.get("chunk_text", "")
            
            source_info = f"[File: {filename}"
            if payload.get("page"):
                source_info += f", Page: {payload['page']}"
            if payload.get("sheet"):
                source_info += f", Sheet: {payload['sheet']}"
            if payload.get("row"):
                source_info += f", Row: {payload['row']}"
            if payload.get("section"):
                source_info += f", Section: {payload['section']}"
            source_info += "]"
            
            context_str_list.append(f"Document {idx + 1} {source_info}:\n{text}")
            sources.append(payload)
            
        context_str = "\n\n".join(context_str_list)

    # 2. Get Memory Context
    recent_messages, summary = await get_conversation_context(conversation_id, is_guest)

    # 3. Build Prompt
    system_prompt = (
        "You are the Campus AI Assistant. "
        "Answer the user's question using ONLY the supplied campus context below. "
        "Rules:\n"
        "1. Use only information present in the CAMPUS CONTEXT.\n"
        "2. If the answer is not in the context, clearly state: 'The available campus documents do not contain enough information to answer this question.'\n"
        "3. Do NOT invent policies, dates, names, routes, fees, rules, or other facts.\n"
        "4. Prefer the most recent authoritative document if multiple sources conflict.\n"
        "5. Provide source references whenever possible.\n"
        "6. Be concise but complete."
    )

    # Profile info
    role = user_profile.get("role", "guest")
    dept = user_profile.get("department_id", "None")
    year = user_profile.get("year", "None")
    
    user_prompt = f"USER CONTEXT:\nRole: {role}\nDepartment: {dept}\nYear: {year}\n\n"
    if summary:
        user_prompt += f"CONVERSATION SUMMARY:\n{summary}\n\n"
    
    user_prompt += (
        f"CAMPUS CONTEXT:\n"
        f"---------------------\n"
        f"{context_str}\n"
        f"---------------------\n"
        f"USER QUESTION: {question}\n\n"
        f"Answer:"
    )

    messages = [{"role": "system", "content": system_prompt}]
    
    # Add recent messages
    for msg in recent_messages:
        messages.append(msg)
        
    messages.append({"role": "user", "content": user_prompt})

    # 4. Generate Response
    answer = await ollama_client.generate_chat_completion(messages)

    # 5. Store conversation
    await add_message_to_conversation(conversation_id, "user", question, is_guest=is_guest)
    await add_message_to_conversation(conversation_id, "assistant", answer, sources=sources, is_guest=is_guest)

    return {
        "answer": answer,
        "sources": sources
    }
