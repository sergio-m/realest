"""
MCP (Model Context Protocol) Server for Real Estate Data API.
Enables integration with n8n, Claude, and other MCP-compatible platforms.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List
from datetime import datetime
import pytz

from data_collector import data_collector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RealEstateMCPServer:
    """MCP Server implementation for Real Estate Data API."""
    
    def __init__(self):
        """Initialize the MCP server."""
        self.tools = self._define_tools()
        logger.info("Real Estate MCP Server initialized")
    
    def _define_tools(self) -> List[Dict[str, Any]]:
        """Define available tools for MCP clients."""
        return [
            {
                "name": "get_properties",
                "description": "Retrieve properties in a ZIP code with investment analysis and amenity information",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "zip_code": {
                            "type": "string",
                            "description": "ZIP code to search (e.g., '78704')"
                        },
                        "timezone": {
                            "type": "string",
                            "description": "Timezone for timestamp (e.g., 'America/Chicago')",
                            "default": "UTC"
                        },
                        "use_sample": {
                            "type": "boolean",
                            "description": "Use sample data",
                            "default": False
                        },
                        "force_refresh": {
                            "type": "boolean",
                            "description": "Force refresh from API",
                            "default": False
                        }
                    },
                    "required": ["zip_code"]
                }
            },
            {
                "name": "get_top_property",
                "description": "Get the property with highest investment score in a ZIP code",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "zip_code": {
                            "type": "string",
                            "description": "ZIP code to search"
                        },
                        "timezone": {
                            "type": "string",
                            "description": "Timezone for timestamp",
                            "default": "UTC"
                        }
                    },
                    "required": ["zip_code"]
                }
            },
            {
                "name": "filter_properties",
                "description": "Filter properties by price, bedrooms, investment score, and market duration",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "zip_code": {
                            "type": "string",
                            "description": "ZIP code to search"
                        },
                        "min_price": {
                            "type": "integer",
                            "description": "Minimum price in USD"
                        },
                        "max_price": {
                            "type": "integer",
                            "description": "Maximum price in USD"
                        },
                        "min_bedrooms": {
                            "type": "integer",
                            "description": "Minimum bedrooms"
                        },
                        "max_bedrooms": {
                            "type": "integer",
                            "description": "Maximum bedrooms"
                        },
                        "min_score": {
                            "type": "number",
                            "description": "Minimum investment score (0-100)"
                        },
                        "max_days_on_market": {
                            "type": "integer",
                            "description": "Maximum days on market"
                        },
                        "timezone": {
                            "type": "string",
                            "description": "Timezone for timestamp",
                            "default": "UTC"
                        }
                    },
                    "required": ["zip_code"]
                }
            },
            {
                "name": "get_statistics",
                "description": "Get aggregate statistics for properties in a ZIP code",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "zip_code": {
                            "type": "string",
                            "description": "ZIP code to analyze"
                        },
                        "timezone": {
                            "type": "string",
                            "description": "Timezone for timestamp",
                            "default": "UTC"
                        }
                    },
                    "required": ["zip_code"]
                }
            },
            {
                "name": "compare_zip_codes",
                "description": "Compare statistics between multiple ZIP codes",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "zip_codes": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of ZIP codes to compare"
                        },
                        "timezone": {
                            "type": "string",
                            "description": "Timezone for timestamp",
                            "default": "UTC"
                        }
                    },
                    "required": ["zip_codes"]
                }
            }
        ]
    
    def _get_timezone_timestamp(self, tz_str: str = "UTC") -> str:
        """Get current timestamp with timezone."""
        try:
            tz = pytz.timezone(tz_str)
        except pytz.exceptions.UnknownTimeZoneError:
            tz = pytz.UTC
        
        now = datetime.now(tz)
        return now.strftime("%Y-%m-%d %H:%M:%S %Z (UTC%z)")
    
    async def execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool and return results."""
        try:
            if tool_name == "get_properties":
                return await self._get_properties(tool_input)
            elif tool_name == "get_top_property":
                return await self._get_top_property(tool_input)
            elif tool_name == "filter_properties":
                return await self._filter_properties(tool_input)
            elif tool_name == "get_statistics":
                return await self._get_statistics(tool_input)
            elif tool_name == "compare_zip_codes":
                return await self._compare_zip_codes(tool_input)
            else:
                return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {str(e)}")
            return {"error": str(e)}
    
    async def _get_properties(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get properties by ZIP code."""
        zip_code = params.get("zip_code")
        if not zip_code:
            return {"error": "zip_code is required"}
        
        timezone = params.get("timezone", "UTC")
        use_sample = params.get("use_sample", False)
        force_refresh = params.get("force_refresh", False)
        
        try:
            properties = data_collector.collect_real_estate_data(
                zip_code,
                use_sample_data=use_sample,
                force_refresh=force_refresh
            )
            
            return {
                "zip_code": zip_code,
                "count": len(properties),
                "timestamp": self._get_timezone_timestamp(timezone),
                "timezone": timezone,
                "properties": properties
            }
        except Exception as e:
            return {"error": f"Failed to fetch properties: {str(e)}"}
    
    async def _get_top_property(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get top property by investment score."""
        zip_code = params.get("zip_code")
        if not zip_code:
            return {"error": "zip_code is required"}
        
        timezone = params.get("timezone", "UTC")
        
        try:
            properties = data_collector.collect_real_estate_data(zip_code)
            
            if not properties:
                return {"error": f"No properties found for ZIP code {zip_code}"}
            
            top_property = max(properties, key=lambda x: x.get("investment_score", 0))
            
            return {
                "property": top_property,
                "timestamp": self._get_timezone_timestamp(timezone),
                "timezone": timezone
            }
        except Exception as e:
            return {"error": f"Failed to get top property: {str(e)}"}
    
    async def _filter_properties(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Filter properties by criteria."""
        zip_code = params.get("zip_code")
        if not zip_code:
            return {"error": "zip_code is required"}
        
        timezone = params.get("timezone", "UTC")
        min_price = params.get("min_price")
        max_price = params.get("max_price")
        min_bedrooms = params.get("min_bedrooms")
        max_bedrooms = params.get("max_bedrooms")
        min_score = params.get("min_score")
        max_days_on_market = params.get("max_days_on_market")
        
        try:
            properties = data_collector.collect_real_estate_data(zip_code)
            
            if not properties:
                return {"error": f"No properties found for ZIP code {zip_code}"}
            
            # Apply filters
            filtered = properties
            if min_price is not None:
                filtered = [p for p in filtered if p.get("price", 0) >= min_price]
            if max_price is not None:
                filtered = [p for p in filtered if p.get("price", 0) <= max_price]
            if min_bedrooms is not None:
                filtered = [p for p in filtered if p.get("bedrooms", 0) >= min_bedrooms]
            if max_bedrooms is not None:
                filtered = [p for p in filtered if p.get("bedrooms", 0) <= max_bedrooms]
            if min_score is not None:
                filtered = [p for p in filtered if p.get("investment_score", 0) >= min_score]
            if max_days_on_market is not None:
                filtered = [p for p in filtered if p.get("days_on_market", 0) <= max_days_on_market]
            
            return {
                "zip_code": zip_code,
                "count": len(filtered),
                "timestamp": self._get_timezone_timestamp(timezone),
                "timezone": timezone,
                "properties": filtered,
                "filters_applied": {
                    "min_price": min_price,
                    "max_price": max_price,
                    "min_bedrooms": min_bedrooms,
                    "max_bedrooms": max_bedrooms,
                    "min_score": min_score,
                    "max_days_on_market": max_days_on_market
                }
            }
        except Exception as e:
            return {"error": f"Failed to filter properties: {str(e)}"}
    
    async def _get_statistics(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get statistics for a ZIP code."""
        zip_code = params.get("zip_code")
        if not zip_code:
            return {"error": "zip_code is required"}
        
        timezone = params.get("timezone", "UTC")
        
        try:
            properties = data_collector.collect_real_estate_data(zip_code)
            
            if not properties:
                return {"error": f"No properties found for ZIP code {zip_code}"}
            
            prices = [p.get("price", 0) for p in properties]
            scores = [p.get("investment_score", 0) for p in properties]
            bedrooms = [p.get("bedrooms", 0) for p in properties]
            sqfts = [p.get("square_feet", 0) for p in properties]
            
            return {
                "zip_code": zip_code,
                "total_properties": len(properties),
                "timestamp": self._get_timezone_timestamp(timezone),
                "timezone": timezone,
                "price": {
                    "average": round(sum(prices) / len(prices), 2) if prices else 0,
                    "min": min(prices) if prices else 0,
                    "max": max(prices) if prices else 0,
                },
                "investment_score": {
                    "average": round(sum(scores) / len(scores), 2) if scores else 0,
                    "min": min(scores) if scores else 0,
                    "max": max(scores) if scores else 0,
                },
                "bedrooms": {
                    "average": round(sum(bedrooms) / len(bedrooms), 2) if bedrooms else 0,
                    "min": min(bedrooms) if bedrooms else 0,
                    "max": max(bedrooms) if bedrooms else 0,
                },
                "square_feet": {
                    "average": round(sum(sqfts) / len(sqfts), 2) if sqfts else 0,
                    "min": min(sqfts) if sqfts else 0,
                    "max": max(sqfts) if sqfts else 0,
                }
            }
        except Exception as e:
            return {"error": f"Failed to get statistics: {str(e)}"}
    
    async def _compare_zip_codes(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Compare statistics between multiple ZIP codes."""
        zip_codes = params.get("zip_codes", [])
        if not zip_codes:
            return {"error": "zip_codes list is required"}
        
        timezone = params.get("timezone", "UTC")
        
        try:
            comparison = {
                "timestamp": self._get_timezone_timestamp(timezone),
                "timezone": timezone,
                "zip_codes": []
            }
            
            for zip_code in zip_codes:
                properties = data_collector.collect_real_estate_data(zip_code)
                
                if not properties:
                    comparison["zip_codes"].append({
                        "zip_code": zip_code,
                        "error": "No properties found"
                    })
                    continue
                
                prices = [p.get("price", 0) for p in properties]
                scores = [p.get("investment_score", 0) for p in properties]
                
                comparison["zip_codes"].append({
                    "zip_code": zip_code,
                    "total_properties": len(properties),
                    "avg_price": round(sum(prices) / len(prices), 2) if prices else 0,
                    "price_range": f"${min(prices)} - ${max(prices)}",
                    "avg_investment_score": round(sum(scores) / len(scores), 2) if scores else 0,
                })
            
            return comparison
        except Exception as e:
            return {"error": f"Failed to compare ZIP codes: {str(e)}"}
    
    def get_tools_list(self) -> List[Dict[str, Any]]:
        """Return list of available tools."""
        return self.tools


# Global server instance
mcp_server = RealEstateMCPServer()


# JSON-RPC Server Implementation for MCP Protocol
class MCPJsonRPCServer:
    """JSON-RPC server implementing MCP protocol."""
    
    def __init__(self, server: RealEstateMCPServer):
        self.server = server
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a JSON-RPC request."""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        try:
            if method == "list_tools":
                result = {"tools": self.server.get_tools_list()}
            elif method == "call_tool":
                tool_name = params.get("name")
                tool_input = params.get("arguments", {})
                result = await self.server.execute_tool(tool_name, tool_input)
            else:
                return {
                    "jsonrpc": "2.0",
                    "error": {"code": -32601, "message": "Method not found"},
                    "id": request_id
                }
            
            return {
                "jsonrpc": "2.0",
                "result": result,
                "id": request_id
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32603, "message": str(e)},
                "id": request_id
            }


async def main():
    """Main entry point for MCP server."""
    server = MCPJsonRPCServer(mcp_server)
    
    print("Real Estate MCP Server Started")
    print("Available tools:")
    for tool in mcp_server.get_tools_list():
        print(f"  - {tool['name']}: {tool['description']}")
    
    # Example usage
    test_request = {
        "jsonrpc": "2.0",
        "method": "call_tool",
        "params": {
            "name": "get_statistics",
            "arguments": {
                "zip_code": "78704",
                "timezone": "America/Chicago"
            }
        },
        "id": 1
    }
    
    result = await server.handle_request(test_request)
    print("\nExample call result:")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
