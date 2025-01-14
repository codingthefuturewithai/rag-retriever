# Configuring AI Assistants with RAG Retriever

This guide explains how to configure AI coding assistants (aider and Cursor) to use RAG Retriever for knowledge verification.

## ⚠️ Important Note About LLM Behavior

This note applies to working with LLMs in general, not just with RAG Retriever:

Due to the nondeterministic nature of Large Language Models (LLMs), AI coding assistants may not always reliably follow their instructions, even when properly configured. This is a fundamental characteristic of LLMs, not specific to any particular tool or instruction set. Users should:

- Remain vigilant for potential hallucinations or cases where the assistant makes claims without verification
- Watch for responses about recent features/versions that aren't properly validated
- Gently remind the assistant about its instructions if it seems to be operating on assumptions
- Be particularly careful when the assistant makes claims about recent releases, version-specific features, or API changes

## Prerequisites

- RAG Retriever installed and configured (see main [README.md](../../README.md))
- Either [aider](https://github.com/paul-gauthier/aider) or [Cursor](https://cursor.sh/) installed

## Configuring Aider

1. Create or edit `~/.aider.conf.yml`:

   ```bash
   mkdir -p ~/.aider
   touch ~/.aider.conf.yml
   ```

2. Copy the RAG Retriever instructions file to your aider configuration directory:

   ```bash
   mkdir -p ~/.aider/custom-instructions
   cp retriever-coding-assistant-instructions.md ~/.aider/custom-instructions/
   ```

3. Add the RAG Retriever instructions file to the `read` section of your config file:

   ```yaml
   read:
     - ~/.aider/custom-instructions/retriever-coding-assistant-instructions.md
   ```

   See the [aider configuration documentation](https://aider.chat/docs/config/aider_conf.html) for more details about the config file format.

   ![Aider Configuration Example](../images/aider-settings-with-retriever-instructions.png)

4. Start aider normally - it will now use the RAG Retriever instructions

## Configuring Cursor

1. Open Command Palette (Shift+Cmd+P)
2. Select "Cursor Settings"
3. Click on "General" in the left sidebar
4. Under "Rules for AI", paste the contents of [RAG Retriever Usage Instructions](./retriever-coding-assistant-instructions.md)

![Cursor Settings Configuration](../images/cursor-settings-with-retriever-instructions.png)

## Populating the Vector Store

Before the AI assistants can use RAG Retriever effectively, you need to populate its vector store with relevant documentation. The vector store will be empty initially, and queries won't return results until you've loaded documents using the `--fetch` or `--ingest` commands.

For example, to load documentation for testing the configuration with recent framework features:

```bash
# Load Angular 18.1 documentation
rag-retriever --fetch https://blog.ninja-squad.com/2024/07/10/what-is-new-angular-18.1 --max-depth 0

# Load Java 23 documentation
rag-retriever --fetch https://www.happycoders.eu/java/java-23-features --max-depth 0
```

You can load additional documentation based on your project's needs using either:

- `rag-retriever --fetch URL` for web documentation
- `rag-retriever --ingest-file FILE` for local documentation
- `rag-retriever --ingest-directory DIR` for directories of local documentation

## Verifying the Configuration

To verify that the AI assistants are properly configured with RAG Retriever instructions, try one of these test prompts (after loading the documentation above):

1. Ask about a very recent framework feature:

   ```
   Create an Angular 18.1 component using the new @let syntax
   ```

2. Request implementation of a new language feature:
   ```
   Write a Java 23 method using the new Markdown Documentation Comments feature
   ```

The AI assistant should recognize these as scenarios requiring knowledge verification and attempt to use RAG Retriever to gather accurate information.

Here are examples of properly configured assistants using RAG Retriever:

**Example 1: Aider using RAG Retriever to verify knowledge about Angular 18.1**
![Aider Using RAG Retriever for Angular 18.1 Knowledge](../images/aider-example-using-retriever.png)

**Example 2: Cursor using RAG Retriever to verify Java 23 features**
![Cursor Using RAG Retriever for Java 23 Features](../images/cursor-example-using-retriever.png)

## Expected Behavior

When properly configured, the AI assistant should:

1. Recognize when it needs to verify its knowledge
2. Attempt to use RAG Retriever with appropriate queries
3. Evaluate the relevance scores of results
4. Either proceed with high-confidence information or request clarification

If the assistant doesn't exhibit this behavior, double-check that you've:

- Copied the complete RAG Retriever instructions
- Configured the correct file/location for your AI assistant
- Populated the vector store with relevant documentation
- Restarted the AI assistant after configuration

If everything is configured correctly but the assistant still isn't following the instructions, simply remind it about checking its knowledge using RAG Retriever. For example:

"Please remember to verify your knowledge about [feature/version] using RAG Retriever before proceeding."
