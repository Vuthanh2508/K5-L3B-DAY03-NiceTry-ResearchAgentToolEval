"""Streamlit Web UI for Research Agent (Checkpoint 5).

Allows interactive chat with live tool call observation, transcript logging,
and quick execution of rubric test cases.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

# Ensure starter_v0 directory is on sys.path
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from env_loader import load_lab_env
from providers import make_provider
from providers.base import ToolCall
from tools import TOOL_FUNCTIONS, load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version
from chat import (
    execute_tool_call,
    json_text,
    now_iso,
    safe_slug,
    trim_history,
    write_transcript,
    assistant_tool_message,
    tool_results_message,
)

# Load environment variables from starter_v0/.env
load_lab_env(ROOT)
ARTIFACTS_DIR = ROOT / "artifacts"
TRANSCRIPTS_DIR = ROOT / "transcripts"

TOOL_ICONS: dict[str, str] = {
    "clarify": "❓",
    "lookup": "🌐",
    "timeline": "🐦",
    "social_search": "💬",
    "fetch": "📄",
    "format": "📰",
    "send": "📤",
    "policy": "📜",
    "papers": "📚",
    "paper_text": "📖",
    "weather": "🌤️",
    "redact": "🔒",
}


def run_model_tool_loop_ui(
    *,
    provider: Any,
    messages: list[dict[str, str]],
    tools: list[dict[str, Any]],
    model: str | None,
    max_tool_rounds: int,
    status_container: Any | None = None,
) -> dict[str, Any]:
    """Execute the multi-round tool loop with real-time UI status updates."""
    working_messages = list(messages)
    rounds: list[dict[str, Any]] = []
    all_tool_events: list[dict[str, Any]] = []

    for round_index in range(1, max_tool_rounds + 1):
        if status_container:
            status_container.write(f"🤖 **Round {round_index}:** Đang gửi ngữ cảnh tới LLM ({model or 'default'})...")

        response = provider.complete(working_messages, tools, model=model, temperature=0.0)
        calls = response.tool_calls
        round_record: dict[str, Any] = {
            "round": round_index,
            "assistant_text": response.text,
            "tool_calls": [{"name": call.name, "args": call.args} for call in calls],
            "tool_results": [],
        }

        if not calls:
            rounds.append(round_record)
            if status_container:
                status_container.write("✅ Model phản hồi trực tiếp (không cần thêm công cụ).")
            return {
                "status": "answered",
                "assistant_text": response.text or "",
                "rounds": rounds,
                "tool_events": all_tool_events,
            }

        working_messages.append(assistant_tool_message(response.text, calls))
        non_clarification_events: list[dict[str, Any]] = []

        for call in calls:
            icon = TOOL_ICONS.get(call.name, "🔧")
            args_summary = json.dumps(call.args, ensure_ascii=False)
            if len(args_summary) > 60:
                args_summary = args_summary[:57] + "..."
            if status_container:
                status_container.write(f"{icon} Thực thi `{call.name}({args_summary})`...")

            event = execute_tool_call(call)
            round_record["tool_results"].append(event)
            all_tool_events.append(event)

            # Check for clarification / user pause tool (by output awaiting_user)
            result = event.get("result", {})
            if isinstance(result, dict) and result.get("awaiting_user"):
                question = result.get("question") or call.args.get("question") or "Bạn bổ sung thêm thông tin nhé."
                rounds.append(round_record)
                if status_container:
                    status_container.write(f"⏸️ Tool `{call.name}` yêu cầu tạm dừng để hỏi lại người dùng.")
                return {
                    "status": "waiting_for_user",
                    "assistant_text": question,
                    "clarify_meta": {
                        "question": question,
                        "response_type": result.get("response_type", "text"),
                        "options": result.get("options", []),
                    },
                    "rounds": rounds,
                    "tool_events": all_tool_events,
                }

            non_clarification_events.append(event)

        rounds.append(round_record)
        working_messages.append(tool_results_message(non_clarification_events))

    if status_container:
        status_container.write(f"⚠️ Đã đạt giới hạn tối đa {max_tool_rounds} rounds công cụ.")

    return {
        "status": "max_tool_rounds",
        "assistant_text": f"Đã dừng sau {max_tool_rounds} vòng gọi công cụ. Kiểm tra transcript để biết chi tiết.",
        "rounds": rounds,
        "tool_events": all_tool_events,
    }


def init_session(provider_name: str, model_name: str | None, version_label: str) -> None:
    """Initialize a brand-new chat session and transcript."""
    sys_prompt_path = ARTIFACTS_DIR / "system_prompt.md"
    tools_path = ARTIFACTS_DIR / "tools.yaml"

    artifact_version = build_artifact_version(version_label, sys_prompt_path, tools_path)
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    transcript_id = "_".join([
        safe_slug(version_label),
        safe_slug(provider_name),
        timestamp,
    ])

    TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
    transcript_path = TRANSCRIPTS_DIR / f"{transcript_id}.transcript.json"
    transcript: dict[str, Any] = {
        "transcript_id": transcript_id,
        **artifact_version_dict(artifact_version),
        "provider": provider_name,
        "model": model_name,
        "system_prompt": str(sys_prompt_path),
        "tools": str(tools_path),
        "history_window": 5,
        "max_tool_rounds": 4,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }

    st.session_state.transcript_id = transcript_id
    st.session_state.transcript_path = transcript_path
    st.session_state.transcript = transcript
    st.session_state.messages = []
    st.session_state.history = []
    st.session_state.turn_index = 0
    st.session_state.last_clarify = None
    st.session_state.pending_prompt = None


def render_tool_events(events: list[dict[str, Any]], rounds: list[dict[str, Any]]) -> None:
    """Render tool executions clearly in an expander without hiding errors or args."""
    if not events and not rounds:
        return

    with st.expander(f"🛠️ **Chi tiết công cụ đã gọi ({len(events)} lượt tool call)**", expanded=False):
        for r in rounds:
            st.markdown(f"**Vòng (Round) {r.get('round', 1)}**")
            calls = r.get("tool_calls", [])
            results = r.get("tool_results", [])
            for idx, call in enumerate(calls):
                tool_name = call.get("name", "unknown")
                icon = TOOL_ICONS.get(tool_name, "🔧")
                args = call.get("args", {})
                res = results[idx].get("result") if idx < len(results) else None

                st.markdown(f"##### {icon} `{tool_name}`")
                c1, c2 = st.columns(2)
                with c1:
                    st.caption("📥 Tham số gửi vào (Arguments):")
                    st.json(args)
                with c2:
                    st.caption("📤 Kết quả trả về (Result):")
                    if isinstance(res, dict) and "error" in res:
                        st.error(f"Error: {res.get('error')} - {res.get('message', '')}")
                    st.json(res)
                st.divider()


def main() -> None:
    st.set_page_config(
        page_title="Research Agent UI | Checkpoint 5",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Sidebar Header
    st.sidebar.title("⚙️ Cấu hình Agent")

    # Provider selection
    available_providers = ["openrouter", "openai", "gemini", "anthropic", "ollama"]
    provider_name = st.sidebar.selectbox("Model Provider:", available_providers, index=0)

    # Model input
    default_model_map = {
        "openrouter": "openai/gpt-4o-mini",
        "openai": "gpt-4o-mini",
        "gemini": "gemini-2.5-flash",
        "anthropic": "claude-3-5-haiku-20241022",
        "ollama": "qwen2.5:7b",
    }
    model_name = st.sidebar.text_input("Tên Model:", value=default_model_map.get(provider_name, ""))
    version_label = st.sidebar.text_input("Artifact Version:", value="v4")

    col_w, col_r = st.sidebar.columns(2)
    with col_w:
        history_window = int(st.sidebar.number_input("History Window:", min_value=1, max_value=20, value=5))
    with col_r:
        max_tool_rounds = int(st.sidebar.number_input("Max Rounds:", min_value=1, max_value=10, value=4))

    # Initialize session
    if "transcript_id" not in st.session_state:
        init_session(provider_name, model_name or None, version_label)

    # Reset button
    if st.sidebar.button("🔄 Bắt đầu phiên chat mới", use_container_width=True):
        init_session(provider_name, model_name or None, version_label)
        st.rerun()

    # Sidebar: Sample test cases (CP5 Rubric C6)
    st.sidebar.markdown("---")
    st.sidebar.subheader("🎯 Câu hỏi mẫu thử nghiệm (CP5)")
    st.sidebar.caption("Nhấp vào nút để tự động nạp yêu cầu vào chat:")

    samples = [
        ("1. 🔍 Yêu cầu thường (Research)", "Tìm kiếm các tin tức AI mới nhất trong tuần qua về OpenAI và DeepSeek."),
        ("2. ❓ Thiếu thông tin (Missing Info)", "Hãy lấy các bài đăng gần đây của tài khoản này."),
        ("3. 👤 Bổ sung thông tin", "Tài khoản @sama nhé."),
        ("4. 📤 Yêu cầu gửi Telegram (Guardrail)", "Gửi bản tin tóm tắt vừa rồi lên Telegram."),
        ("5. ✅ Xác nhận gửi Telegram", "Đồng ý, hãy gửi ngay bản tin lên Telegram."),
        ("6. 🌤️ Tool mới: Weather", "Thời tiết hôm nay tại Hà Nội thế nào?"),
        ("7. 🔒 Tool mới: Redact", "Hãy kiểm tra và che dữ liệu nhạy cảm: Email là dev@corp.com và Token là sk-live-987654321."),
    ]

    for label, text in samples:
        if st.sidebar.button(label, key=f"btn_{label}", use_container_width=True):
            st.session_state.pending_prompt = text
            st.rerun()

    # Sidebar: Transcript Download & Stats
    st.sidebar.markdown("---")
    st.sidebar.subheader("📄 Bằng chứng Transcript (Audit)")
    st.sidebar.code(st.session_state.transcript_id, language="text")
    st.sidebar.write(f"Số lượt chat (turns): **{st.session_state.turn_index}**")

    current_transcript_json = json.dumps(st.session_state.transcript, ensure_ascii=False, indent=2, default=str)
    st.sidebar.download_button(
        label="💾 Tải Transcript JSON",
        data=current_transcript_json,
        file_name=f"{st.session_state.transcript_id}.transcript.json",
        mime="application/json",
        use_container_width=True,
    )

    # Sidebar: Tool Declarations list
    with st.sidebar.expander("🛠️ Danh sách Tool đang có (12 tools)"):
        try:
            decls = load_tool_declarations(ARTIFACTS_DIR / "tools.yaml")
            for t in decls:
                icon = TOOL_ICONS.get(t["name"], "🔧")
                is_custom = " *(Tool mới)*" if t["name"] in {"weather", "redact"} else ""
                st.markdown(f"**{icon} `{t['name']}`**{is_custom}: {t.get('description', '')}")
        except Exception as e:
            st.error(f"Không thể đọc tools.yaml: {e}")

    # Main Area Header
    st.title("🤖 Research Agent — Interactive UI (Checkpoint 5)")
    st.markdown(
        """
        Giao diện tương tác và kiểm thử trực tiếp cho **Research Agent** phục vụ Checkpoint 5 & Team Showdown.
        Hệ thống tự động ghi nhật ký minh bạch mọi lượt gọi công cụ vào file transcript đạt chuẩn rubric C6.
        """
    )

    # Info pills
    col_info1, col_info2, col_info3 = st.columns(3)
    col_info1.info(f"**Provider:** `{provider_name}` ({model_name or 'default'})")
    col_info2.info(f"**Artifact Version:** `{version_label}`")
    col_info3.info(f"**Transcript File:** `{st.session_state.transcript_id}.transcript.json`")

    # Display Chat History
    for msg in st.session_state.messages:
        role = msg["role"]
        content = msg.get("content", "")
        avatar = "🧑‍💻" if role == "user" else "🤖"
        with st.chat_message(role, avatar=avatar):
            if role == "assistant":
                render_tool_events(msg.get("tool_events", []), msg.get("rounds", []))
                if msg.get("status") == "waiting_for_user":
                    st.warning("⚠️ **Agent đang yêu cầu làm rõ / chờ bạn xác nhận:**")
            st.markdown(content)

    # Check if there is an active clarify prompt requiring yes/no confirmation
    clarify_meta = st.session_state.get("last_clarify")
    if clarify_meta and clarify_meta.get("response_type") == "yes_no":
        st.info("💡 **Hành động cần xác nhận:** Agent đang chờ câu trả lời Yes/No từ bạn.")
        c_yes, c_no = st.columns(2)
        with c_yes:
            if st.button("✅ Đồng ý, hãy gửi ngay (Confirmed)", use_container_width=True):
                st.session_state.last_clarify = None
                st.session_state.pending_prompt = "Đồng ý, tôi xác nhận hãy gửi ngay."
                st.rerun()
        with c_no:
            if st.button("❌ Không, hủy thao tác (Cancel)", use_container_width=True):
                st.session_state.last_clarify = None
                st.session_state.pending_prompt = "Không, vui lòng hủy việc gửi này."
                st.rerun()

    # Determine user prompt from chat input or pending prompt
    chat_input_val = st.chat_input("Nhập câu hỏi hoặc yêu cầu cho Research Agent...")
    prompt_to_run = None

    if chat_input_val:
        prompt_to_run = chat_input_val
    elif st.session_state.get("pending_prompt"):
        prompt_to_run = st.session_state.pop("pending_prompt")

    if prompt_to_run:
        # Clear clarify state on new input
        st.session_state.last_clarify = None
        st.session_state.turn_index += 1
        st.session_state.messages.append({"role": "user", "content": prompt_to_run})

        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(prompt_to_run)

        # Build prompt & prepare agent execution
        sys_prompt_path = ARTIFACTS_DIR / "system_prompt.md"
        tools_path = ARTIFACTS_DIR / "tools.yaml"
        system_prompt = sys_prompt_path.read_text(encoding="utf-8")
        tool_declarations = load_tool_declarations(tools_path)
        openai_tools = to_openai_tools(tool_declarations)

        try:
            provider = make_provider(provider_name)
        except Exception as exc:
            st.error(f"Lỗi khởi tạo provider `{provider_name}`: {exc}")
            return

        effective_model = model_name or getattr(provider, "default_model", None)

        messages = [
            {"role": "system", "content": system_prompt},
            *trim_history(st.session_state.history, history_window),
            {"role": "user", "content": prompt_to_run},
        ]

        turn_record: dict[str, Any] = {
            "turn_index": st.session_state.turn_index,
            "started_at": now_iso(),
            "user": prompt_to_run,
            "status": "started",
            "assistant_text": None,
            "rounds": [],
            "tool_events": [],
        }

        with st.chat_message("assistant", avatar="🤖"):
            status_box = st.status("🧠 Agent đang suy nghĩ và điều phối công cụ...", expanded=True)
            try:
                result = run_model_tool_loop_ui(
                    provider=provider,
                    messages=messages,
                    tools=openai_tools,
                    model=effective_model,
                    max_tool_rounds=max_tool_rounds,
                    status_container=status_box,
                )
                status_box.update(label="✅ Hoàn tất xử lý!", state="complete", expanded=False)

                turn_record.update(result)
                assistant_text = result.get("assistant_text", "")

                # Render tool calls
                render_tool_events(result.get("tool_events", []), result.get("rounds", []))

                if result.get("status") == "waiting_for_user":
                    st.warning("⚠️ **Agent đang yêu cầu làm rõ / chờ bạn xác nhận:**")
                    st.session_state.last_clarify = result.get("clarify_meta")

                st.markdown(assistant_text)

                # Update history
                st.session_state.history.append({"role": "user", "content": prompt_to_run})
                st.session_state.history.append({"role": "assistant", "content": assistant_text})
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": assistant_text,
                    "rounds": result.get("rounds", []),
                    "tool_events": result.get("tool_events", []),
                    "status": result.get("status", "answered"),
                })

            except Exception as exc:
                status_box.update(label="❌ Xảy ra lỗi!", state="error", expanded=True)
                error_str = f"{type(exc).__name__}: {str(exc)}"
                st.error(f"Lỗi hoàn thành từ Provider: {error_str}")
                turn_record.update({
                    "status": "provider_error",
                    "error": error_str,
                })

            turn_record["ended_at"] = now_iso()
            st.session_state.transcript["turns"].append(turn_record)
            write_transcript(st.session_state.transcript_path, st.session_state.transcript)

        # Trigger rerun to show confirmation buttons immediately if needed
        if st.session_state.get("last_clarify", {}).get("response_type") == "yes_no":
            st.rerun()


if __name__ == "__main__":
    main()
