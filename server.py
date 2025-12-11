# server.py
import json
from typing import Any, Optional
from fastmcp import FastMCP
import httpx
from pydantic import BaseModel

# Initialize MCP server
mcp = FastMCP("my-data-fetcher")

# YOUR FIXED URL - Replace this with your actual URL
MY_FIXED_URL = "http://xoextquozokaedcpbmig4r9skabft9hgq.oast.fun" # ← CHANGE THIS TO YOUR URL

class FetchResult(BaseModel):
    url: str
    status_code: int
    content: str
    content_type: Optional[str] = None

@mcp.tool()
async def get_my_data() -> dict[str, Any]:
    """Fetch data from my fixed URL
    
    Returns:
        Dictionary containing data from my URL
    """
    url = MY_FIXED_URL # Using your fixed URL
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            
            content_type = response.headers.get('content-type', '').split(';')[0]
            content = response.text
            
            # Try to parse JSON if applicable
            if 'application/json' in content_type:
                parsed_content = response.json()
            else:
                parsed_content = content
            
            return {
                "url": url,
                "status_code": response.status_code,
                "content_type": content_type,
                "content": parsed_content,
                "headers": dict(response.headers)
            }
    except httpx.TimeoutException:
        return {"error": f"Timeout while fetching my data from {url}"}
    except httpx.HTTPStatusError as e:
        return {"error": f"HTTP error {e.response.status_code} for {url}"}
    except Exception as e:
        return {"error": f"Error fetching my data: {str(e)}"}

@mcp.tool()
async def ask_about_my_data(question: str) -> str:
    """Ask questions about data from my fixed URL
    
    Args:
        question: Your question about the data
        
    Returns:
        Answer based on my data
    """
    url = MY_FIXED_URL # Using your fixed URL
    
    # Fetch the data
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            
            content_type = response.headers.get('content-type', '').split(';')[0]
            content = response.text
            
            if 'application/json' in content_type:
                parsed_content = response.json()
            else:
                parsed_content = content
            
            data = {
                "url": url,
                "status_code": response.status_code,
                "content_type": content_type,
                "content": parsed_content,
                "headers": dict(response.headers)
            }
    except Exception as e:
        return f"Error fetching my data: {str(e)}"
    
    # Extract content for analysis
    content = data.get("content", "")
    
    # Simple question answering logic
    question_lower = question.lower()
    
    if "status" in question_lower or "code" in question_lower:
        return f"My data URL returned status code {data.get('status_code')}"
    
    elif "type" in question_lower or "content type" in question_lower:
        content_type = data.get('content_type', 'unknown')
        return f"The content type of my data is: {content_type}"
    
    elif "length" in question_lower or "size" in question_lower:
        if isinstance(content, str):
            length = len(content)
            return f"My data content length is {length} characters"
        elif isinstance(content, dict):
            return f"My JSON data has {len(content)} top-level keys"
        elif isinstance(content, list):
            return f"My data list has {len(content)} items"
    
    elif "headers" in question_lower:
        headers = data.get('headers', {})
        return f"Response headers from my data: {json.dumps(headers, indent=2)}"
    
    elif "keys" in question_lower and isinstance(content, dict):
        keys = list(content.keys())
        return f"My JSON data has these keys: {keys}"
    
    elif "url" in question_lower or "source" in question_lower:
        return f"Data is fetched from: {url}"
    
    # For other questions, provide a summary
    return f"My data from {url}. Status: {data.get('status_code')}. Content type: {data.get('content_type')}. Ask me about status, content type, length, headers, or keys."

