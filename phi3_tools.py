# # import argparse
# # # from langchain.vectorstores.chroma import Chroma
# # from langchain_community.vectorstores import Chroma
# # from langchain.prompts import ChatPromptTemplate
# # from langchain_community.llms.ollama import Ollama

# # from get_embedding_function import get_embedding_function

# # CHROMA_PATH = "chroma"

# # PROMPT_TEMPLATE = """
# # Answer the question based only on the following context:

# # {context}

# # ---

# # Answer the question based on the above context: {question}
# # """


# # def main():
# #     # Create CLI.
# #     parser = argparse.ArgumentParser()
# #     parser.add_argument("query_text", type=str, help="The query text.")
# #     args = parser.parse_args()
# #     query_text = input('Question: ')
# #     query_rag(query_text)


# # def query_rag(query_text: str):
# #     # Prepare the DB.
# #     embedding_function = get_embedding_function()
# #     db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

# #     # Search the DB.
# #     results = db.similarity_search_with_score(query_text, k=5)

# #     context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
# #     prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
# #     prompt = prompt_template.format(context=context_text, question=query_text)
# #     print(prompt)

# #     model = Ollama(model="mistral")
# #     response_text = model.invoke(prompt)

# #     sources = [doc.metadata.get("id", None) for doc, _score in results]
# #     formatted_response = f"Response: {response_text}\nSources: {sources}"
# #     print(formatted_response)
# #     return response_text


# # if __name__ == "__main__":
# #     main()



# # import argparse
# # # from langchain.vectorstores.chroma import Chroma
# # from langchain_community.vectorstores import Chroma
# # from langchain.prompts import ChatPromptTemplate
# # from langchain_community.llms.ollama import Ollama

# # from get_embedding_function import get_embedding_function

# # CHROMA_PATH = "chroma"

# # PROMPT_TEMPLATE = """
# # Answer the question based only on the following context:

# # {context}

# # ---

# # Answer the question based on the above context: {question}
# # """


# # def main():
# #     # Create CLI.
# #     parser = argparse.ArgumentParser()
# #     parser.add_argument("query_text", type=str, help="The query text.")
# #     args = parser.parse_args()
    
# #     # Pass the command line argument to the function.
# #     query_rag(args.query_text)


# # def query_rag(query_text: str):
# #     # Prepare the DB.
# #     embedding_function = get_embedding_function()
# #     db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

# #     # Search the DB.
# #     results = db.similarity_search_with_score(query_text, k=5)

# #     context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
# #     prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
# #     prompt = prompt_template.format(context=context_text, question=query_text)
# #     print(prompt)

# #     model = Ollama(model="mistral")
# #     response_text = model.invoke(prompt)

# #     sources = [doc.metadata.get("id", None) for doc, _score in results]
# #     formatted_response = f"Response: {response_text}\nSources: {sources}"
# #     print(formatted_response)
# #     return response_text


# # if __name__ == "__main__":
# #     main()

# ####### kuhan nix code
# # import argparse
# # from langchain_community.vectorstores import Chroma
# # from langchain.prompts import ChatPromptTemplate
# # from langchain_community.llms import LlamaCpp
# # from langchain_core.callbacks import CallbackManager, StreamingStdOutCallbackHandler
# # from get_embedding_function import get_embedding_function

# # CHROMA_PATH = "chroma"

# # PROMPT_TEMPLATE = """
# # Answer the question based only on the following context:

# # {context}

# # ---

# # Answer the question based on the above context: {question}
# # """

# # def main():
# #     # Create CLI.
# #     parser = argparse.ArgumentParser()
# #     parser.add_argument("query_text", type=str, help="The query text.")
# #     args = parser.parse_args()
    
# #     # Pass the command line argument to the function.
# #     query_rag(args.query_text)

# # def query_rag(query_text: str):
# #     # Prepare the DB.
# #     embedding_function = get_embedding_function()
# #     db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

# #     # Search the DB.
# #     results = db.similarity_search_with_score(query_text, k=5)

# #     context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
# #     prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
# #     prompt = prompt_template.format(context=context_text, question=query_text)
# #     print(prompt)

# #     # Set up the LlamaCpp model
# #     n_gpu_layers = -1
# #     n_batch = 512
# #     callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
    
# #     # Make sure the model path is correct for your system!
# #     model_path = "/Users/sanjaypalanisami/5AP/Phi-3-mini-4k-instruct-function-calling_Q6_K.gguf"
# #     llm = LlamaCpp(
# #         model_path=model_path,
# #         n_gpu_layers=n_gpu_layers,
# #         n_batch=n_batch,
# #         callback_manager=callback_manager,
# #         verbose=True,  # Verbose is required to pass to the callback manager
# #     )
    
# #     # Generate a response using the LlamaCpp model
# #     llm_chain = prompt_template | llm
# #     response_text = llm_chain.invoke({"question": query_text})

