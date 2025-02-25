<p align="center">
  <a href="https://www.mnma.ai/" target="blank"><img src="assets/logo-full.svg" width="300" alt="MNMA Logo" /></a>
</p>

**Minima** is an open source RAG on-premises containers, with ability to integrate with ChatGPT and MCP. 
Minima can also be used as a fully local RAG.

[![smithery badge](https://smithery.ai/badge/minima)](https://smithery.ai/protocol/minima)

Minima currently supports three modes:
1. Isolated installation – Operate fully on-premises with containers, free from external dependencies such as ChatGPT or Claude. All neural networks (LLM, reranker, embedding) run on your cloud or PC, ensuring your data remains secure.

2. Custom GPT – Query your local documents using ChatGPT app or web with custom GPTs. The indexer running on your cloud or local PC, while the primary LLM remains ChatGPT.

3. Anthropic Claude – Use Anthropic Claude app to query your local documents. The indexer operates on your local PC, while Anthropic Claude serves as the primary LLM.

### Running as containers

1. Create a .env file in the project’s root directory (where you’ll find env.sample). Place .env in the same folder and copy all environment variables from env.sample to .env.

2. Ensure your .env file includes the following variables:
<ul>
   <li> LOCAL_FILES_PATH </li>
   <li> EMBEDDING_MODEL_ID </li>
   <li> EMBEDDING_SIZE </li>
   <li> OLLAMA_MODEL </li>
   <li> RERANKER_MODEL </li>
   <li> USER_ID </li> - required for ChatGPT integration, just use your email
   <li> PASSWORD </li> - required for ChatGPT integration, just use any password
</ul>

3. For fully local installation use: **docker compose -f docker-compose-ollama.yml --env-file .env up --build**.

4. For ChatGPT enabled installation use: **docker compose -f docker-compose-chatgpt.yml --env-file .env up --build**.

5. For MCP integration (Anthropic Desktop app usage): **docker compose -f docker-compose-mcp.yml --env-file .env up --build**.

6. In case of ChatGPT enabled installation copy OTP from terminal where you launched docker and use [Minima GPT](https://chatgpt.com/g/g-r1MNTSb0Q-minima-local-computer-search)  

7. If you use Anthropic Claude, just add folliwing to **/Library/Application\ Support/Claude/claude_desktop_config.json**

```
{
    "mcpServers": {
      "minima": {
        "command": "uv",
        "args": [
          "--directory",
          "/path_to_cloned_minima_project/mcp-server",
          "run",
          "minima"
        ]
      }
    }
  }
```
   
8. To use fully local installation go to `cd electron`, then run `npm install` and `npm start` which will launch Minima electron app.

9. Ask anything, and you'll get answers based on local files in {LOCAL_FILES_PATH} folder.

Explanation of Variables:

**LOCAL_FILES_PATH**: Specify the root folder for indexing (on your cloud or local pc). Indexing is a recursive process, meaning all documents within subfolders of this root folder will also be indexed. Supported file types: .pdf, .xls, .docx, .txt, .md, .csv.

**EMBEDDING_MODEL_ID**: Specify the embedding model to use. Currently, only Sentence Transformer models are supported. Testing has been done with sentence-transformers/all-mpnet-base-v2, but other Sentence Transformer models can be used.

**EMBEDDING_SIZE**: Define the embedding dimension provided by the model, which is needed to configure Qdrant vector storage. Ensure this value matches the actual embedding size of the specified EMBEDDING_MODEL_ID.

**OLLAMA_MODEL**: Set up the Ollama model, use an ID available on the Ollama [site](https://ollama.com/search). Please, use LLM model here, not an embedding.

**RERANKER_MODEL**: Specify the reranker model. Currently, we have tested with BAAI rerankers. You can explore all available rerankers using this [link](https://huggingface.co/collections/BAAI/).

**USER_ID**: Just use your email here, this is needed to authenticate custom GPT to search in your data.

**PASSWORD**: Put any password here, this is used to create a firebase account for the email specified above.

### Text Chunking Configuration

Minima provides several options to customize how documents are split into chunks for indexing:

**CHUNK_SIZE**: Default chunk size (in characters) for text segmentation. Default: 500

**CHUNK_OVERLAP**: Number of characters that should overlap between chunks. Default: 200

**AUTO_CHUNKING**: When set to "true" (default), the system automatically uses optimized chunking strategies for different file types. Set to "false" to use a single strategy for all files.

**DEFAULT_CHUNK_STRATEGY**: Default strategy to use when AUTO_CHUNKING is disabled. Options:
  - `default`: Standard chunking based on paragraphs and sentences
  - `markdown_aware`: Optimized for Markdown documents, respects headers and structure
  - `sentence_aware`: Prioritizes keeping sentences intact

**File-specific chunk sizes**:
  - `MARKDOWN_CHUNK_SIZE`: Specific chunk size for markdown (.md) files
  - `PDF_CHUNK_SIZE`: Specific chunk size for PDF files
  - `DOC_CHUNK_SIZE`: Specific chunk size for Word documents (.doc, .docx)

When AUTO_CHUNKING is enabled, the system applies these optimizations:
- Markdown files (.md): Uses header-aware chunking that respects document structure
- PDF files (.pdf): Uses paragraph-focused chunking with custom chunk size
- Word documents (.doc, .docx): Uses paragraph-focused chunking with custom chunk size
- Text files (.txt): Uses sentence-focused chunking to preserve meaning
- Data files (.csv, .xls, .xlsx): Uses row-based chunking to keep data rows together

Example of .env file for on-premises/local usage:
```
LOCAL_FILES_PATH=/Users/davidmayboroda/Downloads/PDFs/
EMBEDDING_MODEL_ID=sentence-transformers/all-mpnet-base-v2
EMBEDDING_SIZE=768
OLLAMA_MODEL=qwen2:0.5b # must be LLM model id from Ollama models page
RERANKER_MODEL=BAAI/bge-reranker-base # please, choose any BAAI reranker model

# Chunking configuration (optional)
CHUNK_SIZE=1000 # increase default chunk size to 1000 characters
CHUNK_OVERLAP=200
AUTO_CHUNKING=true # automatically use optimized strategies per file type
DEFAULT_CHUNK_STRATEGY=default # only used when AUTO_CHUNKING=false
MARKDOWN_CHUNK_SIZE=1500 # larger chunks for markdown files
PDF_CHUNK_SIZE=800 # custom size for PDFs
```

To use a chat ui, please navigate to **http://localhost:3000**

Example of .env file for Claude app:
```
LOCAL_FILES_PATH=/Users/davidmayboroda/Downloads/PDFs/
EMBEDDING_MODEL_ID=sentence-transformers/all-mpnet-base-v2
EMBEDDING_SIZE=768
```
For the Claude app, please apply the changes to the claude_desktop_config.json file as outlined above.

Example of .env file for ChatGPT custom GPT usage:
```
LOCAL_FILES_PATH=/Users/davidmayboroda/Downloads/PDFs/
EMBEDDING_MODEL_ID=sentence-transformers/all-mpnet-base-v2
EMBEDDING_SIZE=768
USER_ID=user@gmail.com # your real email
PASSWORD=password # you can create here password that you want
```

Also, you can run minima using **run.sh**.

### Installing via Smithery (MCP usage)

To install Minima for Claude Desktop automatically via [Smithery](https://smithery.ai/protocol/minima):

```bash
npx -y @smithery/cli install minima --client claude
```

**For MCP usage, please be sure that your local machines python is >=3.10 and 'uv' installed.**

Minima (https://github.com/dmayboroda/minima) is licensed under the Mozilla Public License v2.0 (MPLv2).