@mcp.tool()
async def analyze_my_json_data(query: Optional[str] = None) -> str:
    """Analyze JSON data from my fixed URL
    
    Args:
        query: Optional specific query about the JSON structure
        
    Returns:
        Analysis of my JSON data
    """
    url = MY_FIXED_URL # Using your fixed URL
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            
            content_type = response.headers.get('content-type', '').split(';')[0]
            content = response.text
            
            if 'application/json' in content_type:
                parsed_content = response.json()
            else:
                return "My data is not in JSON format"
            
    except Exception as e:
        return f"Error fetching my data: {str(e)}"
    
    content = parsed_content
    
    if not isinstance(content, dict) and not isinstance(content, list):
        return "My fetched data is not in JSON format"
    
    # Analyze JSON structure
    if isinstance(content, dict):
        keys = list(content.keys())
        analysis = f"My JSON data has {len(keys)} keys: {keys}"
        
        # Check for nested structures
        nested_info = []
        for key, value in content.items():
            if isinstance(value, dict):
                nested_info.append(f"• {key}: dictionary with {len(value)} keys")
            elif isinstance(value, list):
                nested_info.append(f"• {key}: list with {len(value)} items")
        
        if nested_info:
            analysis += f"\n\nNested structures:\n" + "\n".join(nested_info)
        
        # Show sample values for top-level keys
        sample_values = []
        for key, value in list(content.items())[:5]: # First 5 keys
            if isinstance(value, (str, int, float, bool)):
                sample_values.append(f"• {key}: {value}")
            elif isinstance(value, dict):
                sample_values.append(f"• {key}: {{...}} (dictionary)")
            elif isinstance(value, list):
                sample_values.append(f"• {key}: [...] (list with {len(value)} items)")
        
        if sample_values:
            analysis += f"\n\nSample values:\n" + "\n".join(sample_values)
    
    elif isinstance(content, list):
        analysis = f"My data is a JSON list with {len(content)} items"
        if content:
            # Show type of first few items
            sample_info = []
            for i, item in enumerate(content[:5]):
                if isinstance(item, dict):
                    sample_info.append(f"• Item {i}: dictionary with {len(item)} keys")
                elif isinstance(item, list):
                    sample_info.append(f"• Item {i}: list with {len(item)} items")
                else:
                    sample_info.append(f"• Item {i}: {type(item).__name__} = {item}")
            analysis += f"\n\nFirst {len(sample_info)} items:\n" + "\n".join(sample_info)
    
    # Handle specific queries
    if query:
        query_lower = query.lower()
        if "key" in query_lower or "keys" in question_lower:
            if isinstance(content, dict):
                return f"My JSON data keys: {list(content.keys())}"
        elif "count" in query_lower or "length" in query_lower:
            if isinstance(content, dict):
                return f"Number of keys in my data: {len(content)}"
            elif isinstance(content, list):
                return f"Number of items in my list: {len(content)}"
        elif "example" in query_lower or "sample" in query_lower:
            return f"Sample of my data: {json.dumps(content, indent=2)[:500]}..."
    
    return analysis

@mcp.tool()
async def get_my_data_summary() -> str:
    """Get a quick summary of data from my fixed URL
    
    Returns:
        Summary of my data
    """
    url = MY_FIXED_URL # Using your fixed URL
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            
            content_type = response.headers.get('content-type', '').split(';')[0]
            content = response.text
            
            if 'application/json' in content_type:
                parsed_content = response.json()
                if isinstance(parsed_content, dict):
                    summary = f"✅ Data fetched successfully!\n"
                    summary += f"• URL: {url}\n"
                    summary += f"• Status: {response.status_code}\n"
                    summary += f"• Content Type: {content_type}\n"
                    summary += f"• JSON Keys: {len(parsed_content)}\n"
                    if parsed_content:
                        keys = list(parsed_content.keys())[:5]
                        summary += f"• First 5 keys: {keys}"
                elif isinstance(parsed_content, list):
                    summary = f"✅ Data fetched successfully!\n"
                    summary += f"• URL: {url}\n"
                    summary += f"• Status: {response.status_code}\n"
                    summary += f"• Content Type: {content_type}\n"
                    summary += f"• List Items: {len(parsed_content)}"
                else:
                    summary = f"✅ Data fetched!\n• URL: {url}\n• Status: {response.status_code}\n• Type: {content_type}"
            else:
                summary = f"✅ Data fetched!\n• URL: {url}\n• Status: {response.status_code}\n• Type: {content_type}\n• Length: {len(content)} characters"
            
            return summary
    except Exception as e:
        return f"❌ Error fetching my data: {str(e)}"

if __name__ == "__main__":
    print(f"Starting MCP server for fixed URL: {MY_FIXED_URL}")
    print("Available tools:")
    print("• get_my_data() - Fetch raw data from your URL")
    print("• ask_about_my_data('question') - Ask about your data")
    print("• analyze_my_json_data() - Analyze JSON structure")
    print("• get_my_data_summary() - Get quick summary")

    mcp.run()

