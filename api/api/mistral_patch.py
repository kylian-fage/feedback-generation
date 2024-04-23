from typing import Any, Dict, List, Optional, Tuple

from langchain_core.messages.base import BaseMessage
from langchain_mistralai.chat_models import (
    ChatMistralAI,
    _convert_message_to_mistral_chat_message,
)


class PatchedChatMistralAI(ChatMistralAI):
    def _create_message_dicts(
        self, messages: List[BaseMessage], stop: Optional[List[str]]
    ) -> Tuple[List[Dict], Dict[str, Any]]:
        params = self._client_params
        if stop is not None or "stop" in params:
            if "stop" in params:
                params.pop("stop")
        # `_convert_message_to_mistral_chat_message` returns a dict with
        # `tool_calls` and `content` keys. According to Mistral API
        # docs, assistant message must have either `content` or
        # `tool_calls`, but not both. Otherwise, the API will return
        # an error. In our case, `tool_calls` is not used, so we remove
        # it.
        # message_dicts = [
        #     _convert_message_to_mistral_chat_message(m)
        #     for m in messages
        # ]
        message_dicts = [
            {
                k: v
                for k, v in _convert_message_to_mistral_chat_message(m).items()
                if k != "tool_calls"
            }
            for m in messages
        ]
        return message_dicts, params
