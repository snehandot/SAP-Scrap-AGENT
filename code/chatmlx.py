from langchain_community.llms import MLXPipeline
from langchain.schema import HumanMessage
from mlx_lm import load

model_id = "mlx-community/Phi-3-mini-128k-instruct-4bit"
model, tokenizer = load(model_id)

# Initialize the pipeline with the loaded model and tokenizer
llm = MLXPipeline(
    model=model,
    tokenizer=tokenizer,
    pipeline_kwargs={
        # "max_tokens":,  # Set a high limit for max tokens
        "temp": 1,           # Temperature setting for randomness
        "verbose": True      # Enable verbose logging
    },
)

# Print the configuration to debug if parameters are set correctly
print("Pipeline Configuration:", llm)

# Create the prompt with clear instructions
messages = [
    HumanMessage(
        content=("Write a detailed essay about the mystical world of clouds, "
                 "covering various aspects such as types of clouds, their formation processes, "
                 "and their role in the Earth's climate system. The essay should be approximately 1000 words long.")
    ),
]


s=llm.invoke(messages)
print(s)