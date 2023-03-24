"""Chain for chatting with a vector database."""
from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from langchain.chains.chat_vector_db.base import _get_chat_history, ChatVectorDBChain

class CustomChatVectorDBChain(ChatVectorDBChain):
    """Custom Chain for chatting with a vector database."""

    return_condensed_question: bool = True

    @property
    def output_keys(self) -> List[str]:
        """Return the output keys.

        :meta private:
        """
        _output_keys = [self.output_key]
        if self.return_source_documents:
            _output_keys = _output_keys + ["source_documents"]
        if self.return_condensed_question:
            _output_keys = _output_keys + ["condensed_question"]
        return _output_keys

    def _call(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        question = inputs["question"]
        get_chat_history = self.get_chat_history or _get_chat_history
        chat_history_str = get_chat_history(inputs["chat_history"])
        vectordbkwargs = inputs.get("vectordbkwargs", {})
        if chat_history_str:
            new_question = self.question_generator.run(
                question=question, chat_history=chat_history_str
            )
        else:
            new_question = question
        docs = self.vectorstore.similarity_search(
            new_question, k=self.top_k_docs_for_context, **vectordbkwargs
        )
        new_inputs = inputs.copy()
        new_inputs["question"] = new_question
        new_inputs["chat_history"] = chat_history_str
        answer, _ = self.combine_docs_chain.combine_docs(docs, **new_inputs)
        ret_dict = {self.output_key: answer}
        if self.return_source_documents:
            ret_dict.update(source_documents=docs)
        if self.return_condensed_question:
            ret_dict.update(condensed_question=new_inputs["question"])
        
        return ret_dict

    async def _acall(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        question = inputs["question"]
        get_chat_history = self.get_chat_history or _get_chat_history
        chat_history_str = get_chat_history(inputs["chat_history"])
        vectordbkwargs = inputs.get("vectordbkwargs", {})
        if chat_history_str:
            new_question = await self.question_generator.arun(
                question=question, chat_history=chat_history_str
            )
        else:
            new_question = question
        # TODO: This blocks the event loop, but it's not clear how to avoid it.
        docs = self.vectorstore.similarity_search(
            new_question, k=self.top_k_docs_for_context, **vectordbkwargs
        )
        new_inputs = inputs.copy()
        new_inputs["question"] = new_question
        new_inputs["chat_history"] = chat_history_str
        answer, _ = await self.combine_docs_chain.acombine_docs(docs, **new_inputs)
        ret_dict = {self.output_key: answer}
        if self.return_source_documents:
            ret_dict.update(source_documents=docs)
        if self.return_condensed_question:
            ret_dict.update(condensed_question=new_inputs["question"])
        
        return ret_dict
