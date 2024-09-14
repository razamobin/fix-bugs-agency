from agency_swarm import Agent, Agency, set_openai_key, BaseTool
from dotenv import load_dotenv
import os
import difflib
import os
from datetime import datetime
from agency_swarm.tools import BaseTool
from pydantic import Field

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
set_openai_key(api_key)


class BugFixProposalTool(BaseTool):
    """
    A tool for creating and saving proposed bug fixes as diffs.
    """

    source_code_dir: str = Field(
        ...,
        description="The directory path where source code files are located.")
    proposed_changes_dir: str = Field(
        ...,
        description=
        "The directory path where proposed changes (diffs) will be saved.")
    file_name: str = Field(
        ...,
        description="The name of the file being modified (e.g., 'main.go').")
    original_content: str = Field(
        ..., description="The original content of the file.")
    modified_content: str = Field(
        ..., description="The proposed modified content of the file.")
    bug_description: str = Field(
        ..., description="A brief description of the bug being addressed.")
    short_fix_description: str = Field(
        ...,
        description=
        "A short, descriptive name for the bug fix (e.g., 'fix_null_pointer', 'update_api_call')."
    )

    def run(self):
        """
        Creates a diff of the proposed changes and saves it to disk.

        Returns:
            str: The path to the saved diff file.
        """
        # Create diff
        diff = difflib.unified_diff(
            self.original_content.splitlines(keepends=True),
            self.modified_content.splitlines(keepends=True),
            fromfile=self.file_name,
            tofile=f"{self.file_name} (proposed fix)")

        # Create a filename for the diff
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_description = "".join(c if c.isalnum() or c == '_' else '_'
                                   for c in self.short_fix_description)
        diff_filename = f"{timestamp}_{self.file_name}_{safe_description}.diff"

        # Ensure the proposed changes directory exists
        os.makedirs(self.proposed_changes_dir, exist_ok=True)

        # Save the diff
        diff_path = os.path.join(self.proposed_changes_dir, diff_filename)
        with open(diff_path, 'w') as f:
            f.writelines(diff)

        return f"Proposed fix saved as: {diff_path}"


class ErrorLogAnalyzer(Agent):

    def __init__(self):
        super().__init__(
            name="ErrorLogAnalyzer",
            description=
            "An agent that analyzes error logs and suggests improvements to the source code.",
            instructions="""
            1. Use the ErrorLogTool to fetch recent error logs.
            2. Analyze the logs to identify referenced file names and line numbers.
            3. For each identified issue:
               a. Use the SourceCodeTool to retrieve the content of the specific file mentioned in the error logs.
               b. Analyze the source code in context of the error and devise a fix.
               c. Use the BugFixProposalTool to create a diff for the proposed fix:
                  - Set source_code_dir to the directory containing the source files.
                  - Set proposed_changes_dir to the directory where diffs should be saved.
                  - Set file_name to the name of the file being modified.
                  - Set original_content to the current content of the file.
                  - Set modified_content to your proposed fixed version of the file.
                  - Set bug_description to a brief description of the bug and your fix.
                  - Set short_fix_description to a concise, descriptive name for the fix (e.g., 'fix_null_pointer', 'update_api_call').
                     This should be a short phrase that clearly indicates the nature of the fix.
               d. Run the BugFixProposalTool and note the location of the saved diff.
            4. After addressing all issues, summarize the proposed fixes and their corresponding diff file locations.
            5. If you encounter any difficulties or uncertainties, ask for clarification or assistance.
            """,
            tools=[ErrorLogTool, SourceCodeTool, BugFixProposalTool],
        )


class ErrorLogTool(BaseTool):
    """
    A tool for fetching the most recent error logs from a specified directory.
    """

    error_logs_dir: str = Field(
        ...,
        description="The directory path where error log files are stored.")

    def run(self):
        """
        Fetches the last 100 lines from the most recent error logs.

        Returns:
            list: The last 100 lines of error logs.
        """
        logs = []
        for file in sorted(os.listdir(self.error_logs_dir), reverse=True):
            with open(os.path.join(self.error_logs_dir, file), 'r') as f:
                logs.extend(f.readlines()[-100:])
                if len(logs) >= 100:
                    break
        return logs[-100:]


class SourceCodeTool(BaseTool):
    """
    A tool for reading specific source code files from a given directory.
    """

    source_code_dir: str = Field(
        ...,
        description="The directory path where source code files are located.")
    file_name: str = Field(
        ...,
        description=
        "The name of the file to read (e.g., 'main.go', 'utils/helpers.py'). Can be a full path, relative path, or just a file name."
    )

    def run(self):
        """
        Reads the content of the specified source code file.

        Returns:
            str: The content of the file if found, or an error message if the file doesn't exist.
        """
        # Check if it's a full path or relative path
        full_path = os.path.join(self.source_code_dir, self.file_name)
        if os.path.exists(full_path):
            with open(full_path, 'r') as f:
                return f.read()

        # If not found, search for the file in the source directory
        for root, dirs, files in os.walk(self.source_code_dir):
            if self.file_name in files:
                with open(os.path.join(root, self.file_name), 'r') as f:
                    return f.read()

        return f"File not found: {self.file_name}"


error_log_analyzer = ErrorLogAnalyzer()

agency = Agency(
    [error_log_analyzer],
    shared_instructions="Analyze error logs and suggest code improvements.",
)

if __name__ == '__main__':
    agency.run_demo()
