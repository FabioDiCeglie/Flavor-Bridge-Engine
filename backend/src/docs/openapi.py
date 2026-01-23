"""
OpenAPI 3.0 specification for Flavor Bridge Engine.
"""

OPENAPI_SPEC = {
    "openapi": "3.0.3",
    "info": {
        "title": "Flavor Bridge Engine",
        "description": """
A discovery engine that finds "chemical cousins" between ingredients using AI embeddings and vector similarity search.

## How it works

1. **Embeddings**: Each ingredient description is converted to a 384-dimensional vector using Workers AI
2. **Similarity**: When you search, your query is embedded and compared against all ingredients using cosine similarity
3. **Reasoning**: The AI explains WHY ingredients are "chemical cousins" based on shared flavor compounds

## The Science

Ingredients that share flavor compounds (glutamates, Maillard products, fermentation byproducts) 
will have similar embeddings, even if they seem unrelated. This is why Miso and Parmesan are 
"chemical cousins" - both are fermented and high in glutamic acid.
        """,
        "version": "1.0.0",
    },
    "tags": [
        {"name": "Search", "description": "Find chemical cousins"},
        {"name": "Explain", "description": "AI-powered flavor reasoning"},
        {"name": "Admin", "description": "Database operations"},
        {"name": "Health", "description": "Service health"}
    ],
    "paths": {
        "/health": {
            "get": {
                "tags": ["Health"],
                "summary": "Health check",
                "description": "Returns 204 if service is healthy",
                "operationId": "healthCheck",
                "responses": {
                    "204": {"description": "Service is healthy"}
                }
            }
        },
        "/search": {
            "get": {
                "tags": ["Search"],
                "summary": "Find chemical cousins",
                "description": "Search for ingredients with similar flavor profiles using vector similarity",
                "operationId": "searchIngredients",
                "parameters": [
                    {
                        "name": "q",
                        "in": "query",
                        "required": True,
                        "description": "Ingredient or flavor to search for",
                        "schema": {"type": "string"},
                        "examples": {
                            "miso": {"value": "Miso"},
                            "chocolate": {"value": "Dark Chocolate"},
                            "umami": {"value": "umami fermented"}
                        }
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Similar ingredients found",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/SearchResponse"},
                                "example": {
                                    "query": "Miso",
                                    "matches": [
                                        {
                                            "id": "2",
                                            "score": 0.89,
                                            "name": "Parmesan",
                                            "description": "Aged Italian cheese rich in glutamates..."
                                        }
                                    ]
                                }
                            }
                        }
                    },
                    "400": {
                        "description": "Missing query parameter",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Error"}
                            }
                        }
                    }
                }
            }
        },
        "/explain": {
            "post": {
                "tags": ["Explain"],
                "summary": "Explain flavor connections",
                "description": "Use AI to explain why ingredients are 'chemical cousins'",
                "operationId": "explainConnections",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/ExplainRequest"},
                            "example": {
                                "query": "Miso",
                                "matches": [
                                    {"name": "Parmesan", "description": "Aged cheese with glutamates"},
                                    {"name": "Soy Sauce", "description": "Fermented soybean condiment"}
                                ]
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "AI explanation generated",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ExplainResponse"},
                                "example": {
                                    "query": "Miso",
                                    "explanation": "Miso and Parmesan are chemical cousins because both are fermented foods rich in glutamic acid..."
                                }
                            }
                        }
                    },
                    "400": {
                        "description": "Missing query or matches",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Error"}
                            }
                        }
                    }
                }
            }
        },
        "/seed": {
            "post": {
                "tags": ["Admin"],
                "summary": "Seed the database",
                "description": "Populate Vectorize with ingredient embeddings. Safe to run multiple times (upsert).",
                "operationId": "seedDatabase",
                "responses": {
                    "200": {
                        "description": "Database seeded successfully",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/SeedResponse"},
                                "example": {
                                    "success": True,
                                    "message": "Seeded 200 ingredients"
                                }
                            }
                        }
                    }
                }
            }
        }
    },
    "components": {
        "schemas": {
            "SearchResponse": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query"},
                    "matches": {
                        "type": "array",
                        "items": {"$ref": "#/components/schemas/Match"}
                    }
                }
            },
            "Match": {
                "type": "object",
                "properties": {
                    "id": {"type": "string", "description": "Ingredient ID"},
                    "score": {"type": "number", "description": "Similarity score (0-1, higher is more similar)"},
                    "name": {"type": "string", "description": "Ingredient name"},
                    "description": {"type": "string", "description": "Flavor profile description"}
                }
            },
            "ExplainRequest": {
                "type": "object",
                "required": ["query", "matches"],
                "properties": {
                    "query": {"type": "string", "description": "The ingredient being searched"},
                    "matches": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "description": {"type": "string"}
                            }
                        },
                        "description": "Similar ingredients to explain"
                    }
                }
            },
            "ExplainResponse": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "explanation": {"type": "string", "description": "AI-generated explanation of flavor connections"}
                }
            },
            "SeedResponse": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "message": {"type": "string"}
                }
            },
            "Error": {
                "type": "object",
                "properties": {
                    "error": {"type": "string", "description": "Error message"}
                }
            }
        }
    }
}

