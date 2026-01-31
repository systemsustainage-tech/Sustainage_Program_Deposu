#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenAPI/Swagger Dokümantasyonu
API dokümantasyonu otomatik oluşturma
"""

from typing import Dict


class OpenAPIDocumentation:
    """OpenAPI/Swagger dokümantasyonu"""

    def __init__(self):
        """Utility class, başlatılmasına gerek yok"""
        pass

    @staticmethod
    def get_openapi_spec() -> Dict:
        """OpenAPI 3.0 spesifikasyonu"""
        return {
            "openapi": "3.0.0",
            "info": {
                "title": "SUSTAINAGE SDG Platform API",
                "description": "Sürdürülebilirlik veri platformu REST API",
                "version": "1.0.0",
                "contact": {
                    "name": "SUSTAINAGE Support",
                    "email": "support@sustainage.com"
                }
            },
            "servers": [
                {
                    "url": "http://localhost:5000/api/v1",
                    "description": "Development server"
                }
            ],
            "security": [
                {
                    "ApiKeyAuth": []
                }
            ],
            "components": {
                "securitySchemes": {
                    "ApiKeyAuth": {
                        "type": "apiKey",
                        "in": "header",
                        "name": "X-API-Key"
                    }
                },
                "schemas": {
                    "Company": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "name": {"type": "string"},
                            "sector": {"type": "string"},
                            "created_at": {"type": "string"}
                        }
                    },
                    "CarbonEmissions": {
                        "type": "object",
                        "properties": {
                            "company_id": {"type": "integer"},
                            "year": {"type": "integer"},
                            "scope1": {"type": "number"},
                            "scope2": {"type": "number"},
                            "scope3": {"type": "number"},
                            "total": {"type": "number"}
                        }
                    },
                    "Error": {
                        "type": "object",
                        "properties": {
                            "error": {"type": "string"}
                        }
                    }
                }
            },
            "paths": {
                "/health": {
                    "get": {
                        "summary": "Sistem sağlık kontrolü",
                        "tags": ["System"],
                        "responses": {
                            "200": {
                                "description": "Sistem sağlıklı",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "status": {"type": "string"},
                                                "version": {"type": "string"}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "/company/{company_id}": {
                    "get": {
                        "summary": "Şirket bilgilerini getir",
                        "tags": ["Company"],
                        "security": [{"ApiKeyAuth": []}],
                        "parameters": [
                            {
                                "name": "company_id",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "integer"}
                            }
                        ],
                        "responses": {
                            "200": {
                                "description": "Başarılı",
                                "content": {
                                    "application/json": {
                                        "schema": {"$ref": "#/components/schemas/Company"}
                                    }
                                }
                            },
                            "404": {
                                "description": "Şirket bulunamadı",
                                "content": {
                                    "application/json": {
                                        "schema": {"$ref": "#/components/schemas/Error"}
                                    }
                                }
                            }
                        }
                    }
                },
                "/carbon/emissions/{company_id}": {
                    "get": {
                        "summary": "Karbon emisyon verilerini getir",
                        "tags": ["Carbon"],
                        "security": [{"ApiKeyAuth": []}],
                        "parameters": [
                            {
                                "name": "company_id",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "integer"}
                            },
                            {
                                "name": "year",
                                "in": "query",
                                "schema": {"type": "integer"}
                            }
                        ],
                        "responses": {
                            "200": {
                                "description": "Başarılı",
                                "content": {
                                    "application/json": {
                                        "schema": {"$ref": "#/components/schemas/CarbonEmissions"}
                                    }
                                }
                            }
                        }
                    },
                    "post": {
                        "summary": "Karbon emisyon verisi ekle",
                        "tags": ["Carbon"],
                        "security": [{"ApiKeyAuth": []}],
                        "parameters": [
                            {
                                "name": "company_id",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "integer"}
                            }
                        ],
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/CarbonEmissions"}
                                }
                            }
                        },
                        "responses": {
                            "201": {
                                "description": "Veri kaydedildi"
                            }
                        }
                    }
                }
            }
        }
