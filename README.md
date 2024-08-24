# Assistant Function Schemas

This repository contains the function schemas used by the OpenAI assistant in our application. These schemas define how the assistant interacts with long-term and short-term memory, enabling it to save and retrieve important information based on user requests.

## Function Schemas

### 1. Save Memory

This function is used to save important information to the assistant's long-term memory based on a user request. The information is stored persistently and can be retrieved later, even across different sessions.

#### Schema

```json
{
  "name": "save_memory",
  "description": "Save important information to long-term memory based on user request.",
  "strict": false,
  "parameters": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "The specific information or text to be saved."
      }
    },
    "required": [
      "query"
    ]
  }
}
```

### 2. Retrieve Memory

This function allows the assistant to retrieve relevant information from its long-term memory based on a user's query. It helps the assistant provide contextually accurate responses by accessing previously stored information.

#### Schema

```json
{
  "name": "retrieve_memory",
  "description": "Retrieve relevant information from long-term memory based on a user's query.",
  "strict": false,
  "parameters": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "The specific query from the user to search in memory."
      }
    },
    "required": [
      "query"
    ]
  }
}
```

## How to Update Function Schemas

To ensure that the assistant functions correctly and remains up-to-date with the latest requirements, follow these steps:

1. **Edit the JSON Schema**: Update the schema files with the correct parameters and descriptions as needed.
2. **Commit Changes**: Commit the updated schemas to the repository with a clear commit message.
3. **Push to GitHub**: Push the changes to the main branch to update the repository.

## Contributing

If you need to make updates to the function schemas or have suggestions for improvements, please create a pull request or open an issue on this repository. All contributions are welcome!
