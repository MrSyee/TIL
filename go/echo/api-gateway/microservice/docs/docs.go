// Package docs GENERATED BY SWAG; DO NOT EDIT
// This file was generated by swaggo/swag
package docs

import "github.com/swaggo/swag"

const docTemplate = `{
    "schemes": {{ marshal .Schemes }},
    "swagger": "2.0",
    "info": {
        "description": "{{escape .Description}}",
        "title": "{{.Title}}",
        "contact": {
            "name": "Kyunghwan Kim",
            "email": "khsyee@gmail.com"
        },
        "version": "{{.Version}}"
    },
    "host": "{{.Host}}",
    "basePath": "{{.BasePath}}",
    "paths": {
        "/": {
            "get": {
                "description": "It returns true if the api server is alive.",
                "consumes": [
                    "application/json"
                ],
                "produces": [
                    "application/json"
                ],
                "summary": "Healthcheck",
                "responses": {
                    "200": {
                        "description": "API server's liveness",
                        "schema": {
                            "type": "boolean"
                        }
                    }
                }
            }
        },
        "/file": {
            "post": {
                "description": "Receive file",
                "consumes": [
                    "application/json"
                ],
                "produces": [
                    "application/json"
                ],
                "summary": "Receive file",
                "parameters": [
                    {
                        "type": "string",
                        "description": "filename",
                        "name": "filename",
                        "in": "query",
                        "required": true
                    },
                    {
                        "type": "file",
                        "description": "file",
                        "name": "file",
                        "in": "formData",
                        "required": true
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Success",
                        "schema": {
                            "type": "boolean"
                        }
                    }
                }
            }
        },
        "/sum": {
            "post": {
                "description": "It outputs sum of two inputs",
                "consumes": [
                    "application/x-www-form-urlencoded"
                ],
                "produces": [
                    "application/json"
                ],
                "summary": "Sum integer inputs",
                "parameters": [
                    {
                        "type": "integer",
                        "description": "inputX",
                        "name": "inputX",
                        "in": "formData",
                        "required": true
                    },
                    {
                        "type": "integer",
                        "description": "inputY",
                        "name": "inputY",
                        "in": "formData",
                        "required": true
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Integer response: int",
                        "schema": {
                            "type": "integer"
                        }
                    }
                }
            }
        }
    }
}`

// SwaggerInfo holds exported Swagger Info so clients can modify it
var SwaggerInfo = &swag.Spec{
	Version:          "",
	Host:             "",
	BasePath:         "",
	Schemes:          []string{},
	Title:            "",
	Description:      "",
	InfoInstanceName: "swagger",
	SwaggerTemplate:  docTemplate,
}

func init() {
	swag.Register(SwaggerInfo.InstanceName(), SwaggerInfo)
}
