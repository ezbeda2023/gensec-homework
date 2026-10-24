here are my assignment instructions help build this out entierly and create the repo and make sure to push as in the instructions: if you need any more info let me know and I will provide it.

Within your course repository, create a directory for the homework, then commit and push to your remote repository.

cd <path_to_repo> mkdir hw4 touch hw4/agent.py touch hw4/mcp-server.py touch hw4/screencast_url.txt git add hw4 git commit -m "initial commit" git push

In this homework, based on the lab exercises, you will create your own MCP-based agent application using a combination of an MCP server that you write and an MCP server you integrate from published sources.

The MCP server that you write should:
- Implement a set of custom tools for performing functions or returning data or prompts

The MCP server that you integrate should:
- Select MCP servers from the original repository (https://github.com/modelcontextprotocol/servers) or from the more recent MCP Market page (https://mcpmarket.com/server).
CAUTION: because malicious MCP servers are common, investigate the authenticity of the server before installing or running it.

The MCP agent application should
- Configure each MCP server and be able to coordinate the use of each of the tools in them to solve a multi-step problem

Your development should be organized and incremental, with frequent commits into your git repository. Code should also be properly documented via Python docstrings (https://peps.python.org/pep-0257/). Use the uv virtual environment manager to isolate your project dependencies. Use a virtual Python environment as demonstrated in the labs Codelabs. In addition, you must also ensure API keys do not show up in your source files, but rather are passed in via environment variables. Ensure your application code is pushed to your repository before class.

Agentic Code Help and Proper Documentation

For this assignment you must use a coding agent from VSCode (e.g. Claude, Codex). Follow these instructions:
- Download the Homework Template file (https://icardei.github.io/gensec-web/homework-template.docx).
- Rename it to hw3-FAUID.docx, FAUID being your FAU ID.
- During developement, for every significant task given to the agent you must:
  - take a screenshot of your VSCode window showing the prompt you gave to the agent and the response it gave you back.
  - take a screenshot of your VSCode window showing at least the top few lines of code that were generated or modified by the agent
  - the screenshots must show visible your FAU ID or name
  - insert these screenshots into the homework Word document, along with task prompt given to the agent.
- Add the missing information between < and > in the Word document.
- When finished, convert the Word document to PDF and upload it on the Homework Canvas page.