# #     sources = [doc.metadata.get("id", None) for doc, _score in results]
# #     formatted_response = f"Response: {response_text}\nSources: {sources}"
# #     print(formatted_response)
# #     return response_text

# # if __name__ == "__main__":
# #     main()

#################.   working ###################### 

# import argparse
# from langchain_community.vectorstores import Chroma
# from langchain.prompts import ChatPromptTemplate
# from langchain_community.llms import LlamaCpp
# from langchain_core.callbacks import CallbackManager, StreamingStdOutCallbackHandler
# from get_embedding_function import get_embedding_function

# CHROMA_PATH = "chroma"

# PROMPT_TEMPLATE = """
# Answer the question based only on the following context:

# {context}

# ---

# Answer the question based on the above context: {question}
# """

# def main():
#     # Create CLI.
#     parser = argparse.ArgumentParser()
#     parser.add_argument("query_text", type=str, help="The query text.")
#     args = parser.parse_args()
    
#     # Pass the command line argument to the function.
#     query_rag(args.query_text)

# def query_rag(query_text: str):
#     # Prepare the DB.
#     embedding_function = get_embedding_function()
#     db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

#     # Search the DB.
#     results = db.similarity_search_with_score(query_text, k=5)

#     context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
#     prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
#     prompt = prompt_template.format(context=context_text, question=query_text)
#     print(prompt)

#     # Set up the LlamaCpp model
#     n_gpu_layers = -1
#     n_batch = 2000
#     callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
    
#     # Make sure the model path is correct for your system!
#     model_path = "/Users/sanjaypalanisami/5AP/Phi-3-mini-4k-instruct-function-calling_Q6_K.gguf"
#     llm = LlamaCpp(
#         model_path=model_path,
#         n_gpu_layers=n_gpu_layers,
#         n_batch=n_batch,
#         n_ctx = 2048,
#         callback_manager=callback_manager,
#         verbose=True,  # Verbose is required to pass to the callback manager
#     )
    
#     # Generate a response using the LlamaCpp model
#     response_text = llm.invoke(prompt)

#     sources = [doc.metadata.get("id", None) for doc, _score in results]
#     formatted_response = f"Response: {response_text}\nSources: {sources}"
#     print(formatted_response)
#     return response_text

# if __name__ == "__main__":
#     main()



import argparse
from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_community.llms import LlamaCpp
from langchain_core.callbacks import CallbackManager, StreamingStdOutCallbackHandler
from get_embedding_function import get_embedding_function
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

CHROMA_PATH = "chroma"

PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""

def main():
    # Create CLI.
    parser = argparse.ArgumentParser()
    parser.add_argument("query_text", type=str, help="The query text.")
    args = parser.parse_args()
    
    # Pass the command line argument to the function.
    query_rag(args.query_text)

def query_rag(query_text: str):
    # Prepare the DB.
    embedding_function = get_embedding_function()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    # Search the DB.
    results = db.similarity_search_with_score(query_text, k=5)

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)
    print(prompt)

    # Set up the LlamaCpp model
    n_gpu_layers = -1
    n_batch = 2000
    callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
    
    # Make sure the model path is correct for your system!
    model_path = "/Users/sanjaypalanisami/5AP/Phi-3-mini-4k-instruct-function-calling_Q6_K.gguf"
    llm = LlamaCpp(
        model_path=model_path,
        n_gpu_layers=n_gpu_layers,
        n_batch=n_batch,
        n_ctx = 2048,
        callback_manager=callback_manager,
        verbose=True,  # Verbose is required to pass to the callback manager
    )
    
    # Generate a response using the LlamaCpp model
    response_text = llm.invoke(prompt)

    sources = [doc.metadata.get("id", None) for doc, _score in results]
    formatted_response = f"Response: {response_text}\nSources: {sources}"
    print(formatted_response)

    # Integrate the search tool
    integrate_search_tool(query_text)

    return response_text

def integrate_search_tool(query_text: str):
    model_id = "mzbac/Phi-3-mini-4k-instruct-function-calling"
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.bfloat16,
        device_map="auto",
    )

    tool = {
        "name": "search_web",
        "description": "Perform a web search for a given search terms.",
        "parameter": {
            "type": "object",
            "properties": {
                "search_terms": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "The search queries for which the search is performed.",
                    "required": True,
                }
            },
        },
    }

    messages = [
        {
            "role": "user",
            "content": f"You are a helpful assistant with access to the following functions. Use them if required - {str(tool)}",
        },
        {"role": "user", "content": f"Perform a web search for the following query: {query_text}"},
    ]

    input_ids = tokenizer.apply_chat_template(
        messages, add_generation_prompt=True, return_tensors="pt"
    ).to(model.device)

    terminators = [tokenizer.eos_token_id, tokenizer.convert_tokens_to_ids("")]

    outputs = model.generate(
        input_ids,
        max_new_tokens=256,
        eos_token_id=terminators,
        do_sample=True,
        temperature=0.1,
    )
    response = outputs[0]
    print(tokenizer.decode(response))

if __name__ == "__main__":
    main()

