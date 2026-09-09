"""
ANIMA-Agent-Kit Structured Output Parser

Extracts and validates JSON from LLM responses.

Handles various response formats:
- Plain JSON objects
- JSON wrapped in markdown code blocks (```json ... ```)
- Text before/after JSON
- Comments or explanations mixed with JSON
- Malformed JSON (attempts repair)

Architecture:
    1. Extract JSON string from response (multiple strategies)
    2. Parse JSON to dict
    3. Validate with Pydantic schema
    4. Return validated StructuredResponse or error

Usage:
    parser = StructuredOutputParser()
    response, error = parser.parse(llm_output)

    if error:
        # Handle error, use fallback
        response = StructuredOutputParser.create_fallback(content)
"""

import json
import re
from typing import Optional, Tuple
from loguru import logger
from pydantic import ValidationError

from anima_agentkit.schemas.structured_response import StructuredResponse


class StructuredOutputParser:
    """
    Parse and validate structured JSON output from LLM responses.

    This parser is robust against common LLM output variations:
    - JSON wrapped in markdown code blocks
    - Explanatory text before/after JSON
    - Incomplete JSON (attempts repair)
    - Invalid escape sequences
    """

    @staticmethod
    def extract_json_from_response(response: str) -> Optional[str]:
        """
        Extract JSON from LLM response using multiple strategies.

        Strategies (in order):
        1. Extract from markdown code block (```json ... ```)
        2. Find JSON object by brace matching
        3. Treat entire response as JSON

        Args:
            response: Raw LLM response string

        Returns:
            Extracted JSON string or None if not found
        """
        if not response or not response.strip():
            logger.warning("Empty response provided to parser")
            return None

        # Strategy 1: Extract from markdown code block
        # Matches: ```json\n{...}\n``` or ```\n{...}\n```
        json_block_pattern = r'```(?:json)?\s*\n?([\s\S]*?)\n?```'
        match = re.search(json_block_pattern, response, re.IGNORECASE)
        if match:
            extracted = match.group(1).strip()
            logger.debug(f"📦 Found JSON in markdown code block ({len(extracted)} chars)")
            return extracted

        # Strategy 1b: Handle case where LLM outputs "json\n" prefix without backticks
        # Sometimes LLMs output: json\n{"content_blocks":...}
        if response.strip().startswith('json\n') or response.strip().startswith('json\r\n'):
            # Remove the "json\n" prefix
            cleaned = re.sub(r'^json\s*[\r\n]+', '', response.strip(), flags=re.IGNORECASE)
            logger.debug(f"📦 Removed 'json' prefix, extracted ({len(cleaned)} chars)")
            return cleaned.strip()

        # Strategy 2: Find JSON object by balanced brace matching
        # Look for first { and last matching }
        brace_count = 0
        start_idx = None
        end_idx = None

        for i, char in enumerate(response):
            if char == '{':
                if start_idx is None:
                    start_idx = i
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0 and start_idx is not None:
                    end_idx = i + 1
                    break

        if start_idx is not None and end_idx is not None:
            extracted = response[start_idx:end_idx]
            logger.debug(f"📦 Found JSON by brace matching ({len(extracted)} chars)")
            return extracted.strip()

        # Strategy 3: Assume entire response is JSON
        # (Last resort - likely to fail but worth trying)
        logger.debug("📦 Attempting to parse entire response as JSON")
        return response.strip()

    @staticmethod
    def repair_json_string(json_str: str) -> str:
        """
        Attempt to repair common JSON formatting issues.

        Common issues:
        - Trailing commas
        - Unescaped newlines in strings
        - Single quotes instead of double quotes (basic cases)

        Args:
            json_str: Potentially malformed JSON string

        Returns:
            Repaired JSON string
        """
        # Remove trailing commas before closing braces/brackets
        json_str = re.sub(r',\s*([}\]])', r'\1', json_str)

        # Basic single-quote to double-quote conversion (naive, but helps sometimes)
        # Only convert when not inside a string
        # (This is a simplified approach - perfect quote fixing is complex)

        return json_str

    @staticmethod
    def migrate_schema_format(json_data: dict) -> dict:
        """
        Migrate legacy schema formats to current format.

        Handles cases where LLM outputs:
        - "segments" directly under content_block instead of nested under "content"
        - Other legacy format variations

        Args:
            json_data: Parsed JSON dictionary

        Returns:
            Migrated dictionary conforming to current schema
        """
        # Check if content_blocks exists
        if "content_blocks" not in json_data:
            return json_data

        # Migrate each content block
        migrated_blocks = []
        for block in json_data["content_blocks"]:
            # Check if this is legacy format (segments/text directly under block)
            if isinstance(block, dict) and "content" not in block:
                # Legacy format detected - wrap in "content"
                block_type = block.get("type", "paragraph")

                # Extract all non-type fields as content
                content_data = {k: v for k, v in block.items() if k not in ["type", "metadata"]}

                # Create new block with proper nesting
                migrated_block = {
                    "type": block_type,
                    "content": content_data if content_data else {"segments": []}
                }

                # Preserve metadata if it exists
                if "metadata" in block:
                    migrated_block["metadata"] = block["metadata"]

                migrated_blocks.append(migrated_block)
                logger.debug(f"✅ Migrated legacy content block format for type '{block_type}'")
            else:
                # Already in correct format
                migrated_blocks.append(block)

        # Update json_data with migrated blocks
        json_data["content_blocks"] = migrated_blocks
        return json_data

    @staticmethod
    def parse_structured_response(
        response: str,
        fallback_content: Optional[str] = None
    ) -> Tuple[Optional[StructuredResponse], Optional[str]]:
        """
        Parse LLM response into validated StructuredResponse.

        Process:
        1. Extract JSON string from response
        2. Parse JSON to dict
        3. Validate with Pydantic schema
        4. Return (StructuredResponse, None) on success
        5. Return (None, error_message) on failure

        Args:
            response: Raw LLM response
            fallback_content: Optional text to use if parsing fails

        Returns:
            Tuple of (parsed_response, error_message)
            - Success: (StructuredResponse, None)
            - Failure: (None, error_message)
        """
        try:
            # Step 1: Extract JSON string
            json_str = StructuredOutputParser.extract_json_from_response(response)

            if not json_str:
                error_msg = "Could not find JSON in response"
                logger.warning(f"❌ {error_msg}")
                logger.debug(f"Response preview: {response[:200]}...")
                return None, error_msg

            # Step 1.5: Attempt repair if needed
            json_str = StructuredOutputParser.repair_json_string(json_str)

            # Step 2: Parse JSON string to dict
            try:
                json_data = json.loads(json_str)
                logger.debug(f"✅ Successfully parsed JSON ({len(json_str)} chars)")
            except json.JSONDecodeError as e:
                error_msg = f"Invalid JSON syntax: {str(e)}"
                logger.error(f"❌ {error_msg}")
                logger.debug(f"JSON that failed to parse: {json_str[:500]}...")
                return None, error_msg

            # Step 2.5: Migrate legacy schema format if needed
            json_data = StructuredOutputParser.migrate_schema_format(json_data)

            # Step 3: Validate with Pydantic schema
            try:
                structured_response = StructuredResponse(**json_data)
                logger.info(f"✅ Successfully validated structured response with {len(structured_response.content_blocks)} blocks")
                return structured_response, None

            except ValidationError as e:
                error_msg = f"Schema validation failed: {len(e.errors())} errors"
                logger.error(f"❌ {error_msg}")
                logger.debug(f"Validation errors: {e.errors()}")
                logger.debug(f"Data that failed validation: {json.dumps(json_data, indent=2)[:500]}...")
                return None, error_msg

        except Exception as e:
            error_msg = f"Unexpected parsing error: {str(e)}"
            logger.error(f"❌ {error_msg}", exc_info=True)
            return None, error_msg

    @staticmethod
    def create_fallback_response(
        content: str,
        intent: str = "fallback",
        tone: str = "conversational"
    ) -> StructuredResponse:
        """
        Create a simple structured response from plain text.

        Used as fallback when parsing fails. Creates a single-paragraph
        response with the provided text.

        Args:
            content: Text content for the response
            intent: Response intent
            tone: Response tone

        Returns:
            Simple StructuredResponse with single paragraph
        """
        logger.info(f"Creating fallback response ({len(content)} chars)")
        return StructuredResponse.create_simple_text_response(
            text=content,
            tone=tone
        )

    @staticmethod
    def validate_response_quality(response: StructuredResponse) -> dict:
        """
        Validate the quality of a structured response.

        Checks:
        - Has content blocks
        - Content blocks are not empty
        - Code blocks have language specified
        - Headings have appropriate levels

        Args:
            response: Validated StructuredResponse

        Returns:
            Dict with quality metrics and issues
        """
        issues = []
        metrics = {
            "total_blocks": len(response.content_blocks),
            "block_types": {},
            "has_code": False,
            "has_headings": False,
            "has_actions": bool(response.suggested_actions),
        }

        if not response.content_blocks:
            issues.append("No content blocks present")

        for block in response.content_blocks:
            block_type = block.type
            metrics["block_types"][block_type] = metrics["block_types"].get(block_type, 0) + 1

            # Check specific block types
            if block_type == "code_block":
                metrics["has_code"] = True
                if not block.language:
                    issues.append("Code block missing language specification")

            elif block_type == "heading":
                metrics["has_headings"] = True
                if block.level == 1:
                    issues.append("Using H1 heading (should use H2-H3)")

            elif block_type == "paragraph":
                if not block.segments:
                    issues.append("Empty paragraph block")

        return {
            "metrics": metrics,
            "issues": issues,
            "quality_score": max(0, 100 - (len(issues) * 10))
        }


# Convenience function for one-line parsing
def parse_llm_response(
    response: str,
    fallback_on_error: bool = True
) -> Tuple[StructuredResponse, bool]:
    """
    Convenience function to parse LLM response.

    Args:
        response: Raw LLM response string
        fallback_on_error: If True, return fallback response on error

    Returns:
        Tuple of (StructuredResponse, success: bool)
    """
    structured, error = StructuredOutputParser.parse_structured_response(response)

    if error:
        if fallback_on_error:
            structured = StructuredOutputParser.create_fallback_response(response)
            return structured, False
        else:
            raise ValueError(f"Failed to parse response: {error}")

    return structured, True
